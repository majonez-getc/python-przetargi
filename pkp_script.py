# pkp_script.py

import csv
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def contains_keywords(title, keywords):
    for keyword in keywords:
        if keyword.lower().strip() in title.lower():
            return True
    return False

def fetch_pkp_results(keywords):
    # Initialize the results list
    results = []

    # Chrome settings
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    webdriver_service = ChromeService(ChromeDriverManager().install())

    # Initialize the browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    try:
        # Open the page
        driver.get("https://platformazakupowa.plk-sa.pl/app/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList")

        # Change option to "All" in dropdown menu
        select_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "GD_pagesize"))
        )
        select_element.click()
        all_option = driver.find_element(By.CSS_SELECTOR, "option[value='99999999']")
        all_option.click()

        # Click the confirm button if it appears
        try:
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal-button.swal-button--confirm"))
            )
            confirm_button.click()
        except:
            pass  # If the confirm button doesn't appear, continue

        # Wait for the table to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.dataRow"))
        )

        # Get table rows
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.dataRow")

        print(f"Found {len(rows)} rows")

        # Collect titles and rows
        data = []
        for row in rows:
            title_element = row.find_element(By.CSS_SELECTOR, 'td.long.col-1')
            title = title_element.text
            if title and contains_keywords(title, keywords):
                data.append({'title': title.strip(), 'row': row})

        if not data:
            print("No matching data found.")
            return results

        for item in data:
            title = item['title']
            row = item['row']

            # Store the current window handle
            original_window = driver.current_window_handle
            before_click_window_handles = driver.window_handles

            # Click on the row to open details (which opens in a new tab)
            driver.execute_script("arguments[0].click();", row)

            # Wait for the new window or tab
            WebDriverWait(driver, 20).until(
                lambda d: len(d.window_handles) > len(before_click_window_handles)
            )

            # Switch to the new window
            new_window_handles = driver.window_handles
            new_window = [window for window in new_window_handles if window not in before_click_window_handles][0]
            driver.switch_to.window(new_window)

            # Wait for the page to load completely
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # Get the current URL
            link = driver.current_url

            # Append to results list
            print(f"Title: {title}, Link: {link}")
            results.append([title, link, 'pkp'])

            # Close the new window
            driver.close()

            # Switch back to the original window
            driver.switch_to.window(original_window)

            # Wait for the table to be present again
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.dataRow"))
            )

    except Exception as e:
        print("An exception occurred:")
        traceback.print_exc()
    finally:
        # Close the browser
        driver.quit()

    # Return the results list
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
