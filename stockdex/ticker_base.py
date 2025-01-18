"""
Base class for ticker objects to inherit from
"""

import time
from logging import getLogger
from typing import Union

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup

from stockdex.config import RESPONSE_TIMEOUT
from stockdex.lib import get_user_agent
from stockdex.exceptions import NoDataError

class TickerBase:
    request_headers = {
        "User-Agent": get_user_agent(),
    }
    logger = getLogger(__name__)
    _cached_responses: dict[str, requests.Response]  = {}

    def get_response(self, url: str, n_retries: int=5) -> requests.Response:
        """
        Send an HTTP GET request to the website

        Args:
        ----------
        url: str
            The URL to send the HTTP GET request to
        n_retries: int
            Max number of retries allowed w/ rate limit warnings. Default is 5

        Returns:
        ----------
        requests.Response
            The response from the website
        """
        if url in self._cached_responses.keys():
            return self._cached_responses[url]

        # Send an HTTP GET request to the website
        session = requests.Session()
        adapter = HTTPAdapter()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(
            url, headers=self.request_headers, timeout=RESPONSE_TIMEOUT
        )
        # If the HTTP GET request can't be served
        if response.status_code != 200 and response.status_code != 429:
            raise NoDataError(
                f"""
                Failed to load page (status code: {response.status_code}).
                Check if the ticker symbol exists
                """
            )

        # sleep if rate limit is reached and retry after time is given
        # content search is due to macrotrends's way of telling you to wait
        elif response.status_code == 429 or "<title>Just a moment...</title>" in str(response.content):
            # retry n_retries times with 10 seconds intervals and after that raise an exception.
            # since we also use retry in the session, make this one long
            retry_after = 10
            self.logger.warning(
                f"Rate limit reached. Retrying {n_retries-1} more times after {retry_after} seconds"
            )
            if(n_retries > 1):
                time.sleep(retry_after)
                return self.get_response(url, n_retries-1)

        self._cached_responses.update({str(response.url): response})

        return response

    def find_parent_by_text(
        self,
        soup: BeautifulSoup,
        tag: str,
        text: str,
        condition: dict = {},
        skip: int = 0,
    ) -> Union[None, str]:
        """
        Method that finds the parent of a tag by its text from a BeautifulSoup object

        Args:
        ----------
        soup: BeautifulSoup
            The BeautifulSoup object to search
        tag: str
            The tag to search for
        text: str
            The text to search for
        condition: dict
            The condition to search for
        skip: int
            The number of elements to skip before returning the parent

        Returns:
        ----------
        Union[None, str]: The parent of the tag if it exists, None otherwise
        """
        for element in soup.find_all(tag, condition):
            if text in element.get_text():
                for _ in range(skip):
                    element = element.find_next(tag)
                return element
        return None
