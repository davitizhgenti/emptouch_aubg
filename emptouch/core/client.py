# core/client.py
from typing import Type
from .endpoints import Endpoint
from .network import HttpClient
from .parsers import BaseParser


class EmpowerClient:
    """
    A high-level client that orchestrates the network and parsing layers.
    It delegates session management to the underlying HttpClient.
    """

    def __init__(self, username, password):
        """
        Initializes the client.
        
        Args:
            username (str): The SIS username.
            password (str): The SIS password.
        """
        self._http_client = HttpClient(username, password)

    def get(self, endpoint: Endpoint, parser_class: Type[BaseParser]):
        """
        Performs a GET request for a page, processes it with the specified parser,
        and returns the data.

        Args:
            endpoint (Endpoint): The endpoint configuration object defining the target page.
            parser_class (Type[BaseParser]): The concrete parser class used to process the page.

        Returns:
            The structured data returned by the parser's .parse() method.
        """
        soup = self._http_client.get(endpoint)
        parser = parser_class(soup)
        return parser.parse()

    def post(self, endpoint: Endpoint, payload: dict, parser_class: Type[BaseParser]):
        """
        Sends a POST request with a payload to a fuseaction.
        """
        soup = self._http_client.post(endpoint, payload)
        parser = parser_class(soup)
        return parser.parse()

    def ajax_post(self, initial_endpoint: Endpoint, token_name: str, cfc_url: str, method: str, payload: dict, parser_class: Type[BaseParser]):
        """
        Performs a two-step AJAX POST request by first visiting a page to get a dynamic token.
        """
        print(f"DEBUG: Visiting initial page '{initial_endpoint.fuseaction}' to find token '{token_name}'...")
        host_page_soup = self._http_client.get(initial_endpoint)
        
        token_input = host_page_soup.find('input', {'name': token_name})
        
        if not token_input or not token_input.get('value'):
            raise Exception(f"Could not find a valid token named '{token_name}' on the initial page.")
            
        dynamic_token = token_input['value']
        print(f"DEBUG: Found dynamic token: {dynamic_token}")

        payload[token_name] = dynamic_token

        print(f"DEBUG: Making AJAX POST to {cfc_url} with method {method}")
        ajax_soup = self._http_client.ajax_post(cfc_url, method, payload)
        
        parser = parser_class(ajax_soup)
        return parser.parse()

    def __enter__(self):
        """
        Enters the context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context manager, ensuring the session is closed.
        """
        self._http_client.close()