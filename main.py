import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime, timedelta
import os
import schedule
import matplotlib.pyplot as plt
import pandas as pd
import logging
import re
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# List of User-Agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Base URL of the site
BASE_URL = 'https://www.minimx.fr/'

# Different category collections for different schedulers
CATEGORY_URLS_3HOUR = [
    'https://www.minimx.fr/fr/230-maillots',
]

CATEGORY_URLS_24HOUR = [
    'https://www.minimx.fr/fr/168-outils-moteur',
]

# Remove duplicates
CATEGORY_URLS_3HOUR = list(dict.fromkeys(CATEGORY_URLS_3HOUR))
CATEGORY_URLS_24HOUR = list(dict.fromkeys(CATEGORY_URLS_24HOUR))

# Directory to store CSV files and plots
DATA_DIR = 'stock_data'
PLOT_DIR = 'stock_plots'

# Global variables to track current file names
current_files = {
    '3hour': {'file': None, 'file_date': None},
    '24hour': {'file': None, 'file_date': None}
}

# Lock for thread-safe file operations
file_lock = threading.Lock()


def get_headers():
    """Generate headers to mimic a browser."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.minimx.fr/',
    }


def setup_directories():
    """Create directories for data and plots if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)


def get_scheduler_filename(scheduler_type):
    """Get or create filename for specific scheduler type. Files are created daily if they don't exist, otherwise data is appended."""
    with file_lock:
        current_date = datetime.now().date()

        # Check if we need a new file (if the date has changed or no file exists)
        if (current_files[scheduler_type]['file'] is None or
                current_files[scheduler_type]['file_date'] != current_date):

            # Generate new filename based on current date
            date_str = current_date.strftime('%Y-%m-%d')
            filename = os.path.join(DATA_DIR, f'{scheduler_type}-{date_str}.csv')

            # If the file doesn't exist, create it with headers
            if not os.path.exists(filename):
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write column descriptions
                    writer.writerow([
                        '# Column Descriptions:'
                    ])
                    writer.writerow([
                        '# timestamp - Date and time of data collection'
                    ])
                    writer.writerow([
                        '# id_product - Unique product identifier'
                    ])
                    writer.writerow([
                        '# reference - Product reference/SKU code'
                    ])
                    writer.writerow([
                        '# meta_title - Product page title'
                    ])
                    writer.writerow([
                        '# url - Direct link to product page'
                    ])
                    writer.writerow([
                        '# category_url - Category page URL where product was found'
                    ])
                    writer.writerow([
                        '# price_without_reduction - Original price before discount'
                    ])
                    writer.writerow([
                        '# discount_amount - Amount of discount applied'
                    ])
                    writer.writerow([
                        '# price - Final price after discount'
                    ])
                    writer.writerow([
                        '# available_date - Product availability date'
                    ])
                    writer.writerow([
                        '# stock_quantity - Stock quantity for current version'
                    ])
                    writer.writerow([
                        '# quantity_all_versions - Total stock across all versions'
                    ])
                    writer.writerow([])  # Empty line

                    # Write actual headers
                    writer.writerow([
                        'timestamp', 'id_product', 'reference', 'meta_title', 'url', 'category_url',
                        'price_without_reduction', 'discount_amount', 'price', 'available_date',
                        'stock_quantity', 'quantity_all_versions'
                    ])
                logging.info(f"Created new {scheduler_type} CSV file: {filename}")
            else:
                logging.info(f"Using existing {scheduler_type} CSV file for today: {filename}. Appending data.")

            current_files[scheduler_type]['file'] = filename
            current_files[scheduler_type]['file_date'] = current_date

        return current_files[scheduler_type]['file']


