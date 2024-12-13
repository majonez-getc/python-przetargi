# biznespolska_script.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to run the browser in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def contains_keywords(title, keywords):
    return any(keyword.lower() in title.lower() for keyword in keywords)

def fetch_biznespolska_results(keywords):
    url = 'https://www.biznes-polska.pl/oferty/'

    driver = setup_driver()
    driver.get(url)

    results = []
    page_number = 1

    while True:
        print("Biznespolska")
        print(f"Processing page {page_number}")
        try:
            # Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
            )

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            for row in rows:
                try:
                    title_element = row.find_element(By.CSS_SELECTOR, "a.title.show-more-title")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    if contains_keywords(title, keywords):
                        results.append([title, link])
                except Exception as e:
                    print(f"An error occurred while processing a row: {e}")
                    continue

            # Check if there is a "Next" button and click it
            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.next")
            if next_buttons and next_buttons[0].is_displayed():
                driver.execute_script("arguments[0].click();", next_buttons[0])
                page_number += 1
                time.sleep(2)  # Wait for the new page to load
            else:
                break

        except Exception as e:
            print(f"No more pages or an error occurred: {e}")
            break

    driver.quit()

    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
