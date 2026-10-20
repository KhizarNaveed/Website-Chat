import trafilatura
from bs4 import BeautifulSoup
import httpx

def scrape_url(url: str) -> str:
    """
    Extract clean main content from a URL.
    Tries trafilatura first (best for articles), falls back to BeautifulSoup.
    """
    print(f"[SCRAPER] Fetching: {url}")

    # --- Method 1: trafilatura (best for article content) ---
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_precision=True,
            )
            if text and len(text.strip()) > 200:
                print(f"[SCRAPER] trafilatura extracted {len(text)} chars")
                return text
    except Exception as e:
        print(f"[SCRAPER] trafilatura failed: {e}")

    # --- Method 2: BeautifulSoup fallback ---
    try:
        print("[SCRAPER] Falling back to BeautifulSoup...")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove boilerplate
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        print(f"[SCRAPER] BeautifulSoup extracted {len(text)} chars")

        if len(text) < 100:
            raise RuntimeError("Page content too short — likely JavaScript-rendered or blocked")

        return text
    except Exception as e:
        raise RuntimeError(f"Failed to scrape {url}: {e}")