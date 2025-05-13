import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import os
import schedule
import matplotlib.pyplot as plt
import pandas as pd
import logging
import re
import json
import random

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


# Headers to mimic a browser
def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.minimx.fr/',
    }


# Base URL of the site
BASE_URL = 'https://www.minimx.fr/'

# List of category URLs
CATEGORY_URLS = [
    'https://www.minimx.fr/fr/743-10-grandes-roues',
    'https://www.minimx.fr/fr/670-motocross-crz-erz',
    'https://www.minimx.fr/fr/419-motocross',
    'https://www.minimx.fr/fr/782-les-electriques',
    'https://www.minimx.fr/fr/666-motocross-150cc',
    'https://www.minimx.fr/fr/667-motocross-250cc',
    'https://www.minimx.fr/fr/668-les-motocross-300cc',
    'https://www.minimx.fr/fr/736-les-motocross-450cc',
    'https://www.minimx.fr/fr/100-dirt-bike-pit-bike-motocross',
    'https://www.minimx.fr/fr/476-les-mini-moto-electriques',
    'https://www.minimx.fr/fr/136-les-50cc-70cc-88cc-enfant-et-mini-rider',
    'https://www.minimx.fr/fr/749-les-110cc',
    'https://www.minimx.fr/fr/133-dirt-bike-125cc-lifan-yx',
    'https://www.minimx.fr/fr/135-dirt-bike-moteur-150cc-yx',
    'https://www.minimx.fr/fr/533-les-dirt-bike-et-pit-bike-160cc',
    'https://www.minimx.fr/fr/535-les-pit-bike-et-dirt-bike-190cc',
    'https://www.minimx.fr/fr/346-les-motocross-250cc',
    'https://www.minimx.fr/fr/629-les-motocross-300cc',
    'https://www.minimx.fr/fr/737-les-450cc',
    'https://www.minimx.fr/fr/3-dirt-bike-mini-mx',
    'https://www.minimx.fr/fr/327-taille-de-roue-grande-roue-dirt-bike',
    'https://www.minimx.fr/fr/328-dirt-bike-10-12-petites-roues',
    'https://www.minimx.fr/fr/329-dirt-bike-12-14-taille-standard',
    'https://www.minimx.fr/fr/330-dirt-bike-grandes-roues-14-arriere-et-17-avant',
    'https://www.minimx.fr/fr/334-motocross-16-19-grandes-roues',
    'https://www.minimx.fr/fr/519-motocross-18-21',
    'https://www.minimx.fr/fr/392-vehicules-pocket-cross-et-pocket-electrique',
    'https://www.minimx.fr/fr/306-pocket-cross-thermique',
    'https://www.minimx.fr/fr/416-pocket-cross-electriques',
    'https://www.minimx.fr/fr/413-les-cylindrees-de-pocket-bike-thermique-et-electrique',
    'https://www.minimx.fr/fr/414-49cc-enfant-de-3-a-8ans',
    'https://www.minimx.fr/fr/739-60cc-enfant-de-6-a-12ans',
    'https://www.minimx.fr/fr/556-Pocket-Quad-Quad-Electrique-et-Quad-4-Temps',
    'https://www.minimx.fr/fr/557-pocket-quad-2-temps-pour-enfant',
    'https://www.minimx.fr/fr/558-quad-4-temps-pour-enfant',
    'https://www.minimx.fr/fr/559-quad-electriques-pour-enfant',
    'https://www.minimx.fr/fr/744-quad-adultes-a-partir-de-14-ans',
    'https://www.minimx.fr/fr/633-draisienne-electrique-pour-enfant',
    'https://www.minimx.fr/fr/631-voitures-electrique-pour-enfant',
    'https://www.minimx.fr/fr/632-voiture-electrique-buggy-4x4-pour-enfant',
    'https://www.minimx.fr/fr/649-quad-electrique-pour-enfant',
    'https://www.minimx.fr/fr/652-voiture-electrique-pour-enfant',
    'https://www.minimx.fr/fr/616-velo-electrique-ville-et-vtt',
    'https://www.minimx.fr/fr/617-velo-electrique-pliant-crz',
    'https://www.minimx.fr/fr/618-vtt-electrique',
    'https://www.minimx.fr/fr/619-vtc-electrique',
    'https://www.minimx.fr/fr/771-moto-dax-skyteam-homologue',
    'https://www.minimx.fr/fr/772-thermique-a-essencemoto-dax-skyteam-thermique-50cc-et-125cc',
    'https://www.minimx.fr/fr/773-electrique',
    'https://www.minimx.fr/fr/778-voiture-rc-telecommande-electrique'
]

# Directory to store CSV files and plots
DATA_DIR = 'stock_data'
PLOT_DIR = 'stock_plots'
CSV_FILE = os.path.join(DATA_DIR, 'stock_data.csv')


