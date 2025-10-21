# core/exceptions.py

class EmpowerError(Exception):
    """Base exception class for all framework-related errors."""
    pass

class AuthenticationError(EmpowerError):
    """Raised when authentication with the SIS fails."""
    pass

class NavigationError(EmpowerError):
    """
    Raised when an HTTP request fails or when the client lands on an
    unexpected page.
    """
    pass

class SessionExpiredError(NavigationError):
    """
    A specific type of NavigationError raised when the client is redirected
    to the login page, indicating the session has expired.
    """
    pass

class PageParsingError(EmpowerError):
    """
    Raised within a parser class when the page's HTML structure
    is not as expected and cannot be parsed.
    """
    pass