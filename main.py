import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import os
import schedule
import pandas as pd
import logging
import re
import json
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# User-Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Base URL and categories
BASE_URL = 'https://www.minimx.fr/'
CATEGORY_URLS = [
    'https://www.minimx.fr/fr/230-maillots'
]

# Output file
DATA_FILE = 'stock_data/products_data.csv'


def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': BASE_URL,
    }


def get_product_links(session, category_url):
    """Get all product links from a category with pagination"""
    product_links = []
    page = 1
    max_pages = 20
    previous_products = set()

    while page <= max_pages:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            logging.info(f"Fetching page {page} of {category_url}")
            response = session.get(url, headers=get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            products = soup.select('#products a.product-thumbnail')
            if not products:
                break

            current_products = set()
            for product in products:
                href = product.get('href')
                if href and '/fr/' in href:
                    product_id = re.search(r'/(\d+)-', href)
                    if product_id:
                        product_id = product_id.group(1)
                        current_products.add(product_id)
                        product_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category_url': category_url
                        })

            if current_products == previous_products:
                break

            previous_products = current_products
            page += 1
            time.sleep(2)
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            break

    return product_links


def get_all_products(session):
    """Get all products from all categories"""
    all_products = []
    for category_url in CATEGORY_URLS:
        products = get_product_links(session, category_url)
        all_products.extend(products)
        time.sleep(3)

    # Remove duplicates
    seen = set()
    unique_products = []
    for p in all_products:
        if p['id_product'] not in seen:
            seen.add(p['id_product'])
            unique_products.append(p)

    return unique_products


def extract_product_details(session, product):
    """Extract detailed product info"""
    try:
        response = session.get(product['url'], headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize defaults
        details = {
            'id_product': product['id_product'],
            'reference': '',
            'meta_title': '',
            'url': product['url'],
            'category_url': product['category_url'],
            'price_without_reduction': 0,
            'discount_amount': 0,
            'price': 0,
            'available_date': '',
            'stock_quantity': 0,
            'quantity_all_versions': 0
        }

        # Try to get data from JSON first
        product_json = soup.select_one('#product-details[data-product]')
        if product_json:
            try:
                data = json.loads(product_json['data-product'])
                details.update({
                    'reference': data.get('reference', ''),
                    'meta_title': soup.title.get_text(strip=True) if soup.title else '',
                    'price_without_reduction': float(data.get('price_without_reduction', 0)),
                    'price': float(data.get('price_amount', 0)),
                    'discount_amount': float(data.get('price_without_reduction', 0)) - float(
                        data.get('price_amount', 0)),
                    'available_date': data.get('available_date', ''),
                    'stock_quantity': int(data.get('quantity', 0)),
                    'quantity_all_versions': int(data.get('quantity_all_versions', 0))
                })
                return details
            except Exception as e:
                logging.error(f"Error parsing JSON for {product['url']}: {e}")

        # Fallback to HTML parsing
        details['meta_title'] = soup.title.get_text(strip=True) if soup.title else ''

        # Reference
        ref_elem = soup.select_one('[data-product-reference], .product-reference, .reference')
        if ref_elem:
            details['reference'] = ref_elem.get('data-product-reference', ref_elem.get_text(strip=True))

        # Prices
        price_elem = soup.select_one('.current-price, .price')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\d,]+', price_text.replace(',', '.'))
            if price_match:
                details['price'] = float(price_match.group())

        original_price_elem = soup.select_one('.regular-price, .old-price')
        if original_price_elem:
            price_text = original_price_elem.get_text(strip=True)
            price_match = re.search(r'[\d,]+', price_text.replace(',', '.'))
            if price_match:
                details['price_without_reduction'] = float(price_match.group())
        else:
            details['price_without_reduction'] = details['price']

        details['discount_amount'] = details['price_without_reduction'] - details['price']

        # Stock
        stock_elem = soup.select_one('.product-quantities, .stock')
        if stock_elem:
            stock_text = stock_elem.get_text(strip=True)
            stock_match = re.search(r'\d+', stock_text)
            if stock_match:
                details['stock_quantity'] = int(stock_match.group())

        return details

    except Exception as e:
        logging.error(f"Error extracting details for {product['url']}: {e}")
        return None


def load_previous_data():
    """Load previous data from file if exists"""
    if not os.path.exists(DATA_FILE):
        return None

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        logging.error(f"Error loading previous data: {e}")
        return None


def compare_products(current, previous):
    """Compare current products with previous data"""
    if not previous:
        return []

    prev_dict = {p['id_product']: p for p in previous}
    changes = []

    for product in current:
        pid = product['id_product']
        if pid in prev_dict:
            prev_product = prev_dict[pid]

            price_changed = float(product['price']) != float(prev_product['price'])
            stock_changed = int(product['stock_quantity']) != int(prev_product['stock_quantity'])

            if price_changed or stock_changed:
                changes.append({
                    'id_product': pid,
                    'reference': product['reference'],
                    'price': product['price'],
                    'previous_price': prev_product['price'],
                    'stock_quantity': product['stock_quantity'],
                    'previous_stock': prev_product['stock_quantity'],
                    'price_change': price_changed,
                    'stock_change': stock_changed,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

    return changes


def save_data(current_products, changes):
    """Save data to file with current products and changes"""
    try:
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            # Write current products
            writer = csv.writer(f)
            writer.writerow(['=== CURRENT PRODUCTS ==='])
            writer.writerow([
                'timestamp', 'id_product', 'reference', 'meta_title', 'url', 'category_url',
                'price_without_reduction', 'discount_amount', 'price', 'available_date',
                'stock_quantity', 'quantity_all_versions'
            ])

            for p in current_products:
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    p['id_product'],
                    p['reference'],
                    p['meta_title'],
                    p['url'],
                    p['category_url'],
                    p['price_without_reduction'],
                    p['discount_amount'],
                    p['price'],
                    p['available_date'],
                    p['stock_quantity'],
                    p['quantity_all_versions']
                ])

            # Write changes section
            writer.writerow([])
            writer.writerow(['=== CHANGES FROM PREVIOUS DAY ==='])
            if changes:
                writer.writerow([
                    'timestamp', 'id_product', 'reference',
                    'price', 'previous_price', 'price_change',
                    'stock_quantity', 'previous_stock', 'stock_change'
                ])
                for change in changes:
                    writer.writerow([
                        change['timestamp'],
                        change['id_product'],
                        change['reference'],
                        change['price'],
                        change['previous_price'],
                        change['price_change'],
                        change['stock_quantity'],
                        change['previous_stock'],
                        change['stock_change']
                    ])
            else:
                writer.writerow(['No changes detected'])

        logging.info(f"Saved {len(current_products)} products and {len(changes)} changes to {DATA_FILE}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")


def daily_monitor():
    """Main monitoring function"""
    logging.info("Starting daily monitoring...")

    session = requests.Session()

    # Get all products
    products = get_all_products(session)
    if not products:
        logging.error("No products found!")
        return

    # Extract details
    current_products = []
    for product in products:
        details = extract_product_details(session, product)
        if details:
            current_products.append(details)
        time.sleep(1)

    # Load previous data and compare
    previous_data = load_previous_data()
    changes = compare_products(current_products, previous_data)

    # Save new data
    save_data(current_products, changes)

    logging.info("Daily monitoring completed")


def main():
    """Main function"""
    logging.info("Starting product monitor")

    # Run immediately and then daily
    daily_monitor()
    schedule.every().day.at("00:00").do(daily_monitor)

    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")