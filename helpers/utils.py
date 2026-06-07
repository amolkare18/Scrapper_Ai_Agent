from urllib.parse import urlencode
from helpers.config import API_KEY
import pandas as pd
import json
from datetime import datetime

PRODUCT_COLUMNS = [
    'name',
    'product_title',
    'product_url',
    'current_price',
    'original_price',
    'currency',
    'rating',
    'is_sponsered',
    'image_url',
    'review_count',
    'discount_percent',
    'seller_name',
    'availability_status',
]

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


def read_products_csv(csv_filename: str) -> pd.DataFrame:
    """Read product CSVs, including older files with fewer columns."""
    try:
        return pd.read_csv(csv_filename)
    except pd.errors.ParserError:
        return pd.read_csv(
            csv_filename,
            names=PRODUCT_COLUMNS,
            header=None,
            skiprows=1,
            engine='python',
        )


def export_to_json(csv_filename: str, json_filename: str = None) -> str:
    """Export CSV data to JSON format"""
    if json_filename is None:
        json_filename = csv_filename.replace('.csv', '.json')
    
    try:
        df = read_products_csv(csv_filename)
        df.to_json(json_filename, orient='records', indent=2)
        return json_filename
    except Exception as e:
        raise Exception(f"Error exporting to JSON: {e}")


def export_to_excel(csv_filename: str, excel_filename: str = None) -> str:
    """Export CSV data to Excel format"""
    if excel_filename is None:
        excel_filename = csv_filename.replace('.csv', '.xlsx')
    
    try:
        df = read_products_csv(csv_filename)
        df.to_excel(excel_filename, index=False, sheet_name='Products')
        return excel_filename
    except Exception as e:
        raise Exception(f"Error exporting to Excel: {e}")


def get_file_download_bytes(filename: str, file_format: str = 'csv'):
    """Get file content as bytes for download"""
    try:
        if file_format.lower() == 'json':
            filename = filename.replace('.csv', '.json')
            with open(filename, 'rb') as f:
                return f.read(), filename
        elif file_format.lower() == 'xlsx':
            filename = filename.replace('.csv', '.xlsx')
            with open(filename, 'rb') as f:
                return f.read(), filename
        else:  # CSV
            with open(filename, 'rb') as f:
                return f.read(), filename
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
