# oneplace_script.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_oneplace_results(keywords):
    url = "https://oneplace.marketplanet.pl/zapytania-ofertowe-przetargi/-/rfp/cat/11035/elektroenergetyka?_7_WAR_organizationnoticeportlet_cur=1"
    keywords = [kw.strip().lower() for kw in keywords]
    driver = setup_driver()
    driver.get(url)
    results = []

    while True:
        try:
            # Wait for the tiles to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.tiles"))
            )

            articles = driver.find_elements(By.CSS_SELECTOR, "div.row.tiles article")

            for article in articles:
                print("ONEPLACE")
                title_element = article.find_element(By.CSS_SELECTOR, "h3.title")
                title = title_element.text.strip()
                link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                if any(keyword in title.lower() for keyword in keywords):
                    results.append([title, link, 'oneplace'])

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            except:
                print("No more pages or an error occurred: ending processing.")
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    driver.quit()

    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
