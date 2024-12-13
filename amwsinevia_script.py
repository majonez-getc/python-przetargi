import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def setup_driver():
    """
    Konfiguruje i uruchamia instancję przeglądarki Chrome z odpowiednimi opcjami.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Możesz włączyć tryb headless w razie potrzeby
    chrome_options.add_argument("--disable-gpu")  # Wyłączenie GPU, jeśli nie jest potrzebne
    chrome_options.add_argument("--no-sandbox")  # Zabezpieczenie przed problemami z uprawnieniami
    driver = webdriver.Chrome(options=chrome_options)  # Tworzy instancję przeglądarki Chrome z ustawionymi opcjami
    return driver


def fetch_amwsinevia_results(keywords):
    """
    Funkcja łączy się ze stroną AMWSinevia i przetwarza wyniki aukcji.
    Wyszukuje w tytułach aukcji zadane słowa kluczowe, a także sprawdza status aukcji.
    """
    driver = setup_driver()  # Uruchomienie przeglądarki
    driver.get('https://amwsinevia.eb2b.com.pl/open-auctions.html')  # Otworzenie strony z aukcjami

    # Oczekiwanie na załadowanie strony, zwrócenie uwagi na przycisk akceptacji cookies
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span#button-1014-btnInnerEl"))
    )

    try:
        # Próbujemy kliknąć przycisk "Akceptuj cookies", jeśli jest obecny
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span#button-1014-btnInnerEl"))
            )
            accept_button.click()  # Kliknięcie w przycisk akceptacji
            print("Clicked on accept cookies button.")
        except (NoSuchElementException, TimeoutException):
            print("No accept cookies button found or an error occurred.")  # Jeśli przycisk nie istnieje, pomijamy

        results = []  # Lista do przechowywania wyników
        page = 1  # Numer bieżącej strony
        last_first_row_text = None  # Zmienna do porównywania pierwszego wiersza w tabeli (aby wykryć koniec)

        while True:
            time.sleep(2)  # Krótkie opóźnienie między zapytaniami (dla stabilności)
            print(f"Processing page {page}")  # Informacja o bieżącej stronie

            # Czekamy na załadowanie wierszy w tabeli z dłuższym czasem oczekiwania
            rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
            )
            print("AMWSINEVIA")
            print(f"Found {len(rows)} rows on the current page.")  # Informacja o liczbie wierszy na stronie

            # Sprawdzanie, czy znaleziono jakiekolwiek wiersze i porównywanie pierwszego wiersza
            if rows:
                current_first_row_text = rows[1].text  # Tekst pierwszego wiersza w tabeli
                if current_first_row_text == last_first_row_text:  # Sprawdzamy, czy strona się powtarza
                    print("Reached the end of pages.")
                    break  # Jeśli tak, kończymy przetwarzanie
                last_first_row_text = current_first_row_text

            # Przetwarzanie danych w każdym wierszu
            for row in rows:
                try:
                    # Szukamy elementu zawierającego tytuł aukcji i link do niej
                    title_element = row.find_element(By.XPATH, ".//td[5]/div/a")
                    title = title_element.text
                    link = title_element.get_attribute("href")

                    # Szukamy statusu aukcji (np. "Etap składania ofert")
                    status_element = row.find_element(By.XPATH, ".//td[15]/div")
                    status = status_element.text

                    # Jeśli status jest "Etap składania ofert" i tytuł zawiera któreś z kluczowych słów
                    if "Etap składania ofert" in status and any(keyword.lower() in title.lower() for keyword in keywords):
                        results.append([title, link, 'amwsinevia'])  # Dodajemy wynik do listy
                except NoSuchElementException:
                    print("No title element found in this row.")  # Jeśli nie znaleziono elementu, informujemy o błędzie

            # Próbujemy kliknąć przycisk "Next", aby przejść do następnej strony
            try:
                next_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/div/div/div[7]/em/button/span[2]"))
                )
                driver.execute_script("arguments[0].click();", next_button)  # Klikamy przycisk "Next"
                page += 1  # Zwiększamy numer strony
                # Czekamy na załadowanie nowych wierszy po przejściu na następną stronę
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
                )
            except NoSuchElementException:
                print("No more pages.")  # Jeśli nie ma przycisku "Next", kończymy
                break

        # Zwracamy wyniki do głównego programu
        return results

    finally:
        driver.quit()  # Na końcu zamykamy przeglądarkę


if __name__ == "__main__":
    keywords = ["keyword1", "keyword2"]  # Wpisz tutaj odpowiednie słowa kluczowe
    results = fetch_amwsinevia_results(keywords)  # Wywołanie funkcji i pobranie wyników
    print("Found results:", results)  # Wyświetlanie wyników
