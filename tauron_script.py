import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select


# Funkcja do ustawienia sterownika przeglądarki
def setup_driver():
    # Ustawienia dla Chrome - opcje sterownika
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uruchomienie przeglądarki w trybie headless (bez GUI)
    chrome_options.add_argument("--disable-gpu")  # Wyłączenie używania GPU (przydatne w trybie headless)
    chrome_options.add_argument("--no-sandbox")  # Wyłączenie sandboxa (często używane w środowiskach Linux)

    # Utworzenie instancji sterownika Chrome z powyższymi opcjami
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# Funkcja do pobierania liczby stron wyników
def get_total_pages(driver):
    try:
        # Szukanie elementu paginatora, który zawiera informacje o stronach
        paginator = driver.find_element(By.CLASS_NAME, "mp_paginator")
        # Szukanie wszystkich linków stron (linki do stron są w tagach <a> wewnątrz <li>)
        pages = paginator.find_elements(By.CSS_SELECTOR, "li a.anchor")
        # Zwracamy numer przedostatniej strony, ponieważ ostatni element to przycisk "Następny"
        return int(pages[-2].text)
    except Exception as e:
        # Jeśli wystąpi błąd, domyślnie uznajemy, że jest tylko jedna strona
        print(f"Error while getting total pages: {e}")
        return 1


# Funkcja do przetwarzania wyników z jednej strony
def process_page(driver, current_date, keywords, results):
    # Wyszukiwanie wszystkich wierszy tabeli
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    print(f"Found {len(rows)} rows on the current page.")

    for row in rows:
        try:
            # Pobieranie identyfikatora wiersza
            row_id = row.get_attribute("id")
            # Tworzenie linku do szczegółów oferty na podstawie ID wiersza
            link = f"https://swoz.tauron.pl/platform/demand/notice/public/{row_id}/details"

            # Pobieranie daty zakończenia oferty
            date_elements = row.find_elements(By.CLASS_NAME, "date-time")
            if len(date_elements) < 2:
                continue  # Pomijamy wiersze, które nie zawierają daty

            end_date_str = date_elements[1].text
            try:
                # Przekształcanie daty w formacie string na obiekt datetime
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                continue  # Pomijamy wiersze z niepoprawnym formatem daty

            # Jeśli data zakończenia jest przeszła w stosunku do obecnej daty, przerywamy przetwarzanie
            if end_date <= current_date:
                print(f"Terminy w wierszu {row_id} są nieaktualne. Zakończono przetwarzanie.")
                return results, True  # Zwracamy wyniki oraz sygnał o zakończeniu

            # Sprawdzanie, czy tytuł oferty pasuje do słów kluczowych
            title_element = row.find_elements(By.CLASS_NAME, "text.long")
            if title_element:
                title = title_element[0].text
                # Jeśli którykolwiek ze słów kluczowych znajduje się w tytule, dodajemy ofertę do wyników
                if any(keyword.strip().lower() in title.lower() for keyword in keywords):
                    results.append([title, link, 'tauron'])

        except Exception as e:
            # Obsługa błędów dla pojedynczych wierszy
            print(f"Error processing row: {e}")

    return results, False  # Jeśli nie napotkano daty przeszłej, kontynuujemy przetwarzanie


# Funkcja główna, która pobiera wyniki dla podanych słów kluczowych
def fetch_tauron_results(keywords):
    # Inicjalizacja sterownika przeglądarki
    driver = setup_driver()
    driver.get('https://swoz.tauron.pl/platform/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList')

    # Oczekiwanie na załadowanie strony (element, który wskazuje, że strona jest gotowa)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "GD_pagesize"))
    )

    try:
        # Wybór liczby wyników na stronę (np. 100 wyników)
        select = Select(driver.find_element(By.NAME, "GD_pagesize"))
        select.select_by_value("100")

        # Oczekiwanie na pojawienie się wyników
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataRow"))
        )

        # Inicjalizacja listy wyników i bieżącej daty
        results = []
        current_date = datetime.now()

        # Pobranie całkowitej liczby stron wyników
        total_pages = get_total_pages(driver)
        print(f"Total pages found: {total_pages}")

        # Przetwarzanie każdej strony
        for page in range(total_pages):
            print(f"Processing page {page + 1} of {total_pages}")
            results, stop_processing = process_page(driver, current_date, keywords, results)

            # Jeśli napotkano ofertę z przeszłą datą, przerywamy przetwarzanie
            if stop_processing:
                break

            # Jeśli istnieje kolejna strona, przechodzimy do niej
            if page < total_pages - 1:
                try:
                    # Wyszukiwanie przycisku "Następny"
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@title='Następny']"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)  # Kliknięcie na przycisk "Następny"
                    time.sleep(3)  # Krótkie oczekiwanie na załadowanie nowej strony
                except Exception as e:
                    print(f"An error occurred while moving to the next page: {e}")
                    break

        return results

    finally:
        driver.quit()  # Zamknięcie przeglądarki po zakończeniu


# Główna część skryptu
if __name__ == "__main__":
    pass
    # skrypt zwraca dane do pliku AIO.py