def get_product_links(session, category_url):
    """Extract product links from a category page, handling pagination."""
    product_links = []
    page = 1
    max_pages = 20
    previous_page_products = set()

    while page <= max_pages:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            logging.info(f"Fetching page {page} of {category_url}")
            response = session.get(url, headers=get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            products_container = soup.select_one('#products')
            if not products_container:
                logging.info(f"No products container found on page {page} of {category_url}")
                break

            products = products_container.select('a.product-thumbnail')
            if not products:
                logging.info(f"No more products found on page {page} of {category_url}")
                break

            pagination = soup.select_one('.pagination')
            if pagination:
                next_disabled = pagination.select_one('.next.disabled') or not pagination.select_one('.next')
                if next_disabled:
                    logging.info(f"Reached last page ({page}) for {category_url}")

            current_page_products = set()
            current_page_links = []

            for product in products:
                href = product.get('href')
                if href and '/fr/' in href and 'index.php' not in href:
                    product_id = re.search(r'/(\d+)-', href)
                    product_id = product_id.group(1) if product_id else None
                    if product_id:
                        current_page_products.add(product_id)
                        current_page_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category_url': category_url
                        })

            if current_page_products and current_page_products == previous_page_products:
                logging.warning(
                    f"Detected duplicate products on page {page} of {category_url}, breaking pagination loop")
                break

            if page > 1 and len(current_page_products) == len(previous_page_products) and all(
                    pid in previous_page_products for pid in current_page_products):
                logging.warning(
                    f"Page {page} appears to contain the same products as previous page for {category_url}, stopping pagination")
                break

            if not current_page_links:
                logging.info(f"No new products found on page {page} of {category_url}")
                break

            product_links.extend(current_page_links)
            previous_page_products = current_page_products

            logging.info(f"Found {len(current_page_links)} products on page {page} of {category_url}")
            page += 1
            time.sleep(3)
        except requests.RequestException as e:
            logging.error(f"Error fetching category page {url}: {e}")
            break

    if page > max_pages:
        logging.warning(f"Reached maximum page limit ({max_pages}) for {category_url}")

    logging.info(f"Total of {len(product_links)} products found for {category_url}")
    return product_links


def get_all_products(session, category_urls):
    """Get all product links by scanning category pages."""
    all_products = []
    for category_url in category_urls:
        logging.info(f"Scraping category: {category_url}")
        products = get_product_links(session, category_url)
        all_products.extend(products)
        time.sleep(3)

    # Remove duplicates based on product ID
    seen_ids = set()
    unique_products = []
    for product in all_products:
        if product['id_product'] not in seen_ids:
            unique_products.append(product)
            seen_ids.add(product['id_product'])

    logging.info(f"Total unique products found: {len(unique_products)}")
    return unique_products


