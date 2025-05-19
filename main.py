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
    "https://www.minimx.fr/fr/678-nos-motocross",
]
CATEGORY_URLS = list(dict.fromkeys(CATEGORY_URLS))

# Directory to store CSV files and plots
DATA_DIR = 'stock_data'
PLOT_DIR = 'stock_plots'


def get_dated_filename():
    """Create filename with current date and time for CSV and plot directory."""
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H-%M-%S')
    csv_file = os.path.join(DATA_DIR, f'stock_data_{current_date}_{current_time}.csv')
    plot_subdir = os.path.join(PLOT_DIR, f'{current_date}_{current_time}')
    return csv_file, plot_subdir


def setup_directories():
    """Create directories for data and plots if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PLOT_DIR, exist_ok=True)

    # Create date-specific subdirectory for plots
    _, plot_subdir = get_dated_filename()
    os.makedirs(plot_subdir, exist_ok=True)


def create_new_csv():
    """Create a new CSV file for all products with current date and time in name."""
    csv_file, _ = get_dated_filename()
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['timestamp', 'id_product', 'category', 'name', 'stock_quantity', 'quantity_all_versions', 'price',
             'price_without_reduction'])
    logging.info(f"Created new CSV file: {csv_file}")
    return csv_file


def get_product_links(session, category_url):
    """Extract product links from a category page, handling pagination."""
    product_links = []
    page = 1
    max_pages = 20  # Safety limit to prevent infinite loops
    previous_page_products = set()  # To detect when we're getting the same products repeatedly

    while page <= max_pages:
        url = f"{category_url}?page={page}" if page > 1 else category_url
        try:
            logging.info(f"Fetching page {page} of {category_url}")
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

            # Check if we're on the last page by looking for pagination controls
            pagination = soup.select_one('.pagination')
            if pagination:
                # If the "next" button is disabled or doesn't exist, we're on the last page
                next_disabled = pagination.select_one('.next.disabled') or not pagination.select_one('.next')
                if next_disabled:
                    logging.info(f"Reached last page ({page}) for {category_url}")

            # Collect product IDs from this page
            current_page_products = set()
            current_page_links = []

            for product in products:
                href = product.get('href')
                if href and '/fr/' in href and 'index.php' not in href:
                    # Extract product ID from URL (e.g., /fr/quad/123-product1.html)
                    product_id = re.search(r'/(\d+)-', href)
                    product_id = product_id.group(1) if product_id else None
                    if product_id:
                        current_page_products.add(product_id)
                        current_page_links.append({
                            'url': href,
                            'id_product': product_id,
                            'category': category_url
                        })

            # If we got the same products as the previous page, we're in a loop
            if current_page_products and current_page_products == previous_page_products:
                logging.warning(
                    f"Detected duplicate products on page {page} of {category_url}, breaking pagination loop")
                break

            # Check if the current page has the same number of products as page 1
            # This might indicate the site is showing page 1 content for all requested pages
            if page > 1 and len(current_page_products) == len(previous_page_products) and all(
                    pid in previous_page_products for pid in current_page_products):
                logging.warning(
                    f"Page {page} appears to contain the same products as previous page for {category_url}, stopping pagination")
                break

            # No new products found
            if not current_page_links:
                logging.info(f"No new products found on page {page} of {category_url}")
                break

            # Add current page products to our collection
            product_links.extend(current_page_links)
            previous_page_products = current_page_products

            logging.info(f"Found {len(current_page_links)} products on page {page} of {category_url}")
            page += 1
            time.sleep(5)  # Increased delay to avoid server overload
        except requests.RequestException as e:
            logging.error(f"Error fetching category page {url}: {e}")
            break

    if page > max_pages:
        logging.warning(f"Reached maximum page limit ({max_pages}) for {category_url}")

    logging.info(f"Total of {len(product_links)} products found for {category_url}")
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

                # Extract quantity_all_versions
                quantity_all_versions = product_json.get('quantity_all_versions', 0)

                # Price details
                price = product_json.get('price_amount', 0)  # Changed from 'price' to 'price_amount'
                price_without_reduction = product_json.get('price_without_reduction', price)

                # Logging for verification
                logging.info(f"Product Details - ID: {product['id_product']}, URL: {product['url']}, "
                             f"Stock: {stock_quantity}, All Versions Stock: {quantity_all_versions}, Price: {price}, "
                             f"Price without Reduction: {price_without_reduction}")

                return {
                    'id_product': product['id_product'],
                    'category': product['category'],  # Added category
                    'name': product['url'],  # Use product URL as name
                    'stock_quantity': stock_quantity,
                    'quantity_all_versions': quantity_all_versions,  # Added quantity_all_versions
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


def save_stock_data_batch(all_product_details):
    """Save all collected stock data to a date-specific CSV file."""
    if not all_product_details:
        logging.warning("No product details to save")
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    csv_file, _ = get_dated_filename()

    # Prepare all rows at once
    rows = []
    for product_details in all_product_details:
        rows.append([
            timestamp,
            product_details['id_product'],
            product_details['category'],
            product_details['name'],
            product_details['stock_quantity'],
            product_details['quantity_all_versions'],
            product_details['price'],
            product_details['price_without_reduction']
        ])

    # Append to the newly created file (which already has headers)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write all rows at once
        writer.writerows(rows)

    logging.info(f"Saved {len(rows)} product records to CSV file: {csv_file}")


def plot_stock_data(id_product):
    """Generate a line plot of stock levels over time for all dates."""
    # Get list of all CSV files
    csv_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if
                 f.startswith('stock_data_') and f.endswith('.csv') and f != 'stock_data_master.csv']

    if not csv_files:
        logging.warning(f"No data files found to plot for Product ID: {id_product}")
        return

    # Create a combined dataframe from all CSV files
    all_data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', encoding_errors='replace')
            all_data.append(df)
        except Exception as e:
            logging.error(f"Error reading CSV file {csv_file}: {e}")

    if not all_data:
        logging.warning(f"No valid data found to plot for Product ID: {id_product}")
        return

    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)

    # Filter by product ID
    product_df = combined_df[combined_df['id_product'] == id_product]

    if product_df.empty:
        logging.warning(f"No data to plot for Product ID: {id_product}")
        return

    product_df['timestamp'] = pd.to_datetime(product_df['timestamp'])
    product_df = product_df.sort_values('timestamp')

    # Plot both stock quantities
    plt.figure(figsize=(12, 7))

    # Plot regular stock quantity
    plt.plot(product_df['timestamp'], product_df['stock_quantity'], marker='o', label='Current Version Stock')

    # Plot quantity_all_versions if it exists
    if 'quantity_all_versions' in product_df.columns:
        plt.plot(product_df['timestamp'], product_df['quantity_all_versions'], marker='s', linestyle='--',
                 color='green', label='All Versions Stock')

    # Get the latest product name from any record
    product_name = product_df["name"].iloc[0] if not product_df.empty else "Unknown Product"

    plt.title(f'Stock Levels for Product ID {id_product}\n{product_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('Stock Quantity')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save plot with date and time in filename
    _, plot_subdir = get_dated_filename()
    safe_id = re.sub(r'[^\w\-]', '_', str(id_product))[:100]
    current_time = datetime.now().strftime('%H-%M-%S')
    plot_file = os.path.join(plot_subdir, f'{safe_id}_stock_plot_{current_time}.png')
    plt.savefig(plot_file)
    plt.close()
    logging.info(f"Plot saved: {plot_file}")


def plot_all_stocks(all_product_details):
    """Generate plots for all collected product data."""
    # Extract unique product IDs from the collected data
    product_ids = set(item['id_product'] for item in all_product_details)

    logging.info(f"Generating plots for {len(product_ids)} products")

    # Plot each unique product
    for product_id in product_ids:
        plot_stock_data(product_id)


def monitor_stocks():
    """Main function to monitor stock levels."""
    logging.info("Starting monitor_stocks...")
    setup_directories()

    # Create daily CSV file
    csv_file = create_new_csv()
    logging.info(f"Created new daily CSV file: {csv_file}")

    # Create session
    session = requests.Session()

    # Get all products
    logging.info("Collecting products...")
    products = get_all_products(session)
    if not products:
        logging.error("No products found. Exiting.")
        return
    logging.info(f"Collected {len(products)} products")

    # Collect all product details first
    all_product_details = []
    for product in products:
        logging.info(f"Processing product: {product['id_product']}")

        # Extract product details
        product_details = extract_product_details(session, product)

        if product_details:
            # Add to collection instead of saving immediately
            all_product_details.append(product_details)

        # Delay between products to avoid overwhelming server
        time.sleep(5)

    # Save all collected data to today's file
    logging.info(f"Collecting complete. Saving {len(all_product_details)} product details to daily file")
    save_stock_data_batch(all_product_details)

    # Generate plots for all products
    plot_all_stocks(all_product_details)

    # Also create a master CSV that combines all daily files for easy reference
    create_master_csv()


def create_master_csv():
    """Combine all daily CSV files into a master file."""
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    master_file = os.path.join(DATA_DIR, f'stock_data_master_{current_time}.csv')

    # Get list of all daily CSV files
    csv_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)
                 if f.startswith('stock_data_') and f.endswith('.csv') and not f.startswith('stock_data_master_')]

    if not csv_files:
        logging.warning("No daily CSV files found to create master file")
        return

    # Create dataframes from all files
    all_data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', encoding_errors='replace')
            all_data.append(df)
        except Exception as e:
            logging.error(f"Error reading CSV file {csv_file}: {e}")

    if not all_data:
        logging.warning("No valid CSV data found to create master file")
        return

    # Combine all dataframes and sort by timestamp
    master_df = pd.concat(all_data, ignore_index=True)
    master_df['timestamp'] = pd.to_datetime(master_df['timestamp'])
    master_df = master_df.sort_values(['id_product', 'timestamp'])

    # Save to master file
    master_df.to_csv(master_file, index=False, encoding='utf-8')
    logging.info(f"Created master CSV file: {master_file}")


def main():
    """Schedule the stock monitoring task."""
    monitor_stocks()

    schedule.every(5).hours.do(monitor_stocks)

    logging.info("Starting scheduler. Script will run every 15 minutes. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()