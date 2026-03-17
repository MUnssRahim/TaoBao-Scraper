import os
import random
import json
import time
import requests
import mysql.connector
import time
from playwright.sync_api import sync_playwrightimport 
import webbrowser

from PIL import Image
import time, io, pickle, 
from datetime import datetime


from urllib.parse import urlparse



import os
import platform

import os
import platform

click_count = 0  # Global variable to keep track of which link to click


def save_cookies(context, user_id):
    filename = f"{user_id}_taobao_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    with open(filename, "wb") as f:
        pickle.dump(context.cookies(), f)
    print("🍪 Cookies saved to:", filename)


def wait_for_login_success(page):
    print("⏳ Waiting for login confirmation...")
    for _ in range(90):
        try:
            user_span = page.query_selector(
                "#icestarkNode > div > div:nth-child(1) > div > div.personal--Y6wRcg83 > div.accountInfo--nT8rs6G2 > div.name--PChlIH2F > span"
            )
            if user_span:
                user_id = user_span.inner_text()
                print("✅ Logged in as:", user_id)
                return user_id
        except:
            pass
        time.sleep(1)
    print("❌ Login not confirmed.")
    return None




def qr_login(page):
    try:
        page.wait_for_selector("#qrcode-img")
        canvas = page.query_selector("#qrcode-img > canvas")
        if not canvas:
            print("❌ QR canvas not found.")
            return None

        qr_bytes = canvas.screenshot()
        img = Image.open(io.BytesIO(qr_bytes))
        img.show()
        print("📱 Scan QR with Taobao app...")

        return wait_for_login_success(page)
    except Exception as e:
        print("❌ QR login error:", e)
        return None