def extract_product_details(session, product):
    """Extract detailed product information from product page."""
    try:
        response = session.get(product['url'], headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize default values
        reference = ""
        meta_title = ""
        price_without_reduction = 0
        discount_amount = 0
        price = 0
        available_date = ""
        stock_quantity = 0
        quantity_all_versions = 0

        # Extract meta title from page title
        title_tag = soup.find('title')
        if title_tag:
            meta_title = title_tag.get_text(strip=True)

        # Try to extract product details from JSON data
        product_details_elem = soup.select_one('#product-details')
        if product_details_elem and 'data-product' in product_details_elem.attrs:
            try:
                product_json = json.loads(product_details_elem['data-product'])

                reference = product_json.get('reference', '')
                stock_quantity = product_json.get('quantity', 0)
                quantity_all_versions = product_json.get('quantity_all_versions', 0)
                price = product_json.get('price_amount', 0)
                price_without_reduction = product_json.get('price_without_reduction', price)

                if price_without_reduction and price:
                    discount_amount = float(price_without_reduction) - float(price)
                else:
                    discount_amount = 0

                available_date = product_json.get('available_date', '')

            except (json.JSONDecodeError, KeyError) as json_err:
                logging.error(f"Error parsing product JSON for {product['url']}: {json_err}")

        # Alternative extraction methods if JSON parsing fails
        if not reference:
            ref_elem = soup.select_one('[data-product-reference]')
            if ref_elem:
                reference = ref_elem.get('data-product-reference', '')
            else:
                ref_patterns = [
                    soup.select_one('.product-reference'),
                    soup.select_one('.reference'),
                    soup.select_one('[class*="reference"]')
                ]
                for elem in ref_patterns:
                    if elem:
                        reference = elem.get_text(strip=True).replace('Référence:', '').strip()
                        break

        if not price:
            price_elem = soup.select_one('.price, .current-price, [class*="price"]')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', '.'))
                if price_match:
                    price = float(price_match.group())

        if not price_without_reduction:
            original_price_elem = soup.select_one('.regular-price, .old-price, [class*="original"]')
            if original_price_elem:
                price_text = original_price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', '.'))
                if price_match:
                    price_without_reduction = float(price_match.group())
            else:
                price_without_reduction = price

        if price_without_reduction and price and not discount_amount:
            discount_amount = float(price_without_reduction) - float(price)

        return {
            'id_product': product['id_product'],
            'reference': reference,
            'meta_title': meta_title,
            'url': product['url'],
            'category_url': product['category_url'],
            'price_without_reduction': price_without_reduction,
            'discount_amount': discount_amount,
            'price': price,
            'available_date': available_date,
            'stock_quantity': stock_quantity,
            'quantity_all_versions': quantity_all_versions
        }

    except requests.RequestException as e:
        logging.error(f"Error fetching product details for {product['url']}: {e}")
        return None


def save_stock_data_batch(all_product_details, scheduler_type):
    """Save all collected stock data to scheduler-specific CSV file, appending to existing file."""
    if not all_product_details:
        logging.warning(f"No product details to save for {scheduler_type}")
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csv_file = get_scheduler_filename(scheduler_type)

    # Open the file in append mode ('a')
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write scraping session separator
        writer.writerow([])  # Empty line for separation
        writer.writerow([f"=== START SCRAPING SESSION {timestamp} ==="])
        writer.writerow([f"# Scheduler: {scheduler_type}"])
        writer.writerow([f"# Products found: {len(all_product_details)}"])
        writer.writerow([f"# Session started at: {timestamp}"])
        writer.writerow([])  # Empty line

        # Prepare data rows
        rows = []
        for product_details in all_product_details:
            rows.append([
                timestamp,
                product_details['id_product'],
                product_details['reference'],
                product_details['meta_title'],
                product_details['url'],
                product_details['category_url'],
                product_details['price_without_reduction'],
                product_details['discount_amount'],
                product_details['price'],
                product_details['available_date'],
                product_details['stock_quantity'],
                product_details['quantity_all_versions']
            ])

        # Write all data rows
        writer.writerows(rows)

        # Write session end separator
        session_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([])  # Empty line
        writer.writerow([f"=== END SCRAPING SESSION {session_end_time} ==="])
        writer.writerow([
            f"# Session duration: {(datetime.now() - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).total_seconds():.2f} seconds"])
        writer.writerow([])  # Empty line for next session

    logging.info(f"Appended {len(rows)} product records to {scheduler_type} CSV file: {csv_file}")


def monitor_stocks_scheduler(category_urls, scheduler_type, interval_name):
    """Monitor stock levels for specific scheduler."""
    logging.info(f"Starting {scheduler_type} monitor ({interval_name})...")

    session = requests.Session()

    logging.info(f"Collecting products for {scheduler_type}...")
    products = get_all_products(session, category_urls)
    if not products:
        logging.error(f"No products found for {scheduler_type}. Skipping.")
        return
    logging.info(f"Collected {len(products)} products for {scheduler_type}")

    all_product_details = []
    for product in products:
        logging.info(f"Processing product for {scheduler_type}: {product['id_product']}")

        product_details = extract_product_details(session, product)
        if product_details:
            all_product_details.append(product_details)

        time.sleep(2)  # Reduced delay for faster processing

    logging.info(f"Saving {len(all_product_details)} product details for {scheduler_type}")
    save_stock_data_batch(all_product_details, scheduler_type)


def monitor_3hour():
    """3-hour scheduler function."""
    monitor_stocks_scheduler(CATEGORY_URLS_3HOUR, '3hour', 'every 3 hours')


def monitor_24hour():
    """24-hour scheduler function."""
    monitor_stocks_scheduler(CATEGORY_URLS_24HOUR, '24hour', 'every 24 hours')


def run_scheduler_thread(scheduler_func, interval_hours):
    """Run a scheduler in a separate thread."""
    if interval_hours == 3:
        schedule.every(5).minutes.do(scheduler_func)
    elif interval_hours == 24:
        schedule.every(10).minutes.do(scheduler_func)

    # Run immediately on start
    scheduler_func()

    while True:
        schedule.run_pending()
        time.sleep(300)  # Check every 5 minutes


def main():
    """Main function to start parallel schedulers."""
    setup_directories()

    logging.info("Starting parallel stock monitoring with multiple schedulers...")
    logging.info("3-hour scheduler: monitoring motocross categories")
    logging.info("24-hour scheduler: monitoring electric categories")
    logging.info("New files will be created daily for each scheduler, and data will be appended to them.")

    # Create thread pool for parallel execution
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both scheduler threads
        future_3hour = executor.submit(run_scheduler_thread, monitor_3hour, 3)
        future_24hour = executor.submit(run_scheduler_thread, monitor_24hour, 24)

        try:
            # Wait for both threads (they run indefinitely)
            future_3hour.result()
            future_24hour.result()
        except KeyboardInterrupt:
            logging.info("Received interrupt signal. Stopping schedulers...")
            executor.shutdown(wait=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise