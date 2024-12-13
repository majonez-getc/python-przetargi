# pern_script.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def setup_driver():
    """Funkcja do konfiguracji i uruchomienia przeglądarki Chrome z odpowiednimi opcjami."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Inicjalizacja WebDrivera
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def fetch_pern_results(keywords):
    """
    Funkcja przeszukuje stronę PERN w celu znalezienia ofert pasujących do słów kluczowych.

    Parametry:
        keywords (list): lista słów kluczowych, które mają być wyszukane w tytule ogłoszeń.

    Zwraca:
        results (list): lista pasujących wyników, każdy wynik to lista [tytuł, link, źródło].
    """
    driver = setup_driver()
    driver.get("https://platformazakupowa.pern.pl/adverts/NonAdvertActs.xhtml")

    results = []

    while True:
        try:
            # Czekamy, aż na stronie pojawią się wyniki
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.ui-datatable-data tr"))
            )

            # Pobieramy wszystkie wiersze wyników
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ui-datatable-data tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    title = cells[1].text  # Tytuł ogłoszenia jest w drugiej kolumnie
                    for keyword in keywords:
                        # Sprawdzamy, czy tytuł zawiera jedno ze słów kluczowych (niezależnie od wielkości liter)
                        if keyword.strip().lower() in title.lower():
                            # Pobieramy link do szczegółów ogłoszenia
                            details_link = cells[-1].find_element(By.TAG_NAME, "a").get_attribute("href")
                            results.append([title, details_link, 'pern'])
                            break  # Jeśli jedno słowo kluczowe pasuje, przechodzimy do następnego ogłoszenia

            # Przechodzimy do następnej strony, jeśli przycisk "Next" jest dostępny
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "span.ui-paginator-next")
                # Sprawdzamy, czy przycisk nie jest wyłączony
                if "ui-state-disabled" in next_button.get_attribute("class"):
                    break  # Jeśli przycisk jest wyłączony, kończymy przeszukiwanie
                # Klikamy przycisk "Next"
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Czekamy na załadowanie nowej strony
            except Exception as e:
                print(f"No more pages or an error occurred: {e}")
                break  # Jeśli nie ma już następnej strony lub wystąpił błąd, kończymy

        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Jeśli wystąpił błąd w trakcie przetwarzania strony, kończymy

    # Zamykanie przeglądarki po zakończeniu przeszukiwania
    driver.quit()

    # Zwracamy zebrane wyniki
    return results


if __name__ == "__main__":
    # Przykładowe użycie funkcji fetch_pern_results
    keywords = ["gas", "oil", "pipe"]  # Lista słów kluczowych do wyszukiwania
    results = fetch_pern_results(keywords)
    for result in results:
        print(f"Title: {result[0]}, Link: {result[1]}, Source: {result[2]}")
