import random
import time
from typing import Optional, Tuple
import tls_client
import re
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
        self.session = self._new_session()
        self.cookies_warmed_up = set()

    def _new_session(self) -> tls_client.Session:
        return tls_client.Session(
            client_identifier=self.client_identifier,
            random_tls_extension_order=True
        )

    def _get_headers(self, url: str) -> dict:
        parsed = urlparse(url)
        domain = parsed.netloc

        h = {
            "authority": domain,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "cs-CZ,cs;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": random.choice(USER_AGENTS)
        }

        if "datart" in domain:
            h["referer"] = "https://www.seznam.cz/"

        if "czc" in domain:
            h["referer"] = "https://www.google.com/"

        if domain in self.cookies_warmed_up:
            h["sec-fetch-site"] = "same-origin"
            h["referer"] = f"https://{domain}/"

        return h

    def _warm_up(self, url: str):
        domain = urlparse(url).netloc

        if domain in self.cookies_warmed_up:
            return

        try:
            home_url = f"https://{domain}/"
            self.session.get(
                home_url,
                headers=self._get_headers(home_url),
                timeout_seconds=10
            )
            self.cookies_warmed_up.add(domain)
            time.sleep(random.uniform(1.0, 2.5))
        except:
            pass

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

            if response.status_code == 403:
                return None, f"HTTP 403 Forbidden (Anti-bot block) - {urlparse(url).netloc}"

            if response.status_code == 404:
                return None, f"HTTP 404 Not Found"

            if not (200 <= response.status_code < 300):
                return None, f"HTTP {response.status_code}"

            html_lower = response.text.lower()
            if ("captcha" in html_lower or "robot" in html_lower) and len(response.text) < 10000:
                return None, "Captcha detected in content"

            return response.text, None

        except Exception as e:
            return None, str(e)