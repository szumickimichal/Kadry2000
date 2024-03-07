import os

DATA_FOLDER = "data"
DATA_BASE_FILE_DIR = os.path.join(DATA_FOLDER, "kadry.db")
OBECNOSC_TABLE_NAME = "Obecnosc"
PRACOWNICY_TABLE_NAME = "Pracownicy"
APPLICATION_DOCUMENT_DIR = os.path.join(DATA_FOLDER, "Wniosek o urlop.docx")

HOURS_LIST: list = ['07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00',
                    '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00']

ACTIVITY_LIST: list = ['', 'Obecny', 'Urlop bezpłatny', 'Urlop wyp/godz', 'Opieka = Art. 188',
                       'Urlop na żądanie', 'Nieod. uspr. płatna', 'Urlop dodatkowy', "Urlop opiekuńczy", 'Nieob. siła wyższa']