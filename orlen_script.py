import time
import threading
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Klasa do logowania z kolorami
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


# Funkcja ustawiająca sterownik przeglądarki
def setup_driver():
    """
    Konfiguruje sterownik przeglądarki Chrome z odpowiednimi opcjami.

    Zwraca:
        webdriver.Chrome: Skonfigurowany sterownik Chrome.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Włącz tryb headless, jeśli chcesz działać w tle
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    log_with_color("INFO", "Sterownik Chrome skonfigurowany.")
    return driver


# Funkcja klikania przycisku "Pokaż więcej"
def click_show_more(driver, stop_event):
    """
    Wątek klikający przycisk "Pokaż więcej" na stronie Orlenu, aż wszystkie wyniki zostaną załadowane.

    Args:
        driver (webdriver.Chrome): Sterownik przeglądarki.
        stop_event (threading.Event): Zdarzenie do kontrolowania zatrzymania wątku.
    """
    iteration = 1
    while not stop_event.is_set():
        try:
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link-btn.link-load-more"))
            )
            log_with_color("INFO", f"ORLEN - Iteracja nr {iteration}: Kliknięto 'Pokaż więcej'.")
            iteration += 1
            show_more_button.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll na dół
            time.sleep(2)  # Opóźnienie dla załadowania kolejnych elementów
        except Exception as e:
            log_with_color("WARNING", "Brak przycisku 'Pokaż więcej' lub wszystko załadowane.")
            stop_event.set()


# Funkcja główna pobierająca wyniki
def fetch_orlen_results(keywords):
    """
    Pobiera wyniki z platformy Orlen na podstawie podanych słów kluczowych.

    Args:
        keywords (list[str]): Lista słów kluczowych do filtrowania wyników.

    Returns:
        list: Lista wyników w postaci [tytuł, link, źródło].
    """
    url = "https://connect.orlen.pl/servlet/HomeServlet?"
    driver = setup_driver()
    driver.get(url)
    log_with_color("INFO", f"Otworzono stronę: {url}")

    # Lista wyników
    results = []

    # Utwórz zdarzenie zatrzymania i wątek
    stop_event = threading.Event()
    click_thread = threading.Thread(target=click_show_more, args=(driver, stop_event))
    click_thread.start()

    try:
        while not stop_event.is_set():
            try:
                # Pobierz wszystkie elementy na stronie
                items = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.demand-item"))
                )

                for item in items:
                    title_element = item.find_element(By.CSS_SELECTOR, "a.demand-item-details-name")
                    title = title_element.text.strip()
                    link = title_element.get_attribute('href')

                    # Filtrowanie na podstawie słów kluczowych
                    if any(keyword.lower() in title.lower() for keyword in keywords):
                        results.append([title, link, 'ORLEN'])
                        log_with_color("INFO", f"Znaleziono: {title} - {link}")

                time.sleep(1)  # Krótkie opóźnienie przed następnym przetwarzaniem
            except Exception as e:
                log_with_color("ERROR", f"Błąd podczas przetwarzania: {e}")
                break
    finally:
        # Zakończ wątek i zamknij sterownik
        stop_event.set()
        click_thread.join()
        driver.quit()
        log_with_color("INFO", "Zamknięto przeglądarkę.")

    return results


# Główna sekcja skryptu
if __name__ == "__main__":
    pass
