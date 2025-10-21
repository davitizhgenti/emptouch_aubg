# core/network.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .exceptions import AuthenticationError, NavigationError, SessionExpiredError


class HttpClient:
    """
    A stateful session manager that detects session expiry by looking for
    the login form fields in the HTML response.
    """
    def __init__(self, username, password,
                 navigation_url='https://aubg.empower-xl.com/empower/fusebox.cfm',
                 auth_url='https://aubg.empower-xl.com/ptl-includes/authentication/auth-onlogin.cfm'):
        
        self.navigation_url = navigation_url
        self.auth_url = auth_url
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._username = username
        self._password = password
        self._is_logged_in = False

    def _is_login_page(self, soup: BeautifulSoup) -> bool:
        """
        The definitive check: a page is considered a "failed login state" if
        it is EITHER the main login page OR the specific "Authentication Failure" page.
        """
        # --- Check 1: Is it the original login form? ---
        # This is the check we had before, and it's still valid for session timeouts.
        username_field = soup.find('input', {'name': 'empower_usrn'})
        password_field = soup.find('input', {'name': 'empower_pswd'})
        if username_field is not None and password_field is not None:
            print("DEBUG [_is_login_page]: Found login form input fields. Result: True.")
            return True

        # --- Check 2: Is it the "Authentication Failure" page? ---
        # Based on the new HTML, this is a unique fingerprint of that page.
        page_alert = soup.find('p', {'class': 'page-alert'})
        if page_alert and 'Authentication Failed' in page_alert.get_text():
            print("DEBUG [_is_login_page]: Found 'Authentication Failed' alert. Result: True.")
            return True
            
        # --- If neither of the above are true, it's a successful login page ---
        print("DEBUG [_is_login_page]: Did not find any failure indicators. Result: False.")
        return False

    def _login(self):
        """
        Internal login method. Verifies success by checking that the response is NOT the login page.
        """
        print("INFO: Authenticating with Empower SIS...")
        logon_info = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        login_payload = {
            'empower_usrn': self._username, 'empower_pswd': self._password, 'LoggedInToEmpower': '1',
            'logoninfo': logon_info, 'LogInToEmpower.x': '57', 'LogInToEmpower.y': '18',
        }
        try:
            response = self._session.post(self.auth_url, data=login_payload)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            if self._is_login_page(soup):
                # If we are still on the login page, the login FAILED.
                print("DEBUG: Login failed, credentials rejected by SIS.")
                return False
            
            # If we are NOT on the login page, the login SUCCEEDED.
            print("INFO: Authentication successful.")
            self._is_logged_in = True
            return True

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"An HTTP error occurred during authentication: {e}")

    def get(self, endpoint) -> BeautifulSoup:
        if not self._is_logged_in: self._login()
        try:
            return self._perform_get(endpoint)
        except SessionExpiredError:
            self._is_logged_in = False
            self._login()
            return self._perform_get(endpoint)

    def _perform_get(self, endpoint) -> BeautifulSoup:
        response = self._session.get(self.navigation_url, params={'fuseaction': endpoint.fuseaction})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        if self._is_login_page(soup):
            raise SessionExpiredError(f"Session expired when requesting '{endpoint.fuseaction}'.")
        return soup

    def post(self, endpoint, payload: dict) -> BeautifulSoup:
        """
        Performs a POST request with automatic session management.
        """
        if not self._is_logged_in:
            self._login()

        try:
            # We use _perform_post, similar to how get uses _perform_get
            return self._perform_post(endpoint, payload)
        except SessionExpiredError:
            # If we get kicked out, re-login and retry once.
            print("WARNING: Detected redirection to login page during POST. Re-authenticating.")
            self._is_logged_in = False
            self._login()
            
            print("INFO: Retrying original POST request...")
            return self._perform_post(endpoint, payload)

    def _perform_post(self, endpoint, payload: dict) -> BeautifulSoup:
        """The core logic for performing a single POST request."""
        try:
            response = self._session.post(self.navigation_url, params={'fuseaction': endpoint.fuseaction}, data=payload)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            if self._is_login_page(soup):
                raise SessionExpiredError(f"Session expired when POSTing to '{endpoint.fuseaction}'.")
            
            return soup
        except requests.exceptions.RequestException as e:
            raise NavigationError(f"HTTP POST request failed for endpoint '{endpoint.fuseaction}': {e}")

    def ajax_post(self, cfc_url: str, method: str, payload: dict) -> BeautifulSoup:
        """
        Performs a specialized AJAX POST request to a .cfc endpoint.
        """
        if not self._is_logged_in:
            self._login()

        # --- Set the specific headers required for an AJAX request ---
        ajax_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.navigation_url, # Use the main app URL as the referer
            'Origin': 'https://aubg.empower-xl.com',
            'Accept': 'application/json, text/javascript, */*'
        }
        
        # Combine with existing session headers
        original_headers = self._session.headers.copy()
        self._session.headers.update(ajax_headers)

        try:
            # Construct the full URL with the method parameter
            full_url = f"{cfc_url}?method={method}"
            
            response = self._session.post(full_url, data=payload)
            response.raise_for_status()
            
            # Since the response is just HTML, we can parse it directly
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.RequestException as e:
            raise NavigationError(f"AJAX POST request failed for URL '{full_url}': {e}")
        finally:
            # --- IMPORTANT: Restore the original headers ---
            # This prevents these special headers from interfering with normal navigation.
            self._session.headers = original_headers
            
    def close(self):
        logout_params = {'fuseaction': 'Logout'}
        try: self._session.get(self.navigation_url, params=logout_params)
        except requests.exceptions.RequestException: pass
        finally: self._session.close()