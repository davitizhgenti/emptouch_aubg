# core/parsers.py
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseParser(ABC):
    """
    Abstract base class for all page parsers.

    Each concrete parser must implement the `parse` method, which takes a
    BeautifulSoup object and returns structured data.
    """

    def __init__(self, soup: BeautifulSoup):
        """
        Initializes the parser with the HTML content to be parsed.
        """
        self.soup = soup

    @abstractmethod
    def parse(self):
        """
        Parses the BeautifulSoup object to extract structured data.
        This method MUST be implemented by all subclasses.
        """
        raise NotImplementedError("Subclasses must implement the parse() method.")