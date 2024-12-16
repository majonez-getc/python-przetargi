from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Kolory ANSI do terminala
class LogColors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

# Funkcja do kolorowego logowania
def log_with_color(level, msg):
    if level == "INFO":
        print(f"{LogColors.GREEN}{msg}{LogColors.RESET}")
    elif level == "WARNING":
        print(f"{LogColors.YELLOW}{msg}{LogColors.RESET}")
    elif level == "ERROR":
        print(f"{LogColors.RED}{msg}{LogColors.RESET}")

def setup_driver():
    """
    Funkcja konfigurująca sterownik Chrome z opcjami.
    """
    log_with_color("INFO", "[BiznesPolska] Konfiguracja przeglądarki...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    log_with_color("INFO", "[BiznesPolska] Przeglądarka uruchomiona.")
    return driver

def contains_keywords(title, keywords):
    """
    Sprawdza, czy tytuł zawiera przynajmniej jedno słowo kluczowe.
    """
    title = title.lower()
    return any(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', title) for keyword in keywords)

def fetch_biznespolska_results(keywords):
    """
    Pobiera oferty z serwisu BiznesPolska.
    """
    url = 'https://www.biznes-polska.pl/oferty/'
    log_with_color("INFO", "[BiznesPolska] Rozpoczynam pobieranie wyników...")
    driver = setup_driver()
    driver.get(url)

    results = []
    page_number = 1

    while True:
        log_with_color("INFO", f"[BiznesPolska] Przetwarzanie strony {page_number}...")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
            )
            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            log_with_color("INFO", f"[BiznesPolska] Znaleziono {len(rows)} ofert na stronie {page_number}.")

            for row in rows:
                try:
                    title_element = row.find_element(By.CSS_SELECTOR, "a.title")
                    title = title_element.text
                    link = title_element.get_attribute("href")

                    if contains_keywords(title, keywords):
                        results.append([title, link, "BIZNESPOLSKA"])
                        log_with_color("INFO", f"[BiznesPolska] Dodano ofertę: {title}")
                except Exception as e:
                    continue

            next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.next")
            if next_buttons and next_buttons[0].is_displayed():
                driver.execute_script("arguments[0].click();", next_buttons[0])
                page_number += 1
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
                )
            else:
                log_with_color("INFO", "[BiznesPolska] Brak kolejnych stron. Zakończono przetwarzanie.")
                break
        except Exception as e:
            log_with_color("ERROR", f"[BiznesPolska] Wystąpił błąd lub brak kolejnych stron: {e}")
            break

    driver.quit()
    log_with_color("INFO", "[BiznesPolska] Przeglądarka zamknięta.")
    return results

if __name__ == "__main__":
    keywords = ["przetarg", "aukcja", "oferta"]  # Przykładowe słowa kluczowe
    log_with_color("INFO", "[BiznesPolska] Rozpoczynam wyszukiwanie wyników...")
    results = fetch_biznespolska_results(keywords)

    if results:
        log_with_color("INFO", f"[BiznesPolska] Znaleziono {len(results)} wyników.")
        for result in results:
            log_with_color("INFO", f"Title: {result[0]}, Link: {result[1]}, Source: {result[2]}")
    else:
        log_with_color("WARNING", "[BiznesPolska] Nie znaleziono wyników.")
