﻿# python-przetargi

Projekt "python-przetargi" to aplikacja umożliwiająca wyszukiwanie ogłoszeń o przetargach w różnych źródłach internetowych. Program jest napisany w Pythonie i wykorzystuje bibliotekę Tkinter do stworzenia interfejsu graficznego, a także mechanizmy wielowątkowości/współbieżności (np. `ThreadPoolExecutor`) dla równoległego pobierania danych z różnych serwisów.

## Funkcjonalności

Aplikacja oferuje następujące funkcje:

1.  **Wyszukiwanie przetargów:** Wyszukiwanie ogłoszeń na podstawie wprowadzonych słów kluczowych.
2.  **Wybór źródeł:** Możliwość wyboru źródeł, z których mają być pobierane wyniki. Obsługiwane źródła to:
    *   amwsinevia
    *   biparp
    *   biznespolska
    *   energa
    *   oneplace
    *   pern
    *   pkp
    *   pse
    *   tauron
    *   orlen
3.  **Równoległe zapytania:** Wykonywanie zapytań do wybranych źródeł jednocześnie, co znacząco przyspiesza proces pobierania wyników.
4.  **Eksport wyników:** Zapisywanie wyników wyszukiwania do plików CSV lub Excel.
5.  **Wyświetlanie wyników:** Prezentacja wyników w interfejsie graficznym w postaci tabeli.

## Jak uruchomić

### Wymagania

Do uruchomienia aplikacji wymagane jest zainstalowanie następujących bibliotek Pythona. Można to zrobić za pomocą menedżera pakietów `pip`:

```bash
pip install pandas openpyxl
```

*   `pandas`: Biblioteka do analizy i manipulacji danymi, używana do eksportu wyników do formatu Excel i CSV.
*   `openpyxl`: Biblioteka do odczytu i zapisu plików Excel (xlsx).

### Uruchomienie

1.  Sklonuj repozytorium projektu na swój komputer:

    ```bash
    git clone <adres_repozytorium>
    ```

2.  Przejdź do katalogu z projektem:

    ```bash
    cd python-przetargi
    ```

3.  Zainstaluj wymagane biblioteki (jeśli jeszcze nie zostały zainstalowane):

    ```bash
    pip install pandas openpyxl
    ```

4.  Uruchom skrypt główny aplikacji:

    ```bash
    python AIO.py
    ```

    Spowoduje to uruchomienie graficznego interfejsu użytkownika (GUI).

### Obsługa interfejsu GUI

W oknie aplikacji dostępne są następujące opcje:

*   **Słowa kluczowe:** Pole tekstowe, w którym należy wprowadzić szukane frazy. Słowa kluczowe można oddzielać przecinkami (np. `usługa budowlana, przetarg`).
*   **Źródła:** Lista wyboru (checkboxy), pozwalająca na zaznaczenie źródeł, z których mają być pobierane dane.
*   **Format eksportu:** Wybór formatu pliku, do którego zostaną zapisane wyniki (CSV lub Excel).
*   **Szukaj:** Przycisk uruchamiający proces wyszukiwania.

Po zakończeniu wyszukiwania, wyniki zostaną wyświetlone w tabeli w interfejsie oraz zapisane w wybranym formacie na dysku (w tym samym katalogu co skrypt).

## Opis działania

Aplikacja działa w następujący sposób:

1.  Interfejs graficzny (GUI) został stworzony przy użyciu biblioteki `Tkinter`.
2.  Użytkownik wprowadza słowa kluczowe i wybiera źródła, które mają być przeszukiwane.
3.  Wyszukiwanie odbywa się równolegle dla każdego wybranego źródła, co znacząco skraca czas oczekiwania na wyniki. Do realizacji współbieżności używany jest np. `ThreadPoolExecutor`.
4.  Wyniki z poszczególnych źródeł są zbierane, formatowane i wyświetlane w tabeli w interfejsie aplikacji.
5.  Użytkownik ma możliwość zapisania zebranych danych do pliku w formacie CSV lub Excel.

## Zakończenie

Dzięki równoległemu przetwarzaniu zapytań, aplikacja efektywnie pobiera dane z wielu źródeł. Wyniki można przeglądać w aplikacji oraz zapisać do pliku w celu dalszej analizy.

## Licencja

Projekt jest udostępniany na licencji MIT.

## Autorzy

*   [Majonez-getc](https://github.com/majonez-getc)

