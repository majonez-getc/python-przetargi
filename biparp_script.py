# biparp_script.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Enables headless mode for the browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def process_page(driver, keywords):
    results1 = []
    articles = driver.find_elements(By.CLASS_NAME, "art_list")

    for article in articles:
        title_element = article.find_element(By.CSS_SELECTOR, ".lewy a")
        title = title_element.text.strip()
        link = title_element.get_attribute("href")

        if any(keyword.lower() in title.lower() for keyword in keywords):
            results1.append([title, link, "BIPARP"])

    return results1

def fetch_biparp_results(keywords):
    driver = setup_driver()
    driver.get("https://arp.bip.gov.pl/articles/index/zamowienia-strefowe/page:1")

    results = []

    while True:
        print("BIARP")
        results.extend(process_page(driver, keywords))

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.next")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Wait for the page to load
        except:
            break

    driver.quit()

    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
