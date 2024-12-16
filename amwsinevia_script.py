import logging
import time

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Kolory ANSI do terminala
class LogColors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'


# Funkcja do kolorowego logowania
def log_with_color(level, msg):
    if level == "INFO":
        logging.info(f"{LogColors.GREEN}{msg}{LogColors.RESET}")
    elif level == "WARNING":
        logging.warning(f"{LogColors.YELLOW}{msg}{LogColors.RESET}")
    elif level == "ERROR":
        logging.error(f"{LogColors.RED}{msg}{LogColors.RESET}")


# Konfiguracja logowania
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Ustawienie poziomu logowania na INFO
)


def setup_driver():
    """
    Konfiguruje i uruchamia instancję przeglądarki Chrome z odpowiednimi opcjami.
    """
    log_with_color("INFO", "[AMWSinevia] Konfiguracja przeglądarki...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Włącza tryb headless dla przeglądarki (nie wyświetla interfejsu)
    chrome_options.add_argument("--disable-gpu")  # Wyłączenie GPU, jeśli nie jest potrzebne
    chrome_options.add_argument("--no-sandbox")  # Zabezpieczenie przed problemami z uprawnieniami
    driver = webdriver.Chrome(options=chrome_options)  # Tworzy instancję przeglądarki Chrome z ustawionymi opcjami
    log_with_color("INFO", "[AMWSinevia] Przeglądarka uruchomiona.")
    return driver


def change_input_value(driver):
    """
    Funkcja zmienia wartość inputa na stronie.
    """
    try:
        # Czekamy, aż element input będzie dostępny
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "combobox-1055-inputEl"))
        )

        # Znajdź element input
        input_element = driver.find_element(By.ID, "combobox-1055-inputEl")

        # Użyj JavaScriptu do ustawienia nowej wartości w input
        driver.execute_script("arguments[0].value = '100';", input_element)
        log_with_color("INFO", "[AMWSinevia] Input value zmienione na 100.")
    except NoSuchElementException:
        log_with_color("ERROR", "[AMWSinevia] Nie znaleziono elementu input.")
    except TimeoutException:
        log_with_color("ERROR", "[AMWSinevia] Czas oczekiwania na element input upłynął.")


def fetch_amwsinevia_results(keywords):
    """
    Funkcja łączy się ze stroną AMWSinevia i przetwarza wyniki aukcji.
    Wyszukuje w tytułach aukcji zadane słowa kluczowe, a także sprawdza status aukcji.
    """
    log_with_color("INFO", "[AMWSinevia] Rozpoczynanie przetwarzania strony.")
    driver = setup_driver()  # Uruchomienie przeglądarki
    driver.get('https://amwsinevia.eb2b.com.pl/open-auctions.html')  # Otworzenie strony z aukcjami

    try:
        # Oczekiwanie na załadowanie strony, zwrócenie uwagi na przycisk akceptacji cookies
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span#button-1014-btnInnerEl"))
        )

        # Próbujemy kliknąć przycisk "Akceptuj cookies", jeśli jest obecny
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span#button-1014-btnInnerEl"))
            )
            accept_button.click()  # Kliknięcie w przycisk akceptacji
            log_with_color("INFO", "[AMWSinevia] Kliknięto przycisk 'Akceptuj cookies'.")
        except (NoSuchElementException, TimeoutException):
            log_with_color("WARNING",
                           "[AMWSinevia] Przycisk 'Akceptuj cookies' nie został znaleziony lub wystąpił błąd.")

        results = []  # Lista do przechowywania wyników
        page = 1  # Numer bieżącej strony
        last_first_row_text = None  # Zmienna do porównywania pierwszego wiersza w tabeli (aby wykryć koniec)

        while True:
            time.sleep(2)  # Krótkie opóźnienie między zapytaniami (dla stabilności)
            log_with_color("INFO", f"[AMWSinevia] Przetwarzanie strony {page}...")

            # Czekamy na załadowanie wierszy w tabeli z dłuższym czasem oczekiwania
            rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
            )
            log_with_color("INFO", f"[AMWSinevia] Znaleziono {len(rows)} wierszy na stronie {page}.")

            # Sprawdzanie, czy znaleziono jakiekolwiek wiersze i porównywanie pierwszego wiersza
            if rows:
                current_first_row_text = rows[1].text  # Tekst pierwszego wiersza w tabeli
                if current_first_row_text == last_first_row_text:  # Sprawdzamy, czy strona się powtarza
                    log_with_color("INFO", f"[AMWSinevia] Osiągnięto koniec stron na stronie {page}.")
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
                    if "Etap składania ofert" in status and any(
                            keyword.lower() in title.lower() for keyword in keywords):
                        results.append([title, link, 'amwsinevia'])  # Dodajemy wynik do listy
                except NoSuchElementException:
                    pass

            # Próbujemy kliknąć przycisk "Next", aby przejść do następnej strony
            try:
                next_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/div/div/div[7]/em/button/span[2]"))
                )
                driver.execute_script("arguments[0].click();", next_button)  # Klikamy przycisk "Next"
                page += 1  # Zwiększamy numer strony
                # Czekamy na załadowanie nowych wierszy po przejściu na następną stronę
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
                )
            except NoSuchElementException:
                log_with_color("INFO", f"[AMWSinevia] Brak przycisku 'Next' - koniec stron na stronie {page}.")
                break

        # Zwracamy wyniki do głównego programu
        return results

    finally:
        driver.quit()  # Na końcu zamykamy przeglądarkę
        log_with_color("INFO", "[AMWSinevia] Przeglądarka zamknięta.")


if __name__ == "__main__":
    pass
