import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Funkcja ustawiająca sterownik przeglądarki
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Funkcja klikania przycisku "Pokaż więcej" (wątek)
def click_show_more(driver, stop_event):
    i = 1
    while not stop_event.is_set():
        try:
            # Czekaj, aż przycisk "Pokaż więcej" będzie klikniony
            show_more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link-btn.link-load-more"))
            )
            print(f"ORLEN iteracja nr {i}")
            i += 1
            show_more_button.click()  # Kliknięcie przycisku
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Przewijanie strony w dół
            time.sleep(2)  # Krótkie opóźnienie dla załadowania nowych elementów
        except:
            # Jeśli przycisk "Pokaż więcej" nie jest już dostępny, kończymy wątek
            stop_event.set()

# Funkcja główna pobierająca wyniki (przetwarzanie wyników i zbieranie danych)
def fetch_orlen_results(keywords):
    url = "https://connect.orlen.pl/servlet/HomeServlet?"
    driver = setup_driver()
    driver.get(url)

    stop_event = threading.Event()

    # Uruchomienie wątku, który będzie klikał przycisk "Pokaż więcej"
    click_thread = threading.Thread(target=click_show_more, args=(driver, stop_event))
    click_thread.start()

    # Lista do przechowywania wyników
    results = []
    try:
        while not stop_event.is_set():
            # Czekaj na załadowanie elementów
            items = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.demand-item"))
            )
            for item in items:
                # Pobranie tytułu oferty i linku
                title_element = item.find_element(By.CSS_SELECTOR, "a.demand-item-details-name")
                title = title_element.text
                link = title_element.get_attribute('href')
                # Sprawdzenie słów kluczowych
                for keyword in keywords:
                    if keyword.lower() in title.lower():
                        results.append([title, link, 'orlen'])
                        break
            time.sleep(1)  # Zamiast bezustannego przetwarzania co 0.5 sekundy
    except Exception as e:
        print(f"Error: {e}")

    # Poczekaj, aż wątek zakończy swoje działanie
    click_thread.join()
    driver.quit()

    return results

# Przykładowe wywołanie
if __name__ == "__main__":
    keywords = ['energia', 'gaz', 'woda']
    results = fetch_orlen_results(keywords)
    for result in results:
        print(result)  # Można tu zapisać wyniki do pliku lub bazy danych
