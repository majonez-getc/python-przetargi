import csv
import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
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


# version 1.0
# Funkcja do zaktualizowania postępu
def update_progress(progress_var, current, total):
    progress_var.set((current + 1) / total * 100)

# Funkcja do mierzenia czasu wykonania
def measure_time(func, *args, **kwargs):
    start_time = time.time()  # Zaczynamy mierzyć czas
    result = func(*args, **kwargs)  # Wywołanie funkcji
    end_time = time.time()  # Zatrzymujemy czas
    execution_time = end_time - start_time  # Czas wykonania funkcji
    return result, execution_time

def run_search(keywords, selected_sources, progress_var, on_finish):
    try:
        all_results = []
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

        total_sources = len(selected_sources)
        results_per_source = {}
        seen_links = set()  # Zbiór do śledzenia unikalnych linków
        source_times = {}  # Słownik przechowujący czasy wykonania poszczególnych źródeł

        # Przetwarzanie wyników źródeł jeden po drugim
        for idx, source in enumerate(selected_sources):
            # Mierzymy czas wykonania każdej funkcji
            source_results, execution_time = measure_time(source_functions[source], keywords)
            source_times[source] = execution_time  # Zapisujemy czas wykonania
            results_per_source[source] = source_results
            for result in source_results:
                title, link, source_name = result
                if link not in seen_links:  # Sprawdzamy, czy link już się pojawił
                    seen_links.add(link)  # Dodajemy link do zbioru
                    all_results.append(result)

            update_progress(progress_var, idx, total_sources)

        # Zapisanie wyników do pliku CSV
        filename = "combined_results.csv"
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Tytuł", "Link", "Źródło"])
            for result in all_results:
                writer.writerow(result)

        # Wyświetlamy czasy wykonania poszczególnych źródeł
        for source, exec_time in source_times.items():
            print(f"Źródło {source} wykonało się w {exec_time:.2f} sekund.")

        on_finish(all_results)

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem: {str(e)}")
    finally:
        progress_var.set(0)  # Resetowanie paska postępu po zakończeniu


def main():
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

    # Pasek postępu
    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, mode="determinate")
    progress_bar.grid(row=row, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
    row += 1

    # Funkcja uruchamiająca wyszukiwanie
    def on_search(Test_mode=False):
        if Test_mode:
            print("Test mode")
            keywords = ['usł','bud']  # Można zmienić na dowolne dane
            selected_sources = ["orlen"]
        else:
            keywords = [kw.strip() for kw in keywords_entry.get().split(',') if kw.strip()]
            selected_sources = [source for source, var in source_vars.items() if var.get()]

        if not keywords:
            messagebox.showwarning("Brak słów kluczowych", "Wprowadź przynajmniej jedno słowo kluczowe.")
            return
        if not selected_sources:
            messagebox.showwarning("Brak źródeł", "Wybierz przynajmniej jedno źródło.")
            return

        def display_results(results):
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

        progress_var.set(0)

        # Uruchomienie wyszukiwania w głównym wątku
        run_search(keywords, selected_sources, progress_var, display_results)

    # Przycisk wyszukiwania
    search_button = ttk.Button(root, text="Szukaj", command=lambda: on_search(Test_mode=False))
    search_button.grid(row=row, column=0, columnspan=2, pady=(10, 0))

    # Zatrzymanie wątków podczas zamykania okna - FORCOWNE ZAMKNIĘCIE
    def on_close():
        os._exit(1)  # Natychmiastowe zakończenie programu

    root.protocol("WM_DELETE_WINDOW", on_close)  # Przechwycenie zamykania okna

    root.mainloop()

if __name__ == "__main__":
    if (os.path.exists("combined_results.csv")):
        os.remove("combined_results.csv")
    main()
