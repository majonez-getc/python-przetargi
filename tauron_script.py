import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

# Funkcja do ustawienia sterownika
def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Funkcja do pobierania liczby stron
def get_total_pages(driver):
    try:
        paginator = driver.find_element(By.CLASS_NAME, "mp_paginator")
        pages = paginator.find_elements(By.CSS_SELECTOR, "li a.anchor")
        return int(pages[-2].text)  # Zwrócenie przedostatniego elementu jako ostatniej strony
    except Exception as e:
        print(f"Error while getting total pages: {e}")
        return 1  # Domyślnie jedna strona, jeśli wystąpił błąd

# Funkcja do przetwarzania wyników z jednej strony
def process_page(driver, current_date, keywords, results):
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    print(f"Found {len(rows)} rows on the current page.")

    for row in rows:
        try:
            row_id = row.get_attribute("id")
            link = f"https://swoz.tauron.pl/platform/demand/notice/public/{row_id}/details"

            # Pobieranie daty końcowej
            date_elements = row.find_elements(By.CLASS_NAME, "date-time")
            if len(date_elements) < 2:
                continue  # Pomijamy wiersze bez daty

            end_date_str = date_elements[1].text
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue  # Pomijamy wiersze z niepoprawnym formatem daty

            # Jeśli termin w przeszłości, kończymy przetwarzanie
            if end_date <= current_date:
                print(f"Terminy w wierszu {row_id} są nieaktualne. Zakończono przetwarzanie.")
                return results  # Zwrócenie pustej listy, jeśli termin jest nieaktualny

            # Sprawdzanie, czy tytuł pasuje do słów kluczowych
            title_element = row.find_elements(By.CLASS_NAME, "text.long")
            if title_element:
                title = title_element[0].text
                if any(keyword.strip().lower() in title.lower() for keyword in keywords):
                    results.append([title, link, 'tauron'])

        except Exception as e:
            print(f"Error processing row: {e}")

    return results

# Funkcja główna do pobierania wyników
def fetch_tauron_results(keywords):
    driver = setup_driver()
    driver.get('https://swoz.tauron.pl/platform/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList')

    # Oczekiwanie na załadowanie strony
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "GD_pagesize"))
    )

    try:
        # Wybór liczby wyników na stronie
        select = Select(driver.find_element(By.NAME, "GD_pagesize"))
        select.select_by_value("100")

        # Oczekiwanie na wyniki
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataRow"))
        )

        # Inicjalizacja zmiennych
        results = []
        current_date = datetime.now()

        # Pobranie całkowitej liczby stron
        total_pages = get_total_pages(driver)
        print(f"Total pages found: {total_pages}")

        # Przetwarzanie każdej strony
        for page in range(total_pages):
            print(f"Processing page {page + 1} of {total_pages}")
            results = process_page(driver, current_date, keywords, results)

            if not results:  # Jeśli wyniki są puste, kończymy działanie
                break

            # Przejście do następnej strony, jeśli istnieje
            if page < total_pages - 1:
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@title='Następny']"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)  # Krótkie oczekiwanie na załadowanie nowej strony
                except Exception as e:
                    print(f"An error occurred while moving to the next page: {e}")
                    break

        return results

    finally:
        driver.quit()

# Główna część skryptu
if __name__ == "__main__":
    keywords = ['przetarg', 'usługi']  # Słowa kluczowe do filtrowania
    results = fetch_tauron_results(keywords)

    # Drukowanie wyników
    for result in results:
        print(result)
