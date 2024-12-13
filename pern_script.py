# pern_script.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # Run the browser in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_pern_results(keywords):
    driver = setup_driver()
    driver.get("https://platformazakupowa.pern.pl/adverts/NonAdvertActs.xhtml")

    results = []

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.ui-datatable-data tr"))
            )
            
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ui-datatable-data tr")
            for row in rows:
                print("PERN")
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    title = cells[1].text
                    for keyword in keywords:
                        if keyword.strip().lower() in title.lower():
                            details_link = cells[-1].find_element(By.TAG_NAME, "a").get_attribute("href")
                            results.append([title, details_link, 'pern'])
                            break
                
            # Click "Next page" button if it exists
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "span.ui-paginator-next")
                if "ui-state-disabled" in next_button.get_attribute("class"):
                    break
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the new page to load
            except Exception as e:
                print(f"No more pages or an error occurred: {e}")
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    driver.quit()

    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
