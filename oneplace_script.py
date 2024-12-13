import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver():
    """
    Funkcja do konfiguracji sterownika przeglądarki.
    Uruchamia Chrome w trybie headless oraz ustawia odpowiednie opcje, takie jak
    wyłączenie GPU oraz wyłączenie sandboxa. Tryb headless jest wyłączony w tym przypadku,
    ale można go włączyć, odkomentowując odpowiednią linię.

    Zwraca:
        driver (webdriver.Chrome): skonfigurowany obiekt sterownika Chrome.
    """
    chrome_options = Options()
    # Włącz tryb headless, jeśli wymagane (wykomentuj, jeśli nie chcesz używać headless)
    chrome_options.add_argument("--headless")

    # Wyłączenie GPU oraz sandboxa dla większej stabilności
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Inicjalizacja sterownika Chrome z podanymi opcjami
    driver = webdriver.Chrome(options=chrome_options)

    return driver


def fetch_oneplace_results(keywords):
    """
    Funkcja pobierająca oferty z serwisu OnePlace na podstawie słów kluczowych.
    Filtruje wyniki, aby zawierały tylko te oferty, które zawierają przynajmniej jedno
    z podanych słów kluczowych. Skrypt automatycznie przechodzi przez strony, pobierając
    kolejne oferty.

    Args:
        keywords (list): Lista słów kluczowych do wyszukiwania w tytule ofert.

    Zwraca:
        results (list): Lista znalezionych wyników, gdzie każdy wynik jest listą zawierającą
                        tytuł oferty, link oraz źródło ("ONEPLACE").
    """
    # URL strony z ofertami
    url = "https://oneplace.marketplanet.pl/zapytania-ofertowe-przetargi/-/rfp/cat/11035/elektroenergetyka?_7_WAR_organizationnoticeportlet_cur=1"

    # Przekształcanie słów kluczowych na małe litery oraz usunięcie nadmiarowych spacji
    keywords = set(keyword.strip().lower() for keyword in keywords)

    # Inicjalizacja sterownika przeglądarki
    driver = setup_driver()
    driver.get(url)

    # Lista na wyniki wyszukiwania
    results = []

    while True:
        try:
            # Czekanie, aż strony ładują się wystarczająco, aby znaleźć oferty
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.tiles"))
            )

            # Pobieranie wszystkich ofert na bieżącej stronie
            articles = driver.find_elements(By.CSS_SELECTOR, "div.row.tiles article")

            # Iterowanie przez wszystkie oferty na stronie
            for article in articles:
                # Pobieranie tytułu oferty
                title_element = article.find_element(By.CSS_SELECTOR, "h3.title")
                title = title_element.text.strip().lower()  # Upewnij się, że tytuł jest w małych literach
                # Pobieranie linku do oferty
                link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                # Sprawdzanie, czy tytuł zawiera którekolwiek z podanych słów kluczowych
                if any(keyword in title for keyword in keywords):
                    # Dodanie oferty do wyników, jeśli pasuje
                    results.append([title, link, 'ONEPLACE'])
                    print(f"Found: {title} - {link}")

            # Próba przejścia do następnej strony, jeśli przycisk "Next" jest dostępny
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
                # Kliknięcie przycisku "Next" w celu przejścia do następnej strony
                next_button.click()
                # Czekanie na załadowanie nowych ofert po przejściu na nową stronę
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.tiles"))
                )
            except Exception as e:
                # Jeśli nie ma już przycisku "Next" lub wystąpił błąd, kończymy pętlę
                print(f"End of pages or error: {e}")
                break

        except Exception as e:
            # Obsługuje wszelkie inne błędy (np. timeout, problem z ładowaniem strony)
            print(f"Error occurred: {e}")
            break

    # Zakończenie sesji przeglądarki po zakończeniu zbierania danych
    driver.quit()

    return results


if __name__ == "__main__":
    # Przykładowe słowa kluczowe do wyszukiwania w tytułach ofert
    keywords = ["elektroenergetyka", "przetargi", "oferta"]

    # Wywołanie funkcji pobierającej oferty z serwisu OnePlace
    results = fetch_oneplace_results(keywords)

    # Zapisanie wyników do pliku CSV
    with open('oneplace_results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Nagłówki w pliku CSV
        writer.writerow(["Title", "Link", "Source"])
        # Zapisanie każdego wyniku do pliku CSV
        for result in results:
            writer.writerow(result)
