from urllib.parse import urlencode
from helpers.config import API_KEY

def get_scrapper_api_url(url, location) -> str:
    if not API_KEY:
        raise ValueError("API_KEY is not set in the environment variables.")
    payload = {
        "api_key": API_KEY,
        "url": url,
        "country": location,
        "bypass": "cloudflare",
        "render_js": "true",
        "keep_headers": "true",
    }
    return f"https://proxy.scrapeops.io/v1/?{urlencode(payload)}"
