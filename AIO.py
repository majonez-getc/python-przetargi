import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
import pandas as pd
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from amwsinevia_script import fetch_amwsinevia_results
from biparp_script import fetch_biparp_results
from biznespolska_script import fetch_biznespolska_results
from energa_script import fetch_energa_results
from oneplace_script import fetch_oneplace_results
from orlen_script import fetch_orlen_results
from pern_script import fetch_pern_results
from pkp_script import fetch_pkp_results
from pse_script import fetch_pse_results
from tauron_script import fetch_tauron_results


# Kolorowe logowanie
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


# Funkcja pomocnicza do przetwarzania wyników
def fetch_source_data(source, keywords, seen_links, all_results, result_queue):
    source_functions = {
        "amwsinevia": fetch_amwsinevia_results,
        "biparp": fetch_biparp_results,
        "biznespolska": fetch_biznespolska_results,
        "energa": fetch_energa_results,
        "oneplace": fetch_oneplace_results,
        "pern": fetch_pern_results,
        "pkp": fetch_pkp_results,
        "pse": fetch_pse_results,
        "tauron": fetch_tauron_results,
        "orlen": fetch_orlen_results,
    }

    try:
        log_with_color("INFO", f"[{source}] Rozpoczynam pobieranie wyników...")
        source_results = source_functions[source](keywords)
        for result in source_results:
            title, link, source_name = result
            if link not in seen_links:
                seen_links.add(link)
                all_results.append(result)
        result_queue.put((source, len(source_results)))  # Przekazujemy dane do głównego wątku
        log_with_color("INFO", f"[{source}] Pobieranie zakończone. Znaleziono {len(source_results)} wyników.")
    except Exception as e:
        log_with_color("ERROR", f"[{source}] Błąd podczas pobierania wyników: {e}")


# Funkcja do równoległego uruchamiania zapytań
def run_search_parallel(keywords, selected_sources, result_queue, on_finish):
    try:
        all_results = []
        seen_links = set()  # Zbiór do śledzenia unikalnych linków

        # Uruchamiamy równoległe zapytania
        with ThreadPoolExecutor() as executor:
            for source in selected_sources:
                executor.submit(fetch_source_data, source, keywords, seen_links, all_results, result_queue)

        # Zakończenie po przetworzeniu wszystkich zapytań
        on_finish(all_results)  # Pokazujemy wyniki po zakończeniu

    except Exception as e:
        log_with_color("ERROR", f"Błąd: {str(e)}")
        messagebox.showerror("Błąd", f"Wystąpił problem: {str(e)}")


# Funkcja zapisująca wyniki do pliku CSV
def save_results_to_csv(results, filename="combined_results.csv"):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Tytuł", "Link", "Źródło"])  # Nagłówki
            for result in results:
                writer.writerow(result)
        log_with_color("INFO", "Wyniki zapisane do pliku CSV.")
    except Exception as e:
        log_with_color("ERROR", f"Błąd przy zapisywaniu wyników: {e}")


# Funkcja zapisująca wyniki do pliku Excel
def save_results_to_excel(results, filename="combined_results.xlsx"):
    try:
        df = pd.DataFrame(results, columns=["Tytuł", "Link", "Źródło"])
        df.to_excel(filename, index=False, engine='openpyxl')
        log_with_color("INFO", "Wyniki zapisane do pliku Excel.")
    except Exception as e:
        log_with_color("ERROR", f"Błąd przy zapisywaniu wyników: {e}")


# Funkcja wyświetlająca wyniki w nowym oknie
def display_results(results, export_format):
    if export_format == "CSV":
        save_results_to_csv(results)  # Zapisz wyniki do pliku CSV
    elif export_format == "Excel":
        save_results_to_excel(results)  # Zapisz wyniki do pliku Excel

    results_window = tk.Toplevel()
    results_window.title("Wyniki wyszukiwania")

    tree = ttk.Treeview(results_window, columns=("Tytuł", "Link", "Źródło"), show="headings")
    tree.heading("Tytuł", text="Tytuł")
    tree.heading("Link", text="Link")
    tree.heading("Źródło", text="Źródło")
    tree.pack(fill=tk.BOTH, expand=True)

    for result in results:
        tree.insert("", tk.END, values=result)

    close_button = ttk.Button(results_window, text="Zamknij", command=results_window.destroy)
    close_button.pack(pady=5)


# Funkcja główna programu
def main():
    global root
    root = tk.Tk()
    root.title("Przetargi Search")

    # GUI - Słowa kluczowe
    keywords_label = ttk.Label(root, text="Słowa kluczowe (oddzielone przecinkami):")
    keywords_label.grid(row=0, column=0, sticky=tk.W)

    keywords_entry = ttk.Entry(root, width=50)
    keywords_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

    # Tworzenie dynamicznie checkboxów dla źródeł
    source_vars = {}
    sources = ["amwsinevia", "biparp", "biznespolska", "energa", "oneplace", "pern", "pkp", "pse", "tauron", "orlen"]
    row = 1
    for source in sources:
        source_vars[source] = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(root, text=source, variable=source_vars[source])
        checkbox.grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1

    # Opcje eksportu
    export_var = tk.StringVar(value="CSV")  # Domyślny format to CSV
    export_csv_radio = ttk.Radiobutton(root, text="CSV", variable=export_var, value="CSV")
    export_csv_radio.grid(row=row, column=0, sticky=tk.W)
    export_excel_radio = ttk.Radiobutton(root, text="Excel", variable=export_var, value="Excel")
    export_excel_radio.grid(row=row, column=1, sticky=tk.W)
    row += 1

    # Funkcja uruchamiająca wyszukiwanie
    def on_search(Test_mode=False):
        if Test_mode:
            log_with_color("INFO", "Tryb testowy włączony.")
            keywords = ['usł', 'bud']  # Można zmienić na dowolne dane
            selected_sources = ["amwsinevia"]
        else:
            keywords = [kw.strip() for kw in keywords_entry.get().split(',') if kw.strip()]
            selected_sources = [source for source, var in source_vars.items() if var.get()]

        if not keywords:
            messagebox.showwarning("Brak słów kluczowych", "Wprowadź przynajmniej jedno słowo kluczowe.")
            return
        if not selected_sources:
            messagebox.showwarning("Brak źródeł", "Wybierz przynajmniej jedno źródło.")
            return

        result_queue = Queue()  # Kolejka do przekazywania wyników

        # Uruchomienie wyszukiwania w osobnym wątku
        search_thread = threading.Thread(target=run_search_parallel, args=(
        keywords, selected_sources, result_queue, lambda results: display_results(results, export_var.get())))
        search_thread.start()

    # Przycisk wyszukiwania
    search_button = ttk.Button(root, text="Szukaj", command=lambda: on_search(Test_mode=False))
    search_button.grid(row=row, column=0, columnspan=2, pady=(10, 0))

    # Zatrzymanie wątków podczas zamykania okna - FORCOWNE ZAMKNIĘCIE
    def on_close():
        os._exit(1)  # Natychmiastowe zakończenie programu

    root.protocol("WM_DELETE_WINDOW", on_close)  # Przechwycenie zamykania okna

    root.mainloop()


if __name__ == "__main__":
    if os.path.exists("combined_results.csv"):
        os.remove("combined_results.csv")
    main()
