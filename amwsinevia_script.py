# amwsinevia_script.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_amwsinevia_results(keywords):
    driver = setup_driver()
    driver.get('https://amwsinevia.eb2b.com.pl/open-auctions.html')

    time.sleep(5)

    try:
        # Accept cookies if the button exists
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span#button-1014-btnInnerEl"))
            )
            accept_button.click()
            print("Clicked on accept cookies button.")
        except (NoSuchElementException, TimeoutException) as e:
            print("No accept cookies button found or an error occurred:", e)

        time.sleep(5)

        results = []
        page = 1
        last_first_row_text = None

        while True:
            print(f"Processing page {page}")

            rows = driver.find_elements(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr")
            print(f"Found {len(rows)} rows on the current page.")

            if rows:
                current_first_row_text = rows[1].text
                if current_first_row_text == last_first_row_text:
                    print("Reached the end of pages.")
                    break
                last_first_row_text = current_first_row_text

            for row in rows:
                try:
                    title_element = row.find_element(By.XPATH, ".//td[5]/div/a")
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    status_element = row.find_element(By.XPATH, ".//td[15]/div")
                    status = status_element.text
                    if "Etap składania ofert" in status and any(keyword.lower() in title.lower() for keyword in keywords):
                        results.append([title, link, 'amwsinevia'])
                except NoSuchElementException:
                    print("No title element found in this row.")

            try:
                next_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/div/div/div[7]/em/button/span[2]")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)
                page += 1
            except NoSuchElementException:
                print("No more pages.")
                break

        # Return the results to the main script
        return results

    finally:
        driver.quit()

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
