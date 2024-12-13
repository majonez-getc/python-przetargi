# energa_script.py

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time

def contains_keywords(title, keywords):
    for keyword in keywords:
        if keyword.lower().strip() in title.lower():
            return True
    return False

def fetch_energa_results(keywords):
    # Initialize the results list
    results = []
    
    # Chrome settings
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the browser
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Open the page
        driver.get("https://energaostroleka.logintrade.net/portal,listaZapytaniaOfertowe.html?page=1&itemsperpage=9999")
        print("Page opened:", driver.current_url)
        
        # Click the dropdown menu
        dropdown_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.multiselect.dropdown-toggle"))
        )
        dropdown_button.click()
        print("Clicked dropdown menu")
        
        # Uncheck selected checkboxes
        checkbox_values_to_deselect = ["w_realizacji_po_terminie", "ocena_ofert", "zakonczone", "anulowane"]
        for value in checkbox_values_to_deselect:
            checkbox = driver.find_element(By.CSS_SELECTOR, f"input[type='checkbox'][value='{value}']")
            if checkbox.is_selected():
                checkbox.click()
                print(f"Unchecked checkbox '{value}'")
            else:
                print(f"Checkbox '{value}' was already unchecked")
        
        # Click the "Szukaj" button using JavaScript
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.searchButton a[onclick*='document.zapytaniaSearchForm.submit()']"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        print("Clicked 'Szukaj' button")
        
        # Wait for the results to load
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr"))
            )
            print("Results loaded")
        except TimeoutException:
            print("TimeoutException: Elements were not found in the specified time after clicking 'Szukaj'.")
            # Save the page source for debugging
            with open('error_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            return results  # Return empty results
        
        # Get the table rows
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        
        print(f"Found {len(rows)} rows")
        
        if not rows:
            print("No rows found.")
            return results
        
        for idx, row in enumerate(rows, start=1):
            try:
                print("ENERGA")
                title_element = row.find_element(By.CSS_SELECTOR, 'a.name')
                title = title_element.text
                link = title_element.get_attribute('href')
                
                # Check if any keyword is in the title
                if title and contains_keywords(title, keywords):
                    results.append([title.strip(), link, "ENERGA"])
            except Exception as e:
                # It's possible that the row doesn't contain an 'a.name' element, skip such rows
                pass
                
    finally:
        # Close the browser
        driver.quit()
    
    # Return the results to the main script
    return results

if __name__ == "__main__":
    pass  # Do nothing when the script is run directly
