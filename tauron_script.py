# tauron_script.py

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_total_pages(driver):
    try:
        paginator = driver.find_element(By.CLASS_NAME, "mp_paginator")
        pages = paginator.find_elements(By.CSS_SELECTOR, "li a.anchor")
        return int(pages[-2].text)  # Get the second last element, which should be the last page number
    except Exception as e:
        print(f"Error while getting total pages: {e}")
        return 1  # Default to one page if an error occurred

def fetch_tauron_results(keywords):
    driver = setup_driver()
    driver.get('https://swoz.tauron.pl/platform/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList')

    # Wait for the page to load
    time.sleep(5)

    try:
        # Select option 100 in the dropdown menu
        select = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "GD_pagesize"))
        ))
        select.select_by_value("100")
        
        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataRow"))
        )

        results = []
        unique_titles = set()  # Set of unique titles

        # Get the total number of pages
        total_pages = get_total_pages(driver)
        print(f"Total pages found: {total_pages}")

        # Iterate through all pages
        for page in range(total_pages):
            print(f"Processing page {page + 1} of {total_pages}")

            # Get all table rows on the current page
            rows = driver.find_elements(By.XPATH, "//tbody/tr/td[2]")
            print(f"Found {len(rows)} rows on the current page.")  # Should print the number of rows found

            for i in range(len(rows)):
                try:
                    # Refresh the list of rows because navigating to a new page causes earlier references to become stale
                    rows = driver.find_elements(By.XPATH, "//tbody/tr/td[2]")
                    row = rows[i]
                    
                    title = row.text
                    if title not in unique_titles and any(keyword.strip().lower() in title.lower() for keyword in keywords):
                        
                        # Click on the row to go to details
                        driver.execute_script("arguments[0].click();", row)
                        time.sleep(1)  # Wait for the new page to load
                        
                        # Get the current page link
                        link = driver.current_url
                        results.append([title, link, 'tauron'])

                        # Add title to unique_titles to prevent duplicates
                        unique_titles.add(title)

                        # Return to the results page
                        driver.back()  # Use the "Back" button
                        time.sleep(1)  # Wait for the results page to load

                except Exception as e:
                    print(f"Error processing row: {e}")

            # Click the "Next" button if not on the last page
            if page < total_pages - 1:
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@title='Następny']"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(5)  # Wait for the new page to load
                except Exception as e:
                    print(f"An error occurred while moving to the next page: {e}")
                    break

        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
