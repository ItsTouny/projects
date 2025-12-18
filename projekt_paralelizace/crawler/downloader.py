import random
import time
from typing import Optional, Tuple
import tls_client
from urllib.parse import urlparse


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]


class Downloader:
    """
    Universal downloader for extracting HTML content from various e-commerce sites (Alza, Datart, CZC, etc.).

    This class handles TLS fingerprinting, session management, cookie warm-up, and header randomization
    to mimic a real browser and bypass basic anti-bot protections.
    """

    def __init__(self, timeout: int = 15):
        """
        Initializes the Downloader with a specific timeout.

        Args:
            timeout (int): The timeout for HTTP requests in seconds. Defaults to 15.
        """
        self.timeout = timeout
        self.client_identifier = "chrome_124"
        self.session = self._create_session()
        self.cookies_warmed_up = set()

    def _create_session(self) -> tls_client.Session:
        session = tls_client.Session(
            client_identifier=self.client_identifier,
            random_tls_extension_order=True
        )
        return session

    def _get_headers(self, url: str) -> dict:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        headers = {}
        headers["authority"] = domain
        headers["accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        )
        headers["accept-language"] = "cs-CZ,cs;q=0.9,en;q=0.8"
        headers["cache-control"] = "no-cache"
        headers["pragma"] = "no-cache"
        headers["sec-ch-ua"] = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = '"Windows"'
        headers["sec-fetch-dest"] = "document"
        headers["sec-fetch-mode"] = "navigate"
        headers["sec-fetch-site"] = "none"
        headers["sec-fetch-user"] = "?1"
        headers["upgrade-insecure-requests"] = "1"
        headers["user-agent"] = random.choice(USER_AGENTS)

        if "datart" in domain:
            headers["referer"] = "https://www.seznam.cz/"

        if "czc" in domain:
            headers["referer"] = "https://www.google.com/"

        if domain in self.cookies_warmed_up:
            headers["sec-fetch-site"] = "same-origin"
            headers["referer"] = f"https://{domain}/"

        return headers

    def _warm_up(self, url: str) -> None:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        if domain in self.cookies_warmed_up:
            return

        try:
            home_url = f"https://{domain}/"
            headers = self._get_headers(home_url)

            self.session.get(
                home_url,
                headers=headers,
                timeout_seconds=10
            )

            self.cookies_warmed_up.add(domain)
            time.sleep(random.uniform(1.0, 2.5))

        except Exception:
            return

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches the HTML content of the given URL.

        This method performs a 'warm-up' request to the domain's homepage to establish cookies
        before requesting the specific URL. It handles HTTP errors and basic captcha detection.

        Args:
            url (str): The target URL to download.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing:
                - The HTML content (str) if successful, otherwise None.
                - An error message (str) if failed, otherwise None.
        """
        try:
            self._warm_up(url)

            headers = self._get_headers(url)

            response = self.session.get(
                url,
                headers=headers,
                allow_redirects=True,
                timeout_seconds=self.timeout
            )

            status_code = response.status_code

            if status_code == 403:
                domain = urlparse(url).netloc
                return None, f"HTTP 403 Forbidden (Anti-bot block) - {domain}"

            if status_code == 404:
                return None, "HTTP 404 Not Found"

            if not (200 <= status_code < 300):
                return None, f"HTTP {status_code}"

            response_text = response.text
            response_lower = response_text.lower()

            if (
                ("captcha" in response_lower or "robot" in response_lower)
                and len(response_text) < 10000
            ):
                return None, "Captcha detected in content"

            return response_text, None

        except Exception as e:
            return None, str(e)
