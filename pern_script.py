import time

from selenium import webdriver
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
    """
    Konfiguruje sterownik przeglądarki Chrome.

    Zwraca:
        webdriver.Chrome: Sterownik Chrome z odpowiednimi opcjami.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tryb headless (odkomentuj, aby włączyć widoczność przeglądarki)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    log_with_color("INFO", "[PERN] Sterownik Chrome skonfigurowany.")
    return driver


def fetch_pern_results(keywords):
    """
    Pobiera wyniki z platformy PERN na podstawie podanych słów kluczowych.

    Args:
        keywords (list[str]): Lista słów kluczowych do wyszukiwania.

    Returns:
        list: Lista wyników w formacie [tytuł, link, źródło].
    """
    url = "https://platformazakupowa.pern.pl/adverts/NonAdvertActs.xhtml"
    driver = setup_driver()
    driver.get(url)
    log_with_color("INFO", f"[PERN] Otworzono stronę: {url}")

    results = []

    try:
        while True:
            try:
                # Oczekiwanie na załadowanie wierszy tabeli
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody.ui-datatable-data tr"))
                )
                rows = driver.find_elements(By.CSS_SELECTOR, "tbody.ui-datatable-data tr")

                # Przetwarzanie każdego wiersza
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        title = cells[1].text  # Tytuł ogłoszenia znajduje się w drugiej kolumnie
                        for keyword in keywords:
                            if keyword.lower() in title.lower():
                                # Pobieramy link do szczegółów ogłoszenia
                                details_link = cells[-1].find_element(By.TAG_NAME, "a").get_attribute("href")
                                results.append([title, details_link, 'PERN'])
                                log_with_color("INFO", f"[PERN] Dodano wynik: {title}")
                                break

                # Przejście do kolejnej strony
                next_button = driver.find_element(By.CSS_SELECTOR, "span.ui-paginator-next")
                if "ui-state-disabled" in next_button.get_attribute("class"):
                    log_with_color("WARNING", "[PERN] Brak kolejnej strony. Kończenie przeszukiwania.")
                    break
                driver.execute_script("arguments[0].click();", next_button)
                log_with_color("INFO", "[PERN] Przejście do kolejnej strony.")
                time.sleep(2)

            except Exception as e:
                break

    finally:
        driver.quit()
        log_with_color("INFO", "[PERN] Przeglądarka została zamknięta.")

    return results


if __name__ == "__main__":
    pass
