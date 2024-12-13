import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def setup_driver():
    """Initialize the WebDriver with the necessary options."""
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def wait_for_element(driver, by, value, timeout=10):
    """Helper function to wait for an element to be clickable."""
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    except TimeoutException:
        print(f"Element {value} not found within {timeout} seconds.")
        return None


def fetch_pse_results(keywords):
    """Fetch auction results from the PSE website."""
    driver = setup_driver()
    driver.get('https://przetargi.pse.pl/open-auctions.html')

    # Wait for the page to load completely
    time.sleep(3)  # Initial load

    results = []
    page = 1

    while True:
        print(f"Processing page {page}")

        # Wait for table rows to be visible
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
        )
        print(f"Found {len(rows)} rows on the current page.")

        # If the number of rows is less than 25, it's the last page
        if len(rows) < 25:
            print("This is the last page.")
            break

        # Iterate through each row to extract auction details
        for row in rows:
            try:
                title_element = row.find_element(By.XPATH, ".//td[5]/div/a")
                title = title_element.text
                link = title_element.get_attribute("href")
                status_element = row.find_element(By.XPATH, ".//td[15]/div")
                status = status_element.text
                # Check if status is "Etap składania ofert" and if title matches any keyword
                if "Etap składania ofert" in status and any(
                        keyword.strip().lower() in title.lower() for keyword in keywords):
                    results.append([title, link, 'pse'])
            except NoSuchElementException:
                print("No relevant data in this row.")

        # Look for the "Next" button and click it if available
        try:
            next_button = wait_for_element(driver, By.XPATH,
                                           "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/div/div/div[7]/em/button/span[2]")
            if next_button:
                next_button.click()  # Click the "Next" button
                # Wait for the next set of results to load before continuing
                WebDriverWait(driver, 10).until(EC.staleness_of(rows[0]))  # Wait for rows to refresh
                page += 1
            else:
                print("No more pages.")
                break
        except TimeoutException:
            print("Timeout or no 'Next' button found.")
            break

    driver.quit()
    return results


if __name__ == "__main__":
    # Example: Fetch results for keywords
    keywords = ['energia', 'przetarg']
    results = fetch_pse_results(keywords)

    # Save results to CSV (optional)
    with open('auction_results.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Link", "Source"])
        for result in results:
            writer.writerow(result)
