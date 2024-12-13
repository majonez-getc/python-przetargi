# biparp_script.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def setup_driver():
    """
    Ustawia konfigurację przeglądarki Chrome, tworzy i zwraca instancję przeglądarki.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Włącza tryb headless dla przeglądarki (nie wyświetla interfejsu)
    chrome_options.add_argument("--disable-gpu")  # Wyłącza użycie GPU (przydatne w headless mode)
    chrome_options.add_argument("--no-sandbox")  # Wyłącza piaskownicę, co może pomóc w uniknięciu błędów w niektórych systemach
    chrome_options.add_argument("--window-size=1920,1080")  # Ustawia rozdzielczość okna przeglądarki (do rozwiązywania problemów z responsywnością strony)

    driver = webdriver.Chrome(options=chrome_options)  # Tworzy instancję przeglądarki z wcześniej ustawionymi opcjami
    return driver


def process_page(driver, keywords):
    """
    Przetwarza jedną stronę, przeszukując artykuły i zbierając wyniki,
    które zawierają przynajmniej jedno z podanych słów kluczowych w tytule.
    """
    results1 = []  # Lista do przechowywania wyników
    articles = driver.find_elements(By.CLASS_NAME, "art_list")  # Znajdujemy wszystkie artykuły na stronie

    # Dla każdego artykułu na stronie:
    for article in articles:
        # Szukamy elementu zawierającego tytuł i link
        title_element = article.find_element(By.CSS_SELECTOR, ".lewy a")
        title = title_element.text.strip()  # Pobieramy tytuł artykułu i usuwamy zbędne spacje
        link = title_element.get_attribute("href")  # Pobieramy link do artykułu

        # Sprawdzamy, czy tytuł zawiera któreś z podanych słów kluczowych
        if any(keyword.lower() in title.lower() for keyword in keywords):
            # Jeśli tak, dodajemy wynik do listy
            results1.append([title, link, "BIPARP"])

    return results1


def fetch_biparp_results(keywords):
    """
    Funkcja główna odpowiedzialna za zbieranie wyników ze strony BIPARP.
    Pobiera dane ze wszystkich stron, przechodzi przez kolejne strony aukcji,
    i zwraca wyniki pasujące do podanych słów kluczowych.
    """
    driver = setup_driver()  # Uruchamiamy przeglądarkę
    driver.get("https://arp.bip.gov.pl/articles/index/zamowienia-strefowe/page:1")  # Ładujemy pierwszą stronę

    results = []  # Lista, która będzie przechowywać ostateczne wyniki

    while True:
        print("BIARP")  # Drukowanie komunikatu w konsoli informującego o przetwarzaniu strony
        results.extend(process_page(driver, keywords))  # Przetwarzamy stronę i dodajemy wyniki do listy

        try:
            # Próbujemy znaleźć przycisk "Next", aby przejść do następnej strony
            next_button = driver.find_element(By.CSS_SELECTOR, "a.next")
            driver.execute_script("arguments[0].click();", next_button)  # Klikamy przycisk "Next"
            time.sleep(2)  # Czekamy 2 sekundy na załadowanie nowej strony
        except:
            # Jeśli nie udało się znaleźć przycisku "Next", kończymy pętlę (brak kolejnych stron)
            break

    driver.quit()  # Zamykamy przeglądarkę po zakończeniu przetwarzania

    # Zwracamy wyniki do głównego programu
    return results


if __name__ == "__main__":
    pass  # Jeśli skrypt jest uruchamiany bezpośrednio, nie wykonuje żadnej akcji (brak słów kluczowych do przetworzenia)
