import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Function to initialize WebDriver
def get_driver():
    user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 120)}.0.0.0 Safari/537.36"
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # ❌ No headless mode (ensures normal Chrome window opens)
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to wait for products to load
def wait_for_products(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "item-link"))
        )
        print("✅ Products fully loaded!")
    except TimeoutException:
        print("⚠️ Timeout! Some products might not have loaded completely.")

# Function to scroll and wait for new products
def scroll_and_wait(driver):
    last_count = 0
    max_scroll_attempts = 25
    scroll_attempts = 0
    scroll_number = 0  # Counter for scroll attempts

    while scroll_attempts < max_scroll_attempts:
        scroll_number += 1
        print(f"🌀 Scrolling... Attempt {scroll_number}")

        # Scroll down step by step
        for _ in range(10):
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(random.uniform(1, 2))

        time.sleep(3)  # Wait for new products to load
        
        # Click "Load More" button if available
        try:
            load_more_button = driver.find_element(By.CLASS_NAME, "load-more-button")
            if load_more_button.is_displayed():
                print("🖱️ Clicking 'Load More' button...")
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(6)
        except NoSuchElementException:
            pass  # Continue if no button is found

        # Check if new products have loaded
        products = driver.find_elements(By.CLASS_NAME, "item-link")
        new_count = len(products)

        if new_count > last_count:
            scroll_attempts = 0  # Reset attempts if new products are found
        else:
            scroll_attempts += 1  # Increment if no new products load

        last_count = new_count
        print(f"🔄 Scroll {scroll_number} - Products found: {new_count}")

    print(f"✅ Fully scrolled. {len(products)} products detected.")

# Function to scrape product details
def scrape_products(category_url):
    driver = get_driver()
    
    try:
        driver.get(category_url)
        time.sleep(5)  # Wait for the page to load

        print(f"\n🔍 Scraping Category: {category_url}")

        wait_for_products(driver)
        scroll_and_wait(driver)

        products = driver.find_elements(By.CLASS_NAME, "item-link")

        all_products = []
        for product in products:
            product_url = product.get_attribute("href")

            img_element = product.find_element(By.CLASS_NAME, "product-img") if product.find_elements(By.CLASS_NAME, "product-img") else None
            img_url = img_element.get_attribute("src") if img_element else "No Image"

            title_element = product.find_element(By.CLASS_NAME, "info-wrapper-title-text") if product.find_elements(By.CLASS_NAME, "info-wrapper-title-text") else None
            title = title_element.text.strip() if title_element else "No Title"

            price_element = product.find_element(By.CLASS_NAME, "price-value") if product.find_elements(By.CLASS_NAME, "price-value") else None
            price = price_element.text.strip() if price_element else "N/A"
            
            # ✅ Fix: Get actual monthly sale text
            monthly_sale_element = product.find_element(By.CLASS_NAME, "month-sale") if product.find_elements(By.CLASS_NAME, "month-sale") else None
            monthly_sale = monthly_sale_element.text.strip() if monthly_sale_element else "N/A"

            all_products.append({
                "Category URL": category_url,
                "Product": title,
                "URL": product_url,
                "Image": img_url,
                "Price": f"¥{price}",
                "MonthlySale": monthly_sale,  # ✅ Fixed missing comma & correct extraction
            })

        print(f"✅ Finished scraping {category_url}. Found {len(all_products)} products.\n")
        return all_products

    except Exception as e:
        print(f"⚠️ Error scraping {category_url}: {e}")
        return []

    finally:
        driver.quit()

# Start scraping
url = "https://www.taobao.com/"  # Replace with actual Taobao category page
print("\n🔍 Scraping Default Taobao Page...")
all_products = scrape_products(url)

# Save to JSON
with open("taobao_products.json", "w", encoding="utf-8") as json_file:
    json.dump(all_products, json_file, indent=4, ensure_ascii=False)

print("✅ All data saved to taobao_products.json")