def log_login(user_id, method, account_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = (
        f"[{timestamp}] Logged in via {method} as: {user_id} | "
        f"Account Type: {'New' if account_type == 'y' else 'Old'}\n"
    )
    with open("logins.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
    print("📝 Login logged to logins.txt")


def list_saved_cookies():
    import os
    cookies = [f for f in os.listdir() if f.endswith("_taobao_cookies.pkl")]
    if not cookies:
        print("🗂️ No saved accounts found.")
    else:
        print("🧾 Saved Accounts:")
        for idx, file in enumerate(cookies):
            print(f"{idx + 1}. {file}")
    return cookies


def login_with_cookies(context, page, cookies_file):
    try:
        with open(cookies_file, "rb") as f:
            cookies = pickle.load(f)
        context.add_cookies(cookies)
        open_taobaomain(page)
        user_id = wait_for_login_success(page)
        if user_id:
            print(f"✅ Logged in using saved cookies as: {user_id}")
            return user_id
    except Exception as e:
        print("❌ Failed to login using cookies:", e)
    return None


def count_logged_in_accounts():
    try:
        with open("logins.txt", "r", encoding="utf-8") as f:
            logins = f.readlines()

        logged_in_accounts = set()
        print("\n📜 Login History:")
        for entry in logins:
            if "Logged in as:" in entry:
                timestamp = entry.split("[")[1].split("]")[0]
                method = entry.split("via")[1].split("as:")[0].strip()
                user_id = entry.split("Logged in as:")[1].split(" |")[0].strip()
                account_type = "New" if "New" in entry else "Old"
                print(f"Time: {timestamp} | Method: {method} | Account: {user_id} | Account Type: {account_type}")

        print(f"\n🎉 Total distinct accounts logged in: {len(logged_in_accounts)}")
    except FileNotFoundError:
        print("❌ No login records found in logins.txt")







def open_taobaomain(page):
    main_url = "https://www.taobao.com/"
    try:
        if not page:
            print(" Page object is None!")
            return
        try:
            page.goto(main_url)  # Timeout set to 60 seconds
            page.wait_for_load_state('load')
            print(" Taobao main page opened")
        except Exception as e:
            print(f" Error navigating to Taobao main page: {e}")
    except Exception as e:
        print(f" Error opening Taobao main page: {e}")





def ensure_download_folders():
    windows_folder = os.path.join(os.getcwd(), "downloads_windows")
    linux_folder = os.path.join(os.getcwd(), "downloads_linux")

    os.makedirs(windows_folder, exist_ok=True)
    os.makedirs(linux_folder, exist_ok=True)

    return windows_folder, linux_folder


def get_file_extension(url):
    """Get the file extension from the URL."""
    return os.path.splitext(url)[1]

def download_image(url, product_title, image_type="main", retries=3, delay=5):
    """Download and save the image with a unique filename on both Windows and Linux servers."""
    windows_folder, linux_folder = ensure_download_folder()
    timestamp = int(time.time())  # Unique timestamp
    clean_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in product_title)
    
    file_extension = get_file_extension(url)  # Get the correct extension
    filename = f"{clean_title}_{image_type}_{timestamp}{file_extension}"

    # File paths for Windows and Linux
    windows_filepath = os.path.join(windows_folder, filename)
    linux_filepath = os.path.join(linux_folder, filename)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Save on Windows
                try:
                    with open(windows_filepath, 'wb') as file:
                        file.write(response.content)
                except Exception as e:
                    print(f" Error saving image on Windows: {e}")

                # Save on Linux
                try:
                    with open(linux_filepath, 'wb') as file:
                        file.write(response.content)
                    print(f" Image downloaded: {windows_filepath} & {linux_filepath}")
                except Exception as e:
                    print(f" Error saving image on Linux: {e}")
                return  # Exit once the download and save are successful

            elif response.status_code == 420:
                print(f"Attempt {attempt+1}: Rate-limiting detected. Retrying in {delay} seconds...")
                time.sleep(delay)  # Retry after a delay
            else:
                print(f"Failed to download {filename}: HTTP {response.status_code}")
                return

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
            time.sleep(delay)  # Wait before retrying

    print(f"Failed to download {filename} after {retries} attempts.")


import time

def load_products(page):
    scroll_attempts = 0
    products_loaded = 0

    while scroll_attempts < 15:
        try:
           
            page.evaluate("window.scrollBy(0, 170);")
            time.sleep(3)

            # Get products
            product_elements = page.query_selector_all(".item-link")
            new_products_loaded = len(product_elements)
            print("🧾 Products loaded so far:", new_products_loaded)

            # Check if more products are loaded
            if new_products_loaded > products_loaded:
                products_loaded = new_products_loaded
                scroll_attempts = 0  # Reset if new content appears
            else:
                scroll_attempts += 1

            # Optional: scroll back up slightly every 10 scrolls to trigger lazy loads
            if scroll_attempts % 10 == 0:
                page.evaluate("window.scrollBy(0, -50);")
                time.sleep(1)

        except Exception as e:
            print("⚠️ Error during scrolling:", e)
            break

    print("✅ Finished loading products.")

def scrape_product(page, product_url):
    product_data = {"Product URL": product_url}
    try:
        try:
            page.goto(product_url)
            time.sleep(random.uniform(5, 7))
        except Exception as e:
            print(f" Error navigating to product page: {e}")
            return None

        try:
            product_data["Title"] = page.query_selector("E7gD8doUq1--ItemTitle--_34597b1").inner_text().strip()
        except Exception as e:
            print(f" Failed to get title: {e}")
            product_data["Title"] = "N/A"

        try:
            price_container = page.query_selector("shadow-ecotext E7gD8doUq1--text--ca3dd73c")
            spans = price_container.query_selector_all("span")
            product_data["Price Details"] = spans[1].inner_text().strip() if len(spans) > 1 else "N/A"
        except Exception as e:
            product_data["Price Details"] = "N/A"
            print(f" Failed to get price: {e}")

        try:
            main_image_url = page.query_selector("E7gD8doUq1--mainPic--_8729489").get_attribute("src")
            product_data["Main Image URL"] = main_image_url
            download_image(main_image_url, f"{product_data['Title']}_main.jpg")
        except Exception as e:
            product_data["Main Image URL"] = "N/A"
            print(f" Failed to get main image URL: {e}")

        try:
            thumbnails = page.query_selector_all(".E7gD8doUq1--thumbnail--e3bf7146")
            more_images = [thumb.query_selector("img").get_attribute("src") for thumb in thumbnails if thumb.query_selector("img")]
            product_data["More Image URLs"] = "; ".join(more_images) if more_images else "N/A"

            for i, img_url in enumerate(more_images):
                download_image(img_url, f"{product_data['Title']}_more_{i+1}.jpg")
        except Exception as e:
            product_data["More Image URLs"] = "N/A"
            print(f" Failed to retrieve more image URLs: {e}")

        try:
            category_elements = page.query_selector_all(".E7gD8doUq1--valueItem--ee898cc0")
            category_images = [
                {
                    "Category Text": category.inner_text().strip(),
                    "Category Image URL": category.query_selector("img").get_attribute("src") if category.query_selector("img") else "N/A"
                }
                for category in category_elements
            ]
            product_data["Categories & Images"] = category_images if category_images else "N/A"
        except Exception as e:
            product_data["Categories & Images"] = "N/A"
            print(f" Failed to retrieve category images: {e}")
        
    except Exception as e:
        print(f" Error scraping product {product_url}: {e}")
        return None
    
    return product_data

def save_to_json(new_data):
    """ Save product data to JSON on both Windows and Linux systems. """
    try:
        windows_folder = "C:/Users/HP/Desktop/taobao_images"
        linux_folder = "/root/taobao_images"

        windows_filename = os.path.join(windows_folder, "taobao_products.json")
        linux_filename = os.path.join(linux_folder, "taobao_products.json")

        
        try:
            if not os.path.exists(windows_folder):
                os.makedirs(windows_folder)
            if not os.path.exists(linux_folder):
                os.makedirs(linux_folder)
        except Exception as e:
            print(f" Error ensuring folder exists: {e}")

      
        try:
            with open(windows_filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        
        data.append(new_data)

        
        try:
            with open(windows_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f" Product saved on Windows: {new_data['Title']}")
        except Exception as e:
            print(f" Error saving to Windows JSON: {e}")

        # Save the updated data to Linux JSON
        try:
            with open(linux_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f" Product saved on Linux: {new_data['Title']}")
        except Exception as e:
            print(f" Error saving to Linux JSON: {e}")

    except Exception as e:
        print(f" Error saving to JSON: {e}")

from datetime import datetime
import time

def click_next_link(page):
    global click_count
    try:
        elements = page.query_selector_all(".cate-content-href--HI8wwRts")

        if click_count < len(elements):
            element = elements[click_count]
            element.scroll_into_view_if_needed()
            element.click()

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f" Clicked category {click_count + 1}/{len(elements)} at {current_time}")
            
            # Wait for page to load: this waits for product items to appear
            try:
                page.wait_for_selector(".item-link", timeout=15000)  # 15 sec max
                print(" Category page loaded.")
            except:
                print(" Timeout: Category page may not have fully loaded.")

            click_count += 1
        else:
            print(" No more categories to click.")
    except Exception as e:
        print(f" Error clicking category: {e}")
def click_next_button(page):
    """Click the 'next' button repeatedly with a 10-second delay between clicks."""
    while True:
        try:
            
            next_button = page.query_selector(".next-btn.next-medium.next-btn-normal.next-pagination-item.next-next")
            
            if next_button:
                next_button.click()  # Click the 'next' button
                print("Clicked 'next' button.")
                time.sleep(10)  # Sleep for 10 seconds before the next click
            else:
                print("Next button not found!")
                break  # Exit the loop if the 'next' button is not found

        except Exception as e:
            print(f"Error during 'next' button click: {e}")
            break  


def scraping_mechanism(page):
    try:
        
        load_products(page)

        try:
            product_urls = page.eval_on_selector_all(".item-link", "elements => elements.map(el => el.href)")
            print(f" Found {len(product_urls)} products on page.")
        except Exception as e:
            print(f" Error getting product URLs: {e}")
            return

        
        for url in product_urls:
            time.sleep(random.uniform(3, 7))

            product_data = scrape_product(page, url)
            if product_data:
                save_to_json(product_data)
                print("Saved to json")
    except Exception as e:
        print(f" Error during scraping mechanism: {e}")






proxies = [
    
]


def get_random_proxy():
    return random.choice(proxies)

def main():
    browser = None
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)
            except Exception:
                try:
                    browser = p.firefox.launch(headless=False)
                except Exception:
                    try:
                        browser = p.webkit.launch(headless=False)
                    except Exception as e:
                        print(f"Failed to launch any browser: {e}")
                        return


            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                
            )

            page = context.new_page()

            print("""===============================
   🛒 Taobao Login Options
===============================
1. Login as New Account
2. Use Existing Account (Saved Cookies)
""")
            acc_choice = input("🔘 Choose account type (1=New / 2=Old): ").strip()
            user_id = None

            if acc_choice == "1":
                page.goto("https://login.taobao.com/")
                time.sleep(2)

                print("""===============================
    🛂 Login Methods
===============================
1. QR Code Login
""")
                choice = input("📌 Choose login method (1): ").strip()

                if choice == "1":
                    user_id = qr_login(page)
                    method = "QR Code"
                else:
                    print("❌ Invalid login method.")
                    browser.close()
                    return

                if user_id:
                    save_cookies(context, user_id)
                    log_login(user_id, method, "y")
                    print(f"🎉 Logged in successfully as: {user_id} (New Account)")

                    # START MAINPAGE + SCRAPE AFTER NEW LOGIN
                    open_taobaomain(page)
                    for _ in range(42):
                        click_next_link(page)
                        scraping_mechanism(page)
                        for _ in range(100):
                            try:
                                click_next_button(page)
                                scraping_mechanism(page)
                            except Exception as e:
                                print(f"Error during iteration: {e}")
                                break

                else:
                    print("❌ Login failed.")

            elif acc_choice == "2":
                cookies = list_saved_cookies()
                if not cookies:
                    browser.close()
                    return

                index = int(input("🔢 Enter account number to use: ").strip()) - 1
                if 0 <= index < len(cookies):
                    cookies_file = cookies[index]
                    user_id = login_with_cookies(context, page, cookies_file)
                    if user_id:
                        print(f"🎉 Logged in using saved account: {user_id}")
                        
                        
                        open_taobaomain(page)
                        for _ in range(42):
                            click_next_link(page)
                            for _ in range(100):
                                try:
                                    click_next_button(page)
                                except Exception as e:
                                    print(f"Error during iteration: {e}")
                                    break
                    else:
                        print("❌ Failed to login with selected cookies.")
                else:
                    print("❌ Invalid selection.")

            else:
                print("❌ Invalid choice.")

            count_logged_in_accounts()

    except Exception as e:
        print(f" Error launching Playwright: {e}")

    finally:
        try:
           if browser:
                browser.close()
        except Exception as e:
         print("Couldn't close browser properly:", e)

if __name__ == "__main__":
    main() 