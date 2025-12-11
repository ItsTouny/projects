import random
import time
from typing import Optional, Tuple
import tls_client
import re
from urllib.parse import urlparse

# --- KONFIGURACE USER AGENTŮ ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]


class Downloader:
    """Universal downloader for Alza, Datart, CZC."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        # Používáme stabilní profil Chrome 124
        self.client_identifier = "chrome_124"
        self.session = self._new_session()
        # Služba pro sledování, kde už máme cookies
        self.cookies_warmed_up = set()

    def _new_session(self) -> tls_client.Session:
        return tls_client.Session(
            client_identifier=self.client_identifier,
            random_tls_extension_order=True
        )

    def _get_headers(self, url: str) -> dict:
        """Generuje hlavičky specifické pro danou doménu (Alza/Datart/CZC)."""
        parsed = urlparse(url)
        domain = parsed.netloc

        # Základní hlavičky (Chrome style)
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

        # --- SPECIFIKA E-SHOPŮ ---

        # Datart: Kriticky vyžaduje Referer, jinak vrací chyby
        if "datart" in domain:
            h["referer"] = "https://www.seznam.cz/"

        # CZC: Má rádo Google referer a same-site fetch
        if "czc" in domain:
            h["referer"] = "https://www.google.com/"

        # Pokud už jsme na doméně byli (máme cookies), upravíme fetch-site
        if domain in self.cookies_warmed_up:
            h["sec-fetch-site"] = "same-origin"
            h["referer"] = f"https://{domain}/"

        return h

    def _warm_up(self, url: str):
        """Navštíví homepage pro nastavení cookies (Anti-bot ochrana)."""
        domain = urlparse(url).netloc

        # Pokud už jsme tu byli, nezatěžujeme server zbytečně
        if domain in self.cookies_warmed_up:
            return

        try:
            # Jdeme na homepage
            home_url = f"https://{domain}/"
            self.session.get(
                home_url,
                headers=self._get_headers(home_url),
                timeout_seconds=10
            )
            self.cookies_warmed_up.add(domain)
            # Krátká pauza, aby to vypadalo, že uživatel hledá produkt
            time.sleep(random.uniform(1.0, 2.5))
        except:
            # Ignorujeme chyby při warm-up, zkusíme to i tak
            pass

    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            # 1. Warm-up (získá cookies z homepage)
            self._warm_up(url)

            headers = self._get_headers(url)

            # 2. Stažení produktu
            # Používáme timeout_seconds (tls_client specifikum)
            response = self.session.get(
                url,
                headers=headers,
                allow_redirects=True,
                timeout_seconds=self.timeout
            )

            # 3. Kontrola chybových stavů
            if response.status_code == 403:
                return None, f"HTTP 403 Forbidden (Anti-bot block) - {urlparse(url).netloc}"

            if response.status_code == 404:
                return None, f"HTTP 404 Not Found"

            if not (200 <= response.status_code < 300):
                return None, f"HTTP {response.status_code}"

            # 4. Kontrola Captcha (Alza/CZC někdy vrací 200 OK ale s captchou)
            html_lower = response.text.lower()
            if ("captcha" in html_lower or "robot" in html_lower) and len(response.text) < 10000:
                return None, "Captcha detected in content"

            return response.text, None

        except Exception as e:
            return None, str(e)
