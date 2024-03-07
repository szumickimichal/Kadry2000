import sqlite3
from constants import *


def create_obecnosc_table():
    # Połącz z bazą danych (jeśli nie istnieje, zostanie utworzona)
    conn = sqlite3.connect(DATA_BASE_FILE_DIR)

    # Utwórz kursor do wykonywania poleceń SQL
    cursor = conn.cursor()

    cursor.execute('DROP TABLE Obecnosc')

    # Utwórz tabelę pracowników z ograniczeniami na długość tekstu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Obecnosc (
            Data TEXT,
            Imie TEXT CHECK(LENGTH(Imie) <= 50),
            Nazwisko TEXT CHECK(LENGTH(Nazwisko) <= 50),
            GodzinaRozpoczecia INT,
            GodzinaZakonczenia INT,
            Tryb TEXT CHECK(LENGTH(Tryb) <= 20),
            PRIMARY KEY (Data, Imie, Nazwisko)
        )
    ''')

    # Zatwierdź zmiany i zamknij połączenie
    conn.commit()
    conn.close()


def create_pracownicy_table():
    # Połącz z bazą danych (jeśli nie istnieje, zostanie utworzona)
    conn = sqlite3.connect(DATA_BASE_FILE_DIR)

    # Utwórz kursor do wykonywania poleceń SQL
    cursor = conn.cursor()

    cursor.execute('DROP TABLE Pracownicy')

    # Utwórz tabelę pracowników z ograniczeniami na długość tekstu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Pracownicy (
            Imie TEXT CHECK(LENGTH(Imie) <= 50),
            Nazwisko TEXT CHECK(LENGTH(Nazwisko) <= 50),
            Stanowisko TEXT CHECK(LENGTH(Stanowisko) <= 50),
            LimitUrlopu INT,
            DniuUrlopu INT,
            PRIMARY KEY (Imie, Nazwisko)
        )
    ''')

    # Zatwierdź zmiany i zamknij połączenie
    conn.commit()
    conn.close()


create_pracownicy_table()
