import csv
import tkinter as tk
from tkinter import ttk, messagebox
import threading
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

# Funkcja do zaktualizowania postępu
def update_progress(progress_var, current, total):
    progress_var.set((current + 1) / total * 100)

# Zmiana na ThreadPoolExecutor dla równoczesnych zadań
def run_search(keywords, selected_sources, progress_var, on_finish):
    try:
        all_results = []
        source_functions = {
            "amwsinevia": fetch_amwsinevia_results,
            "biparp": fetch_biparp_results,
            "biznespolska": fetch_biznespolska_results,
            "energa": fetch_energa_results,
            "oneplace": fetch_oneplace_results,
            "orlen": fetch_orlen_results,
            "pern": fetch_pern_results,
            "pkp": fetch_pkp_results,
            "pse": fetch_pse_results,
            "tauron": fetch_tauron_results,
        }

        total_sources = len(selected_sources)
        results_per_source = {}

        with ThreadPoolExecutor(max_workers=len(selected_sources)) as executor:
            # Używamy map, aby wykonać funkcje równolegle
            futures = {
                executor.submit(source_functions[source], keywords): source for source in selected_sources
            }

            # Zbieramy wyniki i aktualizujemy pasek postępu
            for idx, future in enumerate(futures):
                source_results = future.result()
                results_per_source[futures[future]] = source_results
                all_results.extend(source_results)
                update_progress(progress_var, idx, total_sources)

        # Zapisz wyniki do pliku CSV
        with open("combined_results.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Tytuł", "Link", "Źródło"])
            for source, results in results_per_source.items():
                for result in results:
                    writer.writerow([result[0], result[1], source])

        on_finish(all_results)

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem: {str(e)}")
    finally:
        progress_var.set(0)  # Resetowanie paska postępu po zakończeniu

def main(Test_mode = False):
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
    def on_search(Test_mode = False):
        if Test_mode:
            keywords = ['usługi']
            selected_sources = ["biznespolska"]
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
        threading.Thread(
            target=run_search, args=(keywords, selected_sources, progress_var, display_results), daemon=True
        ).start()

    # Przycisk wyszukiwania
    search_button = ttk.Button(root, text="Szukaj", command=on_search(Test_mode))
    search_button.grid(row=row, column=0, columnspan=2, pady=(10, 0))

    root.mainloop()

if __name__ == "__main__":
    main(Test_mode=True)
