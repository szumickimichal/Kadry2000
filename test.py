import sqlite3
import pandas as pd
from datetime import datetime
from constants import *

# df = pd.DataFrame(columns=['Data', 'Imie', 'Nazwisko', 'GodzinaRozpoczecia', 'GodzinaZakonczenia', 'Tryb'])

#
# def add_rows(df, table_name):
#     # Połącz z bazą danych
#     conn = sqlite3.connect(DATA_BASE_FILE_DIR)
#     # Zapisz DataFrame do bazy danych
#     df.to_sql(table_name, conn, if_exists='append', index=False)
#     # Zamknij połączenie
#     conn.close()


def add_rows_to_obecnosc_table(df):
    conn = sqlite3.connect(DATA_BASE_FILE_DIR)

    for index, row in df.iterrows():
        # Sprawdzenie, czy kombinacja już istnieje w tabeli
        existing_row = conn.execute(f"SELECT * FROM {OBECNOSC_TABLE_NAME} WHERE Data = ? AND Imie = ? AND Nazwisko = ?",
                                    (row['Data'], row['Imie'], row['Nazwisko'])).fetchone()

        # Jeśli kombinacja istnieje, zaktualizuj wiersz
        if existing_row is not None:
            conn.execute(f"UPDATE {OBECNOSC_TABLE_NAME} SET GodzinaRozpoczecia = ?, GodzinaZakonczenia = ?, Tryb = ? WHERE Data = ? AND Imie = ? AND Nazwisko = ?",
                         (row['GodzinaRozpoczecia'], row['GodzinaZakonczenia'], row['Tryb'], row['Data'], row['Imie'], row['Nazwisko']))
        else:
            # Jeśli kombinacja nie istnieje, dodaj nowy wiersz
            row.to_frame().T.to_sql(OBECNOSC_TABLE_NAME, conn, if_exists='append', index=False)

    conn.commit()
    conn.close()


def add_rows(df, table_name):
    conn = sqlite3.connect(DATA_BASE_FILE_DIR)

    df.to_sql(table_name, conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

def read_table(table_name, where=""):
    # Połącz z bazą danych
    conn = sqlite3.connect(DATA_BASE_FILE_DIR)

    # Wykonaj zapytanie SQL i wczytaj wyniki do DataFrame
    if not where:
        query = f'SELECT * FROM {table_name}'
    else:
        query = f'SELECT * FROM {table_name} WHERE {where}'
    df = pd.read_sql_query(query, conn)
    asd = df["Tryb"].groupby([df['Imie'], df['Nazwisko'], df['Tryb']]).count()
    asd = asd.rename('Liczba')

    asd = asd.reset_index()

    pivot_df = asd.pivot(index=['Imie', 'Nazwisko'], columns='Tryb', values='Liczba').reset_index()

    print(pivot_df)
    # asd = asd.to_frame()

    # Zamknij połączenie
    conn.close()

    # Wyświetl DataFrame
    print(df)


def all_days_except_weekends(start_date, end_date):
    import pandas as pd
    # Utworzenie zakresu dat
    date_range = pd.date_range(start=start_date, end=end_date)

    # Wybór tylko tych dat, które nie są weekendami (poniedziałek oznaczony jako 0, a niedziela jako 6)
    date_range_except_weekends = date_range[date_range.weekday < 5]
    # Utworzenie DataFrame
    values = {'Data': date_range_except_weekends, 'Imie': "Jan", 'Nazwisko': "Kowalski", 'GodzinaRozpoczecia': '11:00', 'GodzinaZakonczenia': '8:00', 'Tryb': 'A'}
    df = pd.DataFrame(values)
    df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')

    add_rows_to_obecnosc_table(df)

# all_days_except_weekends(pd.to_datetime('2024-02-01'), pd.to_datetime('2024-02-20'))

# df = pd.DataFrame({'Imie': ["Jan", "AAA"], 'Nazwisko': ["Kowalski", "aad"], 'Stanowisko': ['11:00', "rolnik"]})
# add_rows(df, PRACOWNICY_TABLE_NAME)
read_table(OBECNOSC_TABLE_NAME)

