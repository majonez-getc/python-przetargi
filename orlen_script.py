import time
import csv
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def setup_driver():
    chrome_options = Options()
    # Uncomment the next line to enable headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def fetch_orlen_results(keywords):
    url = "https://connect.orlen.pl/servlet/HomeServlet?"
    driver = setup_driver()
    driver.get(url)

    # Poczekaj na załadowanie strony
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "section.demand-item"))
    )

    # Zamiast klikania "Pokaż więcej", wykonujemy od razu zapytanie AJAX
    # Przypuszczam, że AJAX wywołuje metodę self.getDemands w backendzie
    # Będziemy musieli symulować tę metodę lub po prostu załadować wszystkie dane.

    # Poczekaj aż załaduje się cała zawartość
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    results = []
    items = driver.find_elements(By.CSS_SELECTOR, "section.demand-item")

    # Przechodzimy po wszystkich elementach
    for item in items:
        title_element = item.find_element(By.CSS_SELECTOR, "a.demand-item-details-name")
        title = title_element.text
        link = title_element.get_attribute('href')
        for keyword in keywords:
            if keyword.lower() in title.lower():
                results.append([title, link, 'orlen'])
                break

    # Przewiń do góry strony, by ułatwić załadowanie pełnych wyników
    driver.execute_script("window.scrollTo(0, 0);")

    driver.quit()

    # Zwróć wyniki
    print(results)
    return results


if __name__ == "__main__":
    keywords = ['praca', 'nowe oferty']  # Przykładowe słowa kluczowe
    results = fetch_orlen_results(keywords)