def setup_directories():
    """Create directories for data and plots if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)


def initialize_csv():
    """Initialize a single CSV file for all products, overwriting if it exists."""
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['timestamp', 'id_product', 'category', 'name', 'stock_quantity', 'quantity_all_version', 'price',
             'price_without_reduction'])
    return CSV_FILE


def get_product_links(session, category_url):
    """Extract product links from a category page, handling pagination."""
    product_links = []
    page = 1
    while True:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            response = session.get(url, headers=get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find product links within id="products" using only a.product-thumbnail
            products_container = soup.select_one('#products')
            if not products_container:
                logging.info(f"No products container found on page {page} of {category_url}")
                break

            products = products_container.select('a.product-thumbnail')
            if not products:
                logging.info(f"No more products found on page {page} of {category_url}")
                break

            for product in products:
                href = product.get('href')
                if href and '/fr/' in href and 'index.php' not in href:
                    # Extract product ID from URL (e.g., /fr/quad/123-product1.html)
                    product_id = re.search(r'/(\d+)-', href)
                    product_id = product_id.group(1) if product_id else None
                    if product_id:
                        product_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category': category_url
                        })
            logging.info(f"Found {len(products)} products on page {page} of {category_url}")
            page += 1
            time.sleep(5)  # Increased delay to avoid server overload
        except requests.RequestException as e:
            logging.error(f"Error fetching category page {url}: {e}")
            break
    return product_links


def get_all_products(session):
    """Get all product links by scanning category pages."""
    all_products = []
    for category_url in CATEGORY_URLS:
        logging.info(f"Scraping category: {category_url}")
        products = get_product_links(session, category_url)
        all_products.extend(products)
        time.sleep(5)  # Increased delay between categories

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

        # Try to extract product details from JSON data
        product_details_elem = soup.select_one('#product-details')
        if product_details_elem and 'data-product' in product_details_elem.attrs:
            try:
                product_json = json.loads(product_details_elem['data-product'])

                # Extract key details
                stock_quantity = product_json.get('quantity', 0)

                # Extract quantity_all_version
                quantity_all_version = product_json.get('quantity_all_version', 0)

                # Price details
                price = product_json.get('price_amount', 0)  # Changed from 'price' to 'price_amount'
                price_without_reduction = product_json.get('price_without_reduction', price)

                # Logging for verification
                logging.info(f"Product Details - ID: {product['id_product']}, URL: {product['url']}, "
                             f"Stock: {stock_quantity}, All Versions Stock: {quantity_all_version}, Price: {price}, "
                             f"Price without Reduction: {price_without_reduction}")

                return {
                    'id_product': product['id_product'],
                    'category': product['category'],  # Added category
                    'name': product['url'],  # Use product URL as name
                    'stock_quantity': stock_quantity,
                    'quantity_all_version': quantity_all_version,  # Added quantity_all_version
                    'price': price,
                    'price_without_reduction': price_without_reduction
                }
            except (json.JSONDecodeError, KeyError) as json_err:
                logging.error(f"Error parsing product JSON for {product['url']}: {json_err}")
                return None

        # Fallback parsing if JSON method fails
        logging.warning(f"Could not find product details JSON for {product['url']}")
        return None

    except requests.RequestException as e:
        logging.error(f"Error fetching product details for {product['url']}: {e}")
        return None


def save_stock_data(product_details):
    """Save stock data to a single CSV file."""
    csv_file = CSV_FILE
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            product_details['id_product'],
            product_details['category'],
            product_details['name'],
            product_details['stock_quantity'],
            product_details['quantity_all_version'],  # Added quantity_all_version
            product_details['price'],
            product_details['price_without_reduction']
        ])


def plot_stock_data(id_product):
    """Generate a line plot of stock levels over time."""
    csv_file = CSV_FILE
    if not os.path.exists(csv_file):
        logging.warning(f"No data to plot for Product ID: {id_product}")
        return

    # Read CSV data with explicit encoding and error handling
    try:
        df = pd.read_csv(csv_file, encoding='utf-8', encoding_errors='replace')
        df = df[df['id_product'] == id_product]  # Filter by Product ID
        if df.empty:
            logging.warning(f"No data to plot for Product ID: {id_product}")
            return
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Plot both stock quantities
        plt.figure(figsize=(12, 7))

        # Plot regular stock quantity
        plt.plot(df['timestamp'], df['stock_quantity'], marker='o', label='Current Version Stock')

        # Plot quantity_all_version if it exists in the DataFrame
        if 'quantity_all_version' in df.columns:
            plt.plot(df['timestamp'], df['quantity_all_version'], marker='s', linestyle='--',
                     color='green', label='All Versions Stock')

        plt.title(f'Stock Levels for Product ID {id_product}\n{df["name"].iloc[0]}')
        plt.xlabel('Timestamp')
        plt.ylabel('Stock Quantity')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save plot with product ID sanitized for filename
        safe_id = re.sub(r'[^\w\-]', '_', str(id_product))[:100]
        plot_file = os.path.join(PLOT_DIR, f'{safe_id}_stock_plot.png')
        plt.savefig(plot_file)
        plt.close()
        logging.info(f"Plot saved: {plot_file}")
    except Exception as e:
        logging.error(f"Error plotting stock data for Product ID {id_product}: {e}")


def monitor_stocks():
    """Main function to monitor stock levels."""
    logging.info("Starting monitor_stocks...")
    setup_directories()
    initialize_csv()
    logging.info("Directories created: stock_data, stock_plots")

    # Create session
    session = requests.Session()

    # Get all products
    logging.info("Collecting products...")
    products = get_all_products(session)
    if not products:
        logging.error("No products found. Exiting.")
        return
    logging.info(f"Collected {len(products)} products")

    # Process each product
    for product in products:
        logging.info(f"Processing product: {product['id_product']}")

        # Extract product details
        product_details = extract_product_details(session, product)

        if product_details:
            # Save stock data
            save_stock_data(product_details)

            # Generate plot
            plot_stock_data(product_details['id_product'])

        # Delay between products to avoid overwhelming server
        time.sleep(5)


def main():
    """Schedule the stock monitoring task."""
    # Run immediately
    monitor_stocks()

    # Schedule to run every 2 hours
    schedule.every(3).hours.do(monitor_stocks)

    logging.info("Starting scheduler. Script will run every 2 hours. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()