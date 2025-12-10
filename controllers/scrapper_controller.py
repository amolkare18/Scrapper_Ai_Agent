import requests
from bs4 import BeautifulSoup
import logging

from pipelines.data_pipeline import DataPipeline

from helpers.utils import get_scrapper_api_url
from products.products import Product

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def search_products(product_name:str, page_number:int=1, location:str="in", retries:int=3,data_pipeline=None):
    scrapped_products = []
    attempts = 0
    success = False

    while attempts < retries and not success:
        try:
            search_url = get_scrapper_api_url(f"https://www.amazon.com/s?k={product_name}&page={page_number}", location)
            logger.info(f"Scraping URL: {search_url}")

            response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                raise Exception(f"Failed to load page, status code: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove ads
            for ad_div in soup.find_all("div", class_="AdHolder"):
                ad_div.decompose()

            product_divs = soup.find_all("div")

            for product_div in product_divs:
                try:
                    h2 = product_div.find("h2")
                    if not h2:
                        continue

                    product_title = h2.text.strip()
                    a = h2.find("a")

                    product_url = "https://www.amazon.com" + a['href'] if a and 'href' in a.attrs else ""

                    name = product_div.get("data-asin", "").strip()
                    if not name:
                        continue

                    is_sponsered = "sspa" in product_url.lower()

                    price_currency = product_div.find("span", class_="a-price-symbol")
                    currency = price_currency.text.strip() if price_currency else ""

                    prices = product_div.find_all("span", class_="a-offscreen")

                    try:
                        current_price = float(prices[0].text.replace(currency, "").replace(",", "").strip()) if prices else 0.0
                        original_price = float(prices[1].text.replace(currency, "").replace(",", "").strip()) if len(prices) > 1 else current_price

                    except:
                        continue

                    rating_span = product_div.find("span", class_="a-icon-alt")
                    rating = float(rating_span.text.split(" ")[0]) if rating_span else 0.0

                    product = Product(
                        name=name,
                        product_title=product_title,
                        product_url=product_url,
                        current_price=current_price,
                        original_price=original_price,
                        currency=currency,
                        rating=rating,
                        is_sponsered=is_sponsered
                    )

                    data_pipeline.add_data(product)
                    success = True

                except Exception as e:
                    logger.warning(f"Error parsing product div: {e}")

            if not success:
                logger.info("Scraping failed")

        except Exception as e:
            logger.warning(f"Error during scraping: {e}")

        attempts += 1

    return scrapped_products   # ✅ RETURN AFTER COMPLETING LOOP
