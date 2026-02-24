import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from config import SEARCH_RESULTS, TIMEOUT

def unwrap_ddg(url):
    """
    DuckDuckGo sometimes returns URLs like:
    https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com
    This function extracts the real URL from the uddg parameter.
    If the URL is already clean, it is returned unchanged.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        if "duckduckgo.com" in parsed.netloc:
            qs = urllib.parse.parse_qs(parsed.query)
            uddg = qs.get("uddg")
            if uddg:
                return urllib.parse.unquote(uddg[0])
    except Exception:
        pass
    return url
def search_web(query, max_results=SEARCH_RESULTS):
    """
    Search DuckDuckGo for the query string.
    Returns a list of clean source URLs.
    """
    urls = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            # Different versions of ddgs use different key names
            url = r.get("href") or r.get("url")
            if not url:
                continue
            urls.append(unwrap_ddg(url))
    return urls

def fetch_text(url, timeout=TIMEOUT):
    """
    Download and clean a web page.
    Returns a plain-text string, or an empty string on failure.
    Fails silently — a broken URL should not crash the agent.
    """
    headers = {"User-Agent": "Mozilla/5.0 (research-agent)"}
    try:
        r = requests.get(url, timeout=timeout,
                         headers=headers, allow_redirects=True)

        # Skip non-200 responses
        if r.status_code != 200:
            return ""

        # Skip PDFs, images, JSON feeds, etc.
        if "html" not in r.headers.get("content-type", "").lower():
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        # Remove clutter tags before reading text
        for tag in soup(["script", "style", "noscript", "header",
                         "footer", "svg", "iframe", "nav", "aside"]):
            tag.extract()

        # Collect all paragraph text
        paragraphs = [p.get_text(" ", strip=True)
                      for p in soup.find_all("p")]
        text = " ".join([p for p in paragraphs if p])

        if text.strip():
            # Collapse multiple spaces or newlines into a single space
            return re.sub(r"\s+", " ", text).strip()

        # ── Fallback: try meta description
        meta = (soup.find("meta", attrs={"name": "description"}) or
                soup.find("meta", attrs={"property": "og:description"}))
        if meta and meta.get("content"):
            return meta["content"].strip()

    except Exception:
        return ""   

    return ""
