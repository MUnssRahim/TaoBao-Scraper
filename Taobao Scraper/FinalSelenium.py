from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os
import random
import json
import time 
import requests
import _mysql_connector
import json
import os
import time
import random
import requests
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service  



from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
import shutil
import tempfile

import time
import tempfile
from playwright.sync_api import sync_playwright

def init_driver():
    try:
        # Try to initialize with Playwright Chromium first
        print("Initializing Chromium with Playwright...")
        print("Test2 ✅ ✅ ✅ ✅ ✅ ✅ ✅")
        
        # Create a temporary directory for user data to avoid conflicts
        temp_dir = tempfile.mkdtemp(prefix=f"chrome_{int(time.time())}_")

        # Launch Chromium using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=[
                '--incognito',  # Open in incognito mode
                '--disable-extensions',  # Disable extensions
                '--disable-notifications',  # Disable notifications
                '--no-sandbox',  # Disable sandboxing (use with caution)
                '--disable-dev-shm-usage',  # Solve potential issues with shared memory
                '--disable-gpu',  # Disable GPU acceleration
                f'--user-data-dir={temp_dir}',  # Use temp directory for user data
                '--remote-debugging-port=9222',  # For debugging if necessary
            ])
            
            # Create a new page and navigate to the desired URL
            page = browser.new_page()
            print("✅ Chromium initialized successfully with Playwright")

            # Return the page object so it can be used for interactions
            return page

    except Exception as e:
        print(f"Error initializing Chromium with Playwright: {e}")
        print("Failed to initialize Chromium. Exiting...")
        return None

# Usage example (calling the function)


   


# Global click count


# Initialize WebDriver


def open_taobaologin(driver_instance):
    login_url = "https://login.taobao.com"
    driver_instance.get(login_url)
    print("✅ Taobao login page opened")

# Wait for 40 seconds
    

# Now open the main Taobao page
def open_taobaomain(driver_instance):  
    main_url = "https://www.taobao.com"
    driver_instance.get(main_url)
    print("✅ Taobao main page opened")

def ensure_download_folder():
    """ Ensure the download folder exists on both Windows and Linux server. """
    windows_folder = "C:/Users/HP/Desktop/taobao_images"
    linux_folder = "/root/taobao_images"

    # Create folder on Windows
    if not os.path.exists(windows_folder):
        os.makedirs(windows_folder)

    # Create folder on Linux
    if not os.path.exists(linux_folder):
        os.makedirs(linux_folder)

    return windows_folder, linux_folder

