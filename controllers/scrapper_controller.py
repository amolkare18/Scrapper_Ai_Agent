import requests
from bs4 import BeautifulSoup
import logging
import time
from random import uniform

from pipelines.data_pipeline import DataPipeline

from helpers.utils import get_scrapper_api_url
from products.products import Product

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extract_discount_percent(current_price, original_price):
    """Calculate discount percentage"""
    if original_price and current_price and original_price > 0:
        discount = ((original_price - current_price) / original_price) * 100
        return round(max(0, min(100, discount)), 2)
    return 0.0

def extract_review_count(product_div):
    """Extract review count from product div"""
    try:
        review_span = product_div.find("span", {"aria-label": lambda x: x and "K" in str(x)})
        if review_span:
            text = review_span.text.strip()
            return int(text.replace("K", "000") if "K" in text else text)
    except:
        pass
    return 0

def extract_image_url(product_div):
    """Extract product image URL"""
    try:
        img_tag = product_div.find("img", class_="s-image")
        if img_tag and img_tag.get("src"):
            return img_tag.get("src")
    except:
        pass
    return ""

def extract_seller_info(product_div):
    """Extract seller information"""
    try:
        seller_span = product_div.find("span", string=lambda x: x and "by" in str(x).lower())
        if seller_span:
            return seller_span.text.strip()
    except:
        pass
    return "Amazon"

def search_products(product_name: str, page_number: int = 1, location: str = "in", retries: int = 3, max_pages: int = 3, data_pipeline=None):
    """
    Enhanced scraper with pagination and better data extraction
    Args:
        product_name: Product to search
        page_number: Starting page
        location: Country code
        retries: Retry attempts per page
        max_pages: Maximum pages to scrape
        data_pipeline: Data pipeline for storage
    """
    scrapped_products = []
    current_page = page_number

    while current_page < page_number + max_pages:
        logger.info(f"Scraping page {current_page} for product: {product_name}")
        
        attempts = 0
        page_success = False

        while attempts < retries and not page_success:
            try:
                # Add random delay to avoid blocking
                time.sleep(uniform(2, 5))
                
                search_url = get_scrapper_api_url(
                    f"https://www.amazon.com/s?k={product_name}&page={current_page}", 
                    location
                )
                logger.info(f"Scraping URL: {search_url}")

                response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                
                if response.status_code != 200:
                    raise Exception(f"Failed to load page, status code: {response.status_code}")

                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove ads
                for ad_div in soup.find_all("div", class_="AdHolder"):
                    ad_div.decompose()

                # Better selector for product containers
                product_divs = soup.find_all("div", {"data-component-type": "s-search-result"})
                
                if not product_divs:
                    logger.warning(f"No products found on page {current_page}")
                    break

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
                        currency = price_currency.text.strip() if price_currency else "$"

                        prices = product_div.find_all("span", class_="a-offscreen")

                        try:
                            current_price = float(prices[0].text.replace(currency, "").replace(",", "").strip()) if prices else 0.0
                            original_price = float(prices[1].text.replace(currency, "").replace(",", "").strip()) if len(prices) > 1 else current_price
                        except:
                            continue

                        rating_span = product_div.find("span", class_="a-icon-alt")
                        rating = float(rating_span.text.split(" ")[0]) if rating_span else 0.0

                        # Extract new fields
                        discount_percent = extract_discount_percent(current_price, original_price)
                        review_count = extract_review_count(product_div)
                        image_url = extract_image_url(product_div)
                        seller_name = extract_seller_info(product_div)

                        product = Product(
                            name=name,
                            product_title=product_title,
                            product_url=product_url,
                            current_price=current_price,
                            original_price=original_price,
                            currency=currency,
                            rating=rating,
                            is_sponsered=is_sponsered,
                            image_url=image_url,
                            review_count=review_count,
                            discount_percent=discount_percent,
                            seller_name=seller_name,
                            availability_status="In Stock"
                        )

                        data_pipeline.add_data(product)
                        scrapped_products.append(product)
                        page_success = True

                    except Exception as e:
                        logger.warning(f"Error parsing product div: {e}")

                if not page_success and product_divs:
                    logger.info(f"No valid products extracted from page {current_page}")

            except Exception as e:
                logger.warning(f"Error during scraping (attempt {attempts + 1}/{retries}): {e}")

            attempts += 1

        current_page += 1

    logger.info(f"Total products scraped: {len(scrapped_products)}")
    return scrapped_products
