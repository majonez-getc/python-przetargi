import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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


def contains_keywords(title, keywords):
    """
    Sprawdza, czy w tytule występuje któreś ze słów kluczowych.

    Args:
        title (str): Tytuł ogłoszenia.
        keywords (list): Lista słów kluczowych do wyszukania.

    Returns:
        bool: True, jeśli przynajmniej jedno słowo kluczowe znajduje się w tytule.
    """
    return any(keyword.lower().strip() in title.lower() for keyword in keywords)


def setup_driver():
    """
    Konfiguruje i uruchamia sterownik Chrome z odpowiednimi opcjami.

    Returns:
        webdriver.Chrome: Obiekt sterownika przeglądarki Chrome.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tryb bez interfejsu
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    webdriver_service = ChromeService(ChromeDriverManager().install())
    log_with_color("INFO", "[PKP] Sterownik Chrome skonfigurowany.")
    return webdriver.Chrome(service=webdriver_service, options=chrome_options)


def fetch_pkp_results(keywords):
    """
    Przeszukuje stronę PKP w celu znalezienia ogłoszeń pasujących do słów kluczowych.

    Args:
        keywords (list): Lista słów kluczowych do wyszukania.

    Returns:
        list: Lista wyników w formacie [tytuł, link, źródło].
    """
    url = "https://platformazakupowa.plk-sa.pl/app/demand/notice/public/current/list?USER_MENU_HOVER=currentNoticeList"
    results = []
    driver = setup_driver()

    try:
        # Otwórz stronę PKP
        driver.get(url)
        log_with_color("INFO", f"[PKP] Otworzono stronę: {url}")

        # Wybór opcji "Wszystkie" w menu rozwijanym
        select_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "GD_pagesize"))
        )
        select_element.click()
        all_option = driver.find_element(By.CSS_SELECTOR, "option[value='99999999']")
        all_option.click()
        log_with_color("INFO", "[PKP] Wybrano opcję 'Wszystkie' w menu rozwijanym.")

        # Kliknij przycisk potwierdzenia, jeśli się pojawi
        try:
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal-button.swal-button--confirm"))
            )
            confirm_button.click()
            log_with_color("INFO", "[PKP] Potwierdzono wyświetlenie większej liczby wyników.")
        except:
            log_with_color("WARNING", "[PKP] Przyciski potwierdzenia nie były dostępne.")

        # Czekaj na załadowanie wyników
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.dataRow"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.dataRow")
        log_with_color("INFO", f"[PKP] Znaleziono {len(rows)} wierszy z wynikami.")

        # Filtruj dane i dodaj wyniki
        for row in rows:
            title_element = row.find_element(By.CSS_SELECTOR, "td.long.col-1")
            title = title_element.text.strip()
            index_id = row.get_attribute("id")

            if contains_keywords(title, keywords):
                link = f"https://platformazakupowa.plk-sa.pl/app/demand/notice/public/{index_id}/details"
                results.append([title, link, "PKP"])
                log_with_color("INFO", f"[PKP] Dodano wynik: {title}")

    except Exception as e:
        log_with_color("ERROR", "[PKP] Wystąpił błąd podczas przetwarzania strony.")
        traceback.print_exc()
    finally:
        driver.quit()
        log_with_color("INFO", "[PKP] Zamknięto sterownik przeglądarki.")

    return results


if __name__ == "__main__":
    pass