def download_image(url, product_title, image_type="main"):
    """ Download and save the image with a unique filename on both Windows and Linux servers. """
    windows_folder, linux_folder = ensure_download_folder()
    timestamp = int(time.time())  # Unique timestamp
    clean_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in product_title)
    filename = f"{clean_title}_{image_type}_{timestamp}.jpg"

    # Save on Windows
    windows_filepath = os.path.join(windows_folder, filename)

    # Save on Linux
    linux_filepath = os.path.join(linux_folder, filename)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Save on Windows
            with open(windows_filepath, 'wb') as file:
                file.write(response.content)

            # Save on Linux
            with open(linux_filepath, 'wb') as file:
                file.write(response.content)

            print(f"✅ Image downloaded: {windows_filepath} & {linux_filepath}")
        else:
            print(f"❌ Failed to download {filename}: {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

def load_products(driver_instance):
    scroll_attempts = 0
    products_loaded = 0

    while scroll_attempts < 15:
        driver_instance.execute_script("window.scrollBy(0, 170);")
        time.sleep(3)
        
        product_elements = driver_instance.find_elements(By.CLASS_NAME, "item-link")
        new_products_loaded = len(product_elements)
        print("Products loaded uptill",new_products_loaded)
        
        if new_products_loaded > products_loaded:
            products_loaded = new_products_loaded
            scroll_attempts = 0  
        else:
            scroll_attempts += 1  
            
    print(f"✅ Page fully loaded. {products_loaded} products loaded.")

def scrape_product(driver_instance, product_url):
    driver_instance.get(product_url)
    time.sleep(random.uniform(5, 7))
    
    product_data = {"Product URL": product_url}

    try:
        product_data["Title"] = driver_instance.find_element(By.CSS_SELECTOR, "#tbpc-detail-item-title").text.strip()
    except:
        print(f"❌ Product failed to load: {product_url}")
        return None
    
    try:
        price_container = driver_instance.find_element(By.CSS_SELECTOR, "div[data-additional-module='true']")
        spans = price_container.find_elements(By.TAG_NAME, "span")
        product_data["Price Details"] = spans[1].text.strip() if len(spans) > 1 else "N/A"
    except:
        product_data["Price Details"] = "N/A"

    try:
        main_image_url = driver_instance.find_element(By.CLASS_NAME, "E7gD8doUq1--mainPic--_8729489").get_attribute("src")
        product_data["Main Image URL"] = main_image_url
        download_image(main_image_url, f"{product_data['Title']}_main.jpg")
    except:
        product_data["Main Image URL"] = "N/A"

    try:
        thumbnails = driver_instance.find_elements(By.CLASS_NAME, "E7gD8doUq1--thumbnail--e3bf7146")
        more_images = [thumb.find_element(By.TAG_NAME, "img").get_attribute("src") for thumb in thumbnails if thumb.find_elements(By.TAG_NAME, "img")]
        product_data["More Image URLs"] = "; ".join(more_images) if more_images else "N/A"

        for i, img_url in enumerate(more_images):
            download_image(img_url, f"{product_data['Title']}_more_{i+1}.jpg")
    except Exception as e:
        product_data["More Image URLs"] = "N/A"
        print(f"❌ Failed to retrieve more image URLs: {e}")

    try:
        category_elements = driver_instance.find_elements(By.CLASS_NAME, "E7gD8doUq1--valueItem--ee898cc0")
        category_images = [
            {
                "Category Text": category.text.strip(),
                "Category Image URL": category.find_element(By.TAG_NAME, "img").get_attribute("src") if category.find_elements(By.TAG_NAME, "img") else "N/A"
            }
            for category in category_elements
        ]
        
        product_data["Categories & Images"] = category_images if category_images else "N/A"
    except Exception as e:
        product_data["Categories & Images"] = "N/A"
        print(f"❌ Failed to retrieve category images: {e}")
    
    return product_data

def save_to_json(new_data):
    """ Save product data to JSON on both Windows and Linux systems. """
    # Define file paths for both systems
    windows_folder = "C:/Users/HP/Desktop/taobao_images"
    linux_folder = "/root/taobao_images"
    
    windows_filename = os.path.join(windows_folder, "taobao_products.json")
    linux_filename = os.path.join(linux_folder, "taobao_products.json")

    # Ensure both directories exist
    if not os.path.exists(windows_folder):
        os.makedirs(windows_folder)
    if not os.path.exists(linux_folder):
        os.makedirs(linux_folder)

    # Load existing data from Windows JSON
    try:
        with open(windows_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Append new product data to the list
    data.append(new_data)

    # Save the updated data to Windows JSON
    with open(windows_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Product saved on Windows: {new_data['Title']}")

    # Save the updated data to Linux JSON
    with open(linux_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Product saved on Linux: {new_data['Title']}")

def save_to_mysql():
    # MySQL database connection
    conn = mysql.connector.connect(
        host="",
        user="",
        password="",
        database="taobao_scraper"
    )
    cursor = conn.cursor()

    # Ensure directory paths exist on both systems
    windows_folder = "C:/Users/HP/Desktop/taobao_images"
    linux_folder = "/root/taobao_images"
    
    windows_filename = os.path.join(windows_folder, "taobao_products.json")
    linux_filename = os.path.join(linux_folder, "taobao_products.json")

    # Load product data from Windows JSON
    try:
        with open(windows_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Insert data from Windows JSON to MySQL
    for product in data:
        # Handle the categories and more images if they exist
        categories_images = json.dumps(product.get("Categories & Images", []))
        more_image_urls = product.get("More Image URLs", "N/A")

        cursor.execute("""
            INSERT INTO Products (Product_URL, Title, Price_Details, Main_Image_URL, More_Image_URLs, Categories_Images)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            product["Product URL"],
            product["Title"],
            product["Price Details"],
            product.get("Main Image URL", "N/A"),
            more_image_urls,
            categories_images
        ))
    
    # Load product data from Linux JSON
    try:
        with open(linux_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Insert data from Linux JSON to MySQL
    for product in data:
        # Handle the categories and more images if they exist
        categories_images = json.dumps(product.get("Categories & Images", []))
        more_image_urls = product.get("More Image URLs", "N/A")

        cursor.execute("""
            INSERT INTO Products (Product_URL, Title, Price_Details, Main_Image_URL, More_Image_URLs, Categories_Images)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            product["Product URL"],
            product["Title"],
            product["Price Details"],
            product.get("Main Image URL", "N/A"),
            more_image_urls,
            categories_images
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Data saved to MySQL from both Windows and Linux JSON files.")
def click_next_link(driver_instance):
    global click_count
    try:
        elements = driver_instance.find_elements(By.CLASS_NAME, "cate-content-href--HI8wwRts")
        if click_count < len(elements):
            element = elements[click_count]
            actions = ActionChains(driver_instance)
            actions.move_to_element(element).perform()
            element.click()
            print(f"✅ Clicked category {click_count + 1}/{len(elements)}")
            time.sleep(15)
            click_count += 1
        else:
            print("❌ No more categories to click.")
    except Exception as e:
        print(f"❌ Error clicking category: {e}")

def scraping_mechanism(driver_instance):
    load_products(driver_instance)
    product_urls = [el.get_attribute("href") for el in driver_instance.find_elements(By.CLASS_NAME, "item-link")]
    print(f"🔄 Found {len(product_urls)} products on page.")

    for url in product_urls:
        product_data = scrape_product(driver_instance, url)
        if product_data:
            save_to_json(product_data)
            print("Saved to json")

    save_to_mysql()

def main():
    driver = init_driver()
    open_taobaologin(driver)
    print("You have 40 seconds until to login")
    time.sleep(40)
    
    open_taobaomain(driver)
    scraping_mechanism(driver)
    
    for _ in range(30):
        open_taobaomain(driver)
        click_next_link(driver)
        scraping_mechanism(driver)
    
    driver.quit()  # Make sure to close the driver at the end

if __name__ == "__main__":
    main()
