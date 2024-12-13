# orlen_script.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_orlen_results(keywords):
    url = "https://connect.orlen.pl/servlet/HomeServlet?"
    driver = setup_driver()
    driver.get(url)

    while True:
        try:
            # Click "Pokaż więcej" if visible
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link-btn.link-load-more"))
            )
            show_more_button.click()
            time.sleep(3)  # Wait for new content to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            break

    results = []
    items = driver.find_elements(By.CSS_SELECTOR, "section.demand-item")
    
    for item in items:
        title_element = item.find_element(By.CSS_SELECTOR, "a.demand-item-details-name")
        title = title_element.text
        link = title_element.get_attribute('href')
        for keyword in keywords:
            if keyword.lower() in title.lower():
                results.append([title, link, 'orlen'])
                break

    driver.quit()

    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
