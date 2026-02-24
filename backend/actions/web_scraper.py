"""
Web scraper: uses Playwright for JS-heavy sites, falls back to httpx + BeautifulSoup.
"""
from __future__ import annotations

import re
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, use_playwright: bool = False):
        self.use_playwright = use_playwright

    def fetch(self, url: str, timeout: int = 20) -> str:
        """Fetch URL and return cleaned text content."""
        if self.use_playwright:
            try:
                return self._playwright_fetch(url)
            except Exception:
                pass
        return self._httpx_fetch(url, timeout)

    def search(self, query: str, num_results: int = 5) -> str:
        """Search DuckDuckGo and return top results as text."""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        try:
            html = self._httpx_fetch(url)
            soup = BeautifulSoup(html, "lxml")
            results = []
            for r in soup.select(".result")[:num_results]:
                title_el = r.select_one(".result__title")
                snippet_el = r.select_one(".result__snippet")
                link_el = r.select_one(".result__url")
                if title_el and snippet_el:
                    results.append(
                        f"• {title_el.get_text(strip=True)}\n"
                        f"  {snippet_el.get_text(strip=True)}\n"
                        f"  {link_el.get_text(strip=True) if link_el else ''}"
                    )
            return "\n\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Search failed: {e}"

    # ──────────────────────────────────────────────────────────────────────────

    def _httpx_fetch(self, url: str, timeout: int = 20) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # Collapse whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:8000]

    def _playwright_fetch(self, url: str) -> str:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            content = page.content()
            browser.close()
        soup = BeautifulSoup(content, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:8000]
