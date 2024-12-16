import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


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


def contains_keywords(title, keywords):
    """
    Sprawdza, czy tytuł zawiera którekolwiek z podanych słów kluczowych.
    """
    for keyword in keywords:
        if keyword.lower().strip() in title.lower():
            return True
    return False


def fetch_energa_results(keywords):
    """
    Pobiera oferty ze strony Energa.
    """
    results = []

    # Konfiguracja przeglądarki Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tryb headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Otwieranie strony
        driver.get("https://energaostroleka.logintrade.net/portal,listaZapytaniaOfertowe.html?page=1&itemsperpage=9999")
        log_with_color("INFO", "[Energa] Strona otwarta.")

        # Klikanie rozwijanego menu
        dropdown_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.multiselect.dropdown-toggle"))
        )
        dropdown_button.click()
        log_with_color("INFO", "[Energa] Kliknięto menu rozwijane.")

        # Odznaczanie wybranych checkboxów
        checkbox_values_to_deselect = ["w_realizacji_po_terminie", "ocena_ofert", "zakonczone", "anulowane"]
        for value in checkbox_values_to_deselect:
            try:
                checkbox = driver.find_element(By.CSS_SELECTOR, f"input[type='checkbox'][value='{value}']")
                if checkbox.is_selected():
                    checkbox.click()
                    log_with_color("INFO", f"[Energa] Odznaczono checkbox: {value}")
                else:
                    log_with_color("INFO", f"[Energa] Checkbox '{value}' już był odznaczony.")
            except Exception as e:
                log_with_color("WARNING", f"[Energa] Nie można znaleźć lub odznaczyć checkboxa '{value}': {e}")

        # Kliknięcie przycisku "Szukaj"
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.searchButton a[onclick*='document.zapytaniaSearchForm.submit()']"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        log_with_color("INFO", "[Energa] Kliknięto przycisk 'Szukaj'.")

        # Czekanie na wyniki
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr"))
            )
            log_with_color("INFO", "[Energa] Wyniki załadowane.")
        except TimeoutException:
            log_with_color("ERROR", "[Energa] Timeout: Wyniki nie załadowały się na czas.")
            with open('error_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            return results  # Zwracanie pustych wyników w przypadku timeoutu

        # Pobieranie wierszy z tabeli
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        log_with_color("INFO", f"[Energa] Znaleziono {len(rows)} wierszy.")

        if not rows:
            log_with_color("WARNING", "[Energa] Nie znaleziono żadnych ofert.")
            return results

        for idx, row in enumerate(rows, start=1):
            try:
                title_element = row.find_element(By.CSS_SELECTOR, 'a.name')
                title = title_element.text
                link = title_element.get_attribute('href')

                if title and contains_keywords(title, keywords):
                    results.append([title.strip(), link, "ENERGA"])
                    log_with_color("INFO", f"[Energa] Dodano ofertę: {title}")
            except Exception as e:
                log_with_color("INFO", f"[Energa] Błąd przetwarzania wiersza {idx}")

    finally:
        driver.quit()
        log_with_color("INFO", "[Energa] Przeglądarka zamknięta.")

    return results


if __name__ == "__main__":
    pass
    #wyjebac webmanager