#ONEPLACE
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
    log_with_color("INFO", "[ONEPLACE] Sterownik Chrome skonfigurowany.")
    return driver


def fetch_oneplace_results(keywords):
    """
    Pobiera oferty z OnePlace, filtrując je na podstawie słów kluczowych.

    Args:
        keywords (list[str]): Lista słów kluczowych do filtrowania ofert.

    Returns:
        list: Wyniki w postaci listy [tytuł, link, źródło].
    """
    url = "https://oneplace.marketplanet.pl/zapytania-ofertowe-przetargi/-/rfp/cat/11035/elektroenergetyka?_7_WAR_organizationnoticeportlet_cur=1"
    driver = setup_driver()
    results = []
    keywords = set(keyword.strip().lower() for keyword in keywords)

    try:
        driver.get(url)
        log_with_color("INFO", f"[ONEPLACE] Otworzono stronę {url}")

        while True:
            try:
                # Poczekaj na załadowanie ofert
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.tiles"))
                )
                log_with_color("INFO", "[ONEPLACE] Załadowano oferty na bieżącej stronie.")

                # Pobieranie ofert
                articles = driver.find_elements(By.CSS_SELECTOR, "div.row.tiles article")
                for article in articles:
                    title_element = article.find_element(By.CSS_SELECTOR, "h3.title")
                    title = title_element.text.strip().lower()
                    link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                    # Filtracja na podstawie słów kluczowych
                    if any(keyword in title for keyword in keywords):
                        results.append([title, link, 'ONEPLACE'])

                # Przejdź do następnej strony, jeśli jest dostępna
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
                    next_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.row.tiles"))
                    )
                    log_with_color("INFO", "[ONEPLACE] Przejście do następnej strony.")
                except Exception as e:
                    log_with_color("WARNING", "[ONEPLACE] Nie znaleziono przycisku 'Next' lub brak kolejnych stron.")
                    break
            except Exception as e:
                log_with_color("ERROR", f"[ONEPLACE] Błąd podczas przetwarzania strony: {e}")
                break
    finally:
        driver.quit()
        log_with_color("INFO", "[ONEPLACE] Zamknięto sterownik przeglądarki.")

    return results


if __name__ == "__main__":
    pass
