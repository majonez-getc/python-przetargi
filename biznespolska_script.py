from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


def setup_driver():
    """
    Funkcja konfigurująca sterownik Chrome z opcjami.
    Ustawia tryb 'headless' oraz inne opcje, które pomagają w działaniu skryptu.
    Zwraca instancję sterownika Chrome.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uruchomienie przeglądarki w trybie headless (bez GUI)
    chrome_options.add_argument(
        "--no-sandbox")  # Rozwiązuje problemy z sandboxem w niektórych środowiskach (np. Docker)
    chrome_options.add_argument(
        "--disable-dev-shm-usage")  # Wyłącza użycie pamięci współdzielonej, co może pomóc na maszynach z ograniczoną pamięcią
    driver = webdriver.Chrome(options=chrome_options)  # Inicjalizuje sterownik z powyższymi opcjami
    return driver


def contains_keywords(title, keywords):
    """
    Funkcja sprawdzająca, czy tytuł zawiera przynajmniej jedno z podanych słów kluczowych.
    Używa wyrażeń regularnych, aby sprawdzić występowanie słów kluczowych w tytule.

    title: str - tytuł oferty
    keywords: list - lista słów kluczowych

    Zwraca True, jeśli któreś ze słów kluczowych występuje w tytule, w przeciwnym razie False.
    """
    title = title.lower()  # Przekształca tytuł na małe litery, by ignorować różnice w wielkości liter
    # Sprawdzanie, czy któreś słowo kluczowe występuje w tytule
    return any(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', title) for keyword in keywords)


def fetch_biznespolska_results(keywords):
    """
    Funkcja do pobierania ofert z serwisu BiznesPolska.
    Otwiera stronę i przeszukuje oferty na wszystkich stronach, dopóki są dostępne.

    keywords: list - lista słów kluczowych

    Zwraca listę wyników zawierającą tytuły ofert, linki oraz źródło.
    """
    url = 'https://www.biznes-polska.pl/oferty/'  # URL strony z ofertami
    driver = setup_driver()  # Inicjalizowanie sterownika przeglądarki
    driver.get(url)  # Otwieranie strony

    results = []  # Lista, do której będą dodawane wyniki
    page_number = 1  # Licznik stron

    while True:
        print(f"Processing page {page_number}")
        try:
            # Czekanie na załadowanie tabeli ofert (element tbody)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
            )

            # Znalezienie wszystkich wierszy w tabeli (oferty)
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            print(f"Found {len(rows)} rows")

            # Przechodzenie przez wszystkie wiersze
            for row in rows:
                try:
                    # Zbieranie tytułu i linku oferty
                    title_element = row.find_element(By.CSS_SELECTOR, "a.title")
                    title = title_element.text
                    link = title_element.get_attribute("href")

                    # Sprawdzanie, czy tytuł zawiera któreś ze słów kluczowych
                    if contains_keywords(title, keywords):
                        results.append([title, link, "BIZNESPOLSKA"])  # Dodanie wyniku do listy

                except Exception as e:
                    print(f"Error while processing a row: {e}")  # Obsługuje błąd, jeśli nie uda się znaleźć elementu
                    continue  # Przechodzi do kolejnego wiersza, ignorując ten, który sprawił błąd

            # Szukanie przycisku "Next" do przejścia na następną stronę
            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.next")
            if next_buttons and next_buttons[0].is_displayed():
                driver.execute_script("arguments[0].click();", next_buttons[0])  # Kliknięcie przycisku "Next"
                page_number += 1  # Zwiększenie numeru strony
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
                )  # Czekanie na załadowanie kolejnej strony
            else:
                break  # Jeśli nie ma przycisku "Next", kończymy przetwarzanie

        except Exception as e:
            print(f"Error or no more pages: {e}")  # Obsługuje błędy lub brak dostępnych stron
            break  # Kończy działanie, gdy nie ma więcej stron lub wystąpił błąd

    driver.quit()  # Zamyka przeglądarkę po zakończeniu
    return results  # Zwraca listę wyników


if __name__ == "__main__":
    keywords = ["keyword1", "keyword2",
                "keyword3"]  # Lista słów kluczowych, które mają być wyszukiwane w tytułach ofert
    results = fetch_biznespolska_results(keywords)  # Uruchomienie funkcji zbierającej dane

    # Wydrukowanie wyników (tytuł, link, źródło)
    for result in results:
        print(f"Title: {result[0]}, Link: {result[1]}, Source: {result[2]}")
