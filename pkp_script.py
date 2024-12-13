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


def contains_keywords(title, keywords):
    """
    Funkcja sprawdzająca, czy w tytule występuje któreś ze słów kluczowych.

    Parametry:
        title (str): Tytuł ogłoszenia.
        keywords (list): Lista słów kluczowych do wyszukania w tytule.

    Zwraca:
        bool: True, jeśli przynajmniej jedno słowo kluczowe jest w tytule, w przeciwnym razie False.
    """
    return any(keyword.lower().strip() in title.lower() for keyword in keywords)


def fetch_pkp_results(keywords):
    """
    Funkcja przeszukuje stronę PKP w celu znalezienia ogłoszeń pasujących do słów kluczowych.

    Parametry:
        keywords (list): Lista słów kluczowych, które mają być wyszukane w tytule ogłoszeń.

    Zwraca:
        results (list): Lista wyników, każdy wynik to lista [tytuł, link, źródło].
    """
    results = []

    # Konfiguracja opcji przeglądarki
    chrome_options = Options()
    # Jeśli chcesz uruchomić skrypt w trybie headless, odkomentuj poniższą linię
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    webdriver_service = ChromeService(ChromeDriverManager().install())

    # Inicjalizacja przeglądarki
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    try:
        # Otwórz stronę
        driver.get(
            "https://platformazakupowa.plk-sa.pl/app/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList")

        # Wybierz opcję "Wszystkie" w menu rozwijanym
        select_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "GD_pagesize"))
        )
        select_element.click()
        all_option = driver.find_element(By.CSS_SELECTOR, "option[value='99999999']")
        all_option.click()

        # Kliknij przycisk potwierdzenia, jeśli się pojawi
        try:
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal-button.swal-button--confirm"))
            )
            confirm_button.click()
        except:
            pass  # Jeśli przycisk nie pojawił się, kontynuuj

        # Czekaj, aż tabela z danymi będzie załadowana
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.dataRow"))
        )

        # Pobierz wszystkie wiersze tabeli
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.dataRow")
        print(f"Found {len(rows)} rows")

        # Filtruj wiersze według słów kluczowych
        data = [
            {'title': row.find_element(By.CSS_SELECTOR, 'td.long.col-1').text.strip(), 'id': row.get_attribute('id')}
            for row in rows
            if contains_keywords(row.find_element(By.CSS_SELECTOR, 'td.long.col-1').text, keywords)
        ]

        if not data:
            print("No matching data found.")
            return results

        for item in data:
            title = item['title']
            index_id = item['id']

            # Tworzymy URL do szczegółów ogłoszenia
            link = f"https://platformazakupowa.plk-sa.pl/app/demand/notice/public/{index_id}/details"

            # Dodaj wynik do listy
            results.append([title, link, 'pkp'])
            print(f"Title: {title}, Link: {link}")

    except Exception as e:
        print("An exception occurred:")
        traceback.print_exc()
    finally:
        # Zamknij przeglądarkę po zakończeniu
        driver.quit()

    # Zwróć wyniki
    return results


if __name__ == "__main__":
    pass  # Nie rób nic, gdy skrypt jest uruchamiany bezpośrednio
