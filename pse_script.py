import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Klasa dla kolorowych logów
class LogColors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'


def log_with_color(level, msg):
    """Funkcja do logowania z kolorami."""
    if level == "INFO":
        print(f"{LogColors.GREEN}{msg}{LogColors.RESET}")
    elif level == "WARNING":
        print(f"{LogColors.YELLOW}{msg}{LogColors.RESET}")
    elif level == "ERROR":
        print(f"{LogColors.RED}{msg}{LogColors.RESET}")


def setup_driver():
    """Inicjalizuje WebDrivera z wymaganymi opcjami."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tryb headless (odkomentuj, aby włączyć widoczność przeglądarki)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    log_with_color("INFO", "[PSE] Sterownik Chrome skonfigurowany.")
    return driver


def wait_for_element(driver, by, value, timeout=10):
    """Pomocnicza funkcja oczekująca na element, aż stanie się klikalny."""
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
    except TimeoutException:
        log_with_color("ERROR", f"[PSE] Element {value} nie został znaleziony w ciągu {timeout} sekund.")
        return None


def fetch_pse_results(keywords):
    """Pobiera wyniki aukcji z witryny PSE."""
    driver = setup_driver()
    driver.get('https://przetargi.pse.pl/open-auctions.html')
    log_with_color("INFO", "[PSE] Otworzono stronę: https://przetargi.pse.pl/open-auctions.html")

    # Poczekaj na załadowanie strony
    time.sleep(3)

    results = []
    page = 1

    while True:
        log_with_color("INFO", f"[PSE] Przetwarzanie strony {page}")

        # Czekaj na wiersze tabeli
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/table/tbody/tr"))
        )
        log_with_color("INFO", f"[PSE] Znaleziono {len(rows)} wierszy na bieżącej stronie.")

        # Jeśli liczba wierszy jest mniejsza niż 25, to jest ostatnia strona
        if len(rows) < 25:
            log_with_color("INFO", "[PSE] To jest ostatnia strona.")
            break

        # Iterowanie po każdym wierszu, aby wyciągnąć szczegóły aukcji
        for row in rows:
            try:
                title_element = row.find_element(By.XPATH, ".//td[5]/div/a")
                title = title_element.text
                link = title_element.get_attribute("href")
                status_element = row.find_element(By.XPATH, ".//td[15]/div")
                status = status_element.text
                # Sprawdź, czy status to "Etap składania ofert" oraz czy tytuł pasuje do jakiegokolwiek słowa kluczowego
                if "Etap składania ofert" in status and any(
                        keyword.strip().lower() in title.lower() for keyword in keywords):
                    results.append([title, link, 'pse'])
                    log_with_color("INFO", f"[PSE] Dodano wynik: {title}")
            except NoSuchElementException:
                log_with_color("WARNING", "[PSE] Brak istotnych danych w tym wierszu.")

        # Szukaj przycisku "Next" i kliknij go, jeśli jest dostępny
        try:
            next_button = wait_for_element(driver, By.XPATH,
                                           "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div/div[3]/div/div/div[7]/em/button/span[2]")
            if next_button:
                next_button.click()  # Kliknij przycisk "Next"
                # Czekaj na załadowanie nowych wyników
                WebDriverWait(driver, 10).until(EC.staleness_of(rows[0]))  # Czekaj, aż wiersze się odświeżą
                page += 1
                log_with_color("INFO", "[PSE] Przejście do następnej strony.")
            else:
                log_with_color("INFO", "[PSE] Brak kolejnych stron.")
                break
        except TimeoutException:
            log_with_color("ERROR", "[PSE] Czas oczekiwania na przycisk 'Next' upłynął lub nie znaleziono przycisku.")
            break

    driver.quit()
    log_with_color("INFO", "[PSE] Zakończono przetwarzanie wyników. Przeglądarka została zamknięta.")
    return results


if __name__ == "__main__":
    pass
