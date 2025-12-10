import random
import time
from typing import Optional, Tuple
import tls_client

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

BROWSER_HEADERS = {
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

TLS_CLIENT_IDS = [
    "chrome_124",
    "chrome_123",
    "chrome_120",
    "chrome_118"
]

class Downloader:
    """High-success downloader for Czech e-shops with anti-bot protection bypass."""

    def __init__(self, timeout: int = 7):
        self.timeout = timeout
        self.session = self._new_session()

    def _new_session(self) -> tls_client.Session:
        """Create a fresh TLS client session with Chrome-like fingerprint."""
        return tls_client.Session(
            client_identifier=random.choice(TLS_CLIENT_IDS),
            random_tls_extension_order=True
        )

    def _prepare_headers(self) -> dict:
        h = BROWSER_HEADERS.copy()
        ua = random.choice(USER_AGENTS)
        h["User-Agent"] = ua
        h["sec-ch-ua"] = '"Chromium";v="124", "Not-A.Brand";v="99"'
        h["sec-ch-ua-mobile"] = "?0"
        h["sec-ch-ua-platform"] = '"Windows"'
        return h

    def _delay(self):
        time.sleep(random.uniform(1.1, 2.8))

    def _init_cookies(self):
        """Load homepage first – Alza sets several validation cookies here."""
        try:
            self.session.get(
                "https://www.alza.cz/",
                headers=self._prepare_headers()
            )
            time.sleep(0.5)
        except:
            pass

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Download page content with retry on 403."""
        try:
            self._init_cookies()
            self._delay()

            headers = self._prepare_headers()
            response = self.session.get(url, headers=headers)

            if response.status_code == 403:
                self._delay()
                self.session = self._new_session()
                headers = self._prepare_headers()
                response = self.session.get(url, headers=headers)

            if not (200 <= response.status_code < 300):
                return None, f"HTTP {response.status_code}"

            return response.text, None

        except Exception as e:
            return None, str(e)
