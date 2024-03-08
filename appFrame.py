import tkinter as tk
from tkinter import ttk, messagebox
import sqlWorkspace
from constants import *
import docx
from docx2pdf import convert
import tkcalendar
import pandas as pd
from agendaCls import Agenda
from datetime import datetime

from tkcalendar import Calendar


class MainApplication(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)

        self.root = root
        self.selected_user = {}  # Selected user values

        self.open_menu()

    def open_menu(self):
        self.clear_frame(self)

        self.selected_user = {}

        self.add_users_table()
        self.add_right_bar()

    def add_right_bar(self):
        self.bar_frame = tk.Frame(self)
        buttons_width = 100
        tk.Button(self.bar_frame, text="Dodaj nowego pracownika", command=lambda: self.add_new_employee()).pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Edytuj pracownika", state='disabled', command=lambda: self.edit_employee()).pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Usuń pracownika", state='disabled', command=lambda: self.delete_employee()).pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Dodaj aktywność", state='disabled', command=lambda: self.add_employee_activity()).pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Podgląd aktywności", state='disabled', command=lambda: self.activity_preview()).pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Generuj raport", state='disabled').pack(fill='both', ipadx=buttons_width, ipady=10)
        tk.Button(self.bar_frame, text="Generuj wniosek", state='disabled', command=lambda: self.generate_application()).pack(fill='both', ipadx=buttons_width, ipady=10)
        self.bar_frame.pack(side="left", fill="x", expand=False)

    def activity_preview(self):
        preview_root = tk.Toplevel()
        preview_root.title("Podgląd")

        preview_root.geometry("800x600")

        preview = Agenda(preview_root)

        df_activity = sqlWorkspace.read_table(OBECNOSC_TABLE_NAME, where=f""" Nazwisko = "{self.selected_user.get('Nazwisko')}" AND Imie = "{self.selected_user.get('Imie')}" """)
        preview.tag_config('Obecny', background='green', foreground='yellow')
        preview.tag_config('Urlop wyp/godz', background='red', foreground='yellow')

        for index, row in df_activity.iterrows():
            label_text = row["Tryb"] + '\n' +  row["GodzinaRozpoczecia"] + '\n' + row["GodzinaZakonczenia"] if row["Tryb"] == "Obecny" else row["Tryb"]
            preview.calevent_create(datetime.strptime(row['Data'], "%Y-%m-%d"), label_text, row['Tryb'])

        # to nie powinna być funkcja wewnętrzna. Wywołanie powinno nastąpić po zadeklarowaniu calevent'ów, a nie przy inicjalizacji.
        # Zostawiam prefix, bo jest to funkcja nadpisana z klasy Calendar
        preview._display_days_with_othermonthdays()

        preview.pack(fill="both", expand=True)

    def generate_document(self, info_dict):
        doc = docx.Document(APPLICATION_DOCUMENT_DIR)

        for paragraph in doc.paragraphs:
            paragraph.text = paragraph.text.replace("TODAY", info_dict["TODAY"])
            paragraph.text = paragraph.text.replace("IMIE", info_dict["IMIE"])
            paragraph.text = paragraph.text.replace("NAZWISKO", info_dict["NAZWISKO"])
            paragraph.text = paragraph.text.replace("START", info_dict["START"])
            paragraph.text = paragraph.text.replace("END", info_dict["END"])
            paragraph.text = paragraph.text.replace("FREE DAYS", info_dict["FREE DAYS"])

        doc.save(f'Wniosek {info_dict["IMIE"]} {info_dict["NAZWISKO"]}.docx')
        convert(f'Wniosek {info_dict["IMIE"]} {info_dict["NAZWISKO"]}.docx')
        messagebox.showinfo("Wniosek", "Wniosek został wygenerowany!")

    def generate_application(self):
        self.clear_frame(self)

        info_dict = {}
        info_dict["IMIE"] = self.selected_user.get("Imie")
        info_dict["NAZWISKO"] = self.selected_user.get("Nazwisko")

        generate_application_frame = tk.Frame(self)
        generate_application_frame.pack()

        def _add_document_date():
            label = tk.Label(generate_application_frame, text="Data wydania dokumentu", width=32, relief="groove")
            label.grid(row=0, column=0, sticky=tk.NSEW)

            info_dict["TODAY"] = tkcalendar.DateEntry(generate_application_frame, date_pattern="yyyy-mm-dd")
            info_dict["TODAY"].grid(row=0, column=1, sticky=tk.NSEW)

        def _add_start_date():
            label = tk.Label(generate_application_frame, text="Data rozpoczęcia urlopu", width=32, relief="groove")
            label.grid(row=1, column=0, sticky=tk.NSEW)
            info_dict["START"] = tkcalendar.DateEntry(generate_application_frame, date_pattern="yyyy-mm-dd")
            info_dict["START"].grid(row=1, column=1, sticky=tk.NSEW)

        def _add_end_date():
            label = tk.Label(generate_application_frame, text="Data zakończenia urlopu", width=32, relief="groove")
            label.grid(row=2, column=0, sticky=tk.NSEW)
            info_dict["END"] = tkcalendar.DateEntry(generate_application_frame, date_pattern="yyyy-mm-dd")
            info_dict["END"].grid(row=2, column=1, sticky=tk.NSEW)

        def _add_buttons():
            menu_button = tk.Button(generate_application_frame, text="Cofnij", width=32, relief="groove", command=lambda: self.open_menu())
            menu_button.grid(row=3, column=0, sticky=tk.NSEW)
            add_worker_button = tk.Button(generate_application_frame, text="Generuj wniosek", width=32, relief="groove", command=lambda: _convert_dict_and_generate_document())
            add_worker_button.grid(row=3, column=1, sticky=tk.NSEW)

        def _convert_dict_and_generate_document():
            for key, value in info_dict.items():
                if isinstance(value, tk.Entry):
                    info_dict[key] = value.get()

            date_range = pd.date_range(start=info_dict["START"], end=info_dict["END"])
            info_dict["FREE DAYS"] = str(len(date_range[date_range.weekday < 5]))

            self.generate_document(info_dict)

        _add_document_date()
        _add_start_date()
        _add_end_date()
        _add_buttons()

    def delete_employee(self):
        confirmation = messagebox.askyesno("Confirmation", "Czy na pewno chcesz usunąć tego pracownika?")

        if confirmation:
            sqlWorkspace.delete_user(self.selected_user)
            self.open_menu()

    def add_employee_activity(self):
        self.clear_frame(self)

        info_dict = {}
        info_dict["Imie"] = self.selected_user.get("Imie")
        info_dict["Nazwisko"] = self.selected_user.get("Nazwisko")

        employee_presence_frame = tk.Frame(self)
        employee_presence_frame.pack()

        def _add_hours():
            label = tk.Label(employee_presence_frame, text="Godzina rozpoczęcia pracy", width=32, relief="groove")
            label.grid(row=0, column=0, sticky=tk.NSEW)
            info_dict["GodzinaRozpoczecia"] = ttk.Combobox(employee_presence_frame, values=HOURS_LIST)
            info_dict["GodzinaRozpoczecia"].insert(0, "8:00")
            info_dict["GodzinaRozpoczecia"].grid(row=0, column=1, sticky=tk.NSEW)

            label = tk.Label(employee_presence_frame, text="Godzina zakończenia pracy", width=32, relief="groove")
            label.grid(row=1, column=0, sticky=tk.NSEW)
            info_dict["GodzinaZakonczenia"] = ttk.Combobox(employee_presence_frame, values=HOURS_LIST)
            info_dict["GodzinaZakonczenia"].insert(0, "16:00")
            info_dict["GodzinaZakonczenia"].grid(row=1, column=1, sticky=tk.NSEW)

        def _add_start_date():
            label = tk.Label(employee_presence_frame, text="Data początkowa", width=32, relief="groove")
            label.grid(row=2, column=0, sticky=tk.NSEW)
            info_dict["START"] = tkcalendar.DateEntry(employee_presence_frame, date_pattern="yyyy-mm-dd")
            info_dict["START"].grid(row=2, column=1, sticky=tk.NSEW)

        def _add_end_date():
            label = tk.Label(employee_presence_frame, text="Data końcowa", width=32, relief="groove")
            label.grid(row=3, column=0, sticky=tk.NSEW)
            info_dict["END"] = tkcalendar.DateEntry(employee_presence_frame, date_pattern="yyyy-mm-dd")
            info_dict["END"].grid(row=3, column=1, sticky=tk.NSEW)

        def _add_activity_type():
            label = tk.Label(employee_presence_frame, text="Rodzaj", width=32, relief="groove")
            label.grid(row=4, column=0, sticky=tk.NSEW)
            info_dict["Tryb"] = ttk.Combobox(employee_presence_frame, values=ACTIVITY_LIST)
            info_dict["Tryb"].insert(0, "Obecny")
            info_dict["Tryb"].grid(row=4, column=1, sticky=tk.NSEW)

        def _add_buttons():
            menu_button = tk.Button(employee_presence_frame, text="Cofnij", width=32, relief="groove", command=lambda: self.open_menu())
            menu_button.grid(row=5, column=0, sticky=tk.NSEW)
            add_worker_button = tk.Button(employee_presence_frame, text="Dodaj obecność", width=32, relief="groove", command=lambda: _convert_dict_and_write_to_table())
            add_worker_button.grid(row=5, column=1, sticky=tk.NSEW)

        def _convert_dict_and_write_to_table():
            for key, value in info_dict.items():
                if isinstance(value, ttk.Combobox) or isinstance(value, tkcalendar.DateEntry):
                    info_dict[key] = value.get()

            date_range = pd.date_range(start=info_dict["START"], end=info_dict["END"])
            info_dict["Data"] = date_range[date_range.weekday < 5]

            sqlWorkspace.add_rows_to_obecnosc_table(info_dict)

            df_activity = sqlWorkspace.read_table(OBECNOSC_TABLE_NAME, where=f""" Nazwisko = "{self.selected_user.get('Nazwisko')}" AND Imie = "{self.selected_user.get('Imie')}" """)
            self.selected_user['DniuUrlopu'] = self.selected_user['LimitUrlopu'] - len(df_activity[df_activity['Tryb'] == 'Urlop wyp/godz'])
            sqlWorkspace.add_or_edit_rows_to_pracownicy_table(pd.DataFrame(self.selected_user, index=[0]))

            self.open_menu()

        _add_hours()
        _add_start_date()
        _add_end_date()
        _add_activity_type()
        _add_buttons()

    def edit_employee(self):
        employee_info_list = self.selected_user

        self.clear_frame(self)
        new_worker_addition_frame = tk.Frame(self)
        new_worker_addition_frame.pack()

        info_dict = {}

        def _name_row():
            label = tk.Label(new_worker_addition_frame, text="Imię:", width=32, relief="groove")
            label.grid(row=0, column=0, sticky=tk.NSEW)
            info_dict["Imie"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Imie"].insert(0, employee_info_list.get("Imie"))
            info_dict["Imie"].config(state='disabled')
            info_dict["Imie"].grid(row=0, column=1, sticky=tk.NSEW)

        def _surname_row():
            label = tk.Label(new_worker_addition_frame, text="Nazwisko:", width=32, relief="groove")
            label.grid(row=2, column=0, sticky=tk.NSEW)
            info_dict["Nazwisko"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Nazwisko"].insert(0, employee_info_list.get("Nazwisko"))
            info_dict["Nazwisko"].config(state='disabled')
            info_dict["Nazwisko"].grid(row=2, column=1, sticky=tk.NSEW)

        def _job_row():
            label = tk.Label(new_worker_addition_frame, text="Stanowisko:", width=32, relief="groove")
            label.grid(row=3, column=0, sticky=tk.NSEW)
            info_dict["Stanowisko"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Stanowisko"].insert(0, employee_info_list.get("Stanowisko"))
            info_dict["Stanowisko"].grid(row=3, column=1, sticky=tk.NSEW)

        def _limit_row():
            label = tk.Label(new_worker_addition_frame, text="Limit dni urlopowych:", width=32, relief="groove")
            label.grid(row=4, column=0, sticky=tk.NSEW)
            info_dict["LimitUrlopu"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["LimitUrlopu"].insert(0, employee_info_list.get("LimitUrlopu"))
            info_dict["LimitUrlopu"].grid(row=4, column=1, sticky=tk.NSEW)

        def _add_buttons():
            menu_button = tk.Button(new_worker_addition_frame, text="Cofnij", width=32, relief="groove", command=lambda: self.open_menu())
            menu_button.grid(row=5, column=0, sticky=tk.NSEW)

            add_worker_button = tk.Button(new_worker_addition_frame, text="Edytuj pracownika", width=32, relief="groove", command=lambda: _add_new_user())
            add_worker_button.grid(row=5, column=1, sticky=tk.NSEW)

        def _add_new_user():
            for key, value in info_dict.items():
                if isinstance(value, tk.Entry):
                    info_dict[key] = value.get()
            info_dict["DniuUrlopu"] = employee_info_list.get("DniuUrlopu")

            sqlWorkspace.add_or_edit_rows_to_pracownicy_table(pd.DataFrame(info_dict, index=[0]))
            self.open_menu()

        _name_row()
        _surname_row()
        _job_row()
        _limit_row()
        _add_buttons()

    def add_new_employee(self):
        self.clear_frame(self)
        new_worker_addition_frame = tk.Frame(self)
        new_worker_addition_frame.pack()

        info_dict = {}

        def _name_row():
            label = tk.Label(new_worker_addition_frame, text="Imię:", width=32, relief="groove")
            label.grid(row=0, column=0, sticky=tk.NSEW)
            info_dict["Imie"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Imie"].grid(row=0, column=1, sticky=tk.NSEW)

        def _surname_row():
            label = tk.Label(new_worker_addition_frame, text="Nazwisko:", width=32, relief="groove")
            label.grid(row=2, column=0, sticky=tk.NSEW)
            info_dict["Nazwisko"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Nazwisko"].grid(row=2, column=1, sticky=tk.NSEW)

        def _job_row():
            label = tk.Label(new_worker_addition_frame, text="Stanowisko:", width=32, relief="groove")
            label.grid(row=3, column=0, sticky=tk.NSEW)
            info_dict["Stanowisko"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["Stanowisko"].grid(row=3, column=1, sticky=tk.NSEW)

        def _limit_row():
            label = tk.Label(new_worker_addition_frame, text="Limit dni urlopowych:", width=32, relief="groove")
            label.grid(row=4, column=0, sticky=tk.NSEW)
            info_dict["LimitUrlopu"] = tk.Entry(new_worker_addition_frame, width=10)
            info_dict["LimitUrlopu"].grid(row=4, column=1, sticky=tk.NSEW)

        def _add_buttons():
            menu_button = tk.Button(new_worker_addition_frame, text="Cofnij", width=32, relief="groove", command=lambda: self.open_menu())
            menu_button.grid(row=5, column=0, sticky=tk.NSEW)

            add_worker_button = tk.Button(new_worker_addition_frame, text="Dodaj nowego pracownika", width=32, relief="groove", command=lambda: _add_new_user())
            add_worker_button.grid(row=5, column=1, sticky=tk.NSEW)

        def _add_new_user():
            for key, value in info_dict.items():
                if isinstance(value, tk.Entry):
                    info_dict[key] = value.get()
            info_dict["DniuUrlopu"] = info_dict["LimitUrlopu"]

            sqlWorkspace.add_rows(info_dict, PRACOWNICY_TABLE_NAME)
            self.open_menu()

        _name_row()
        _surname_row()
        _job_row()
        _limit_row()
        _add_buttons()

    def clear_frame(self, master):
        for widget in master.winfo_children():
            widget.destroy()

    def add_users_table(self):
        # Tworzenie ramki dla Treeview
        users_table_frame = tk.Frame(self)
        users_table_frame.pack(side="left", fill="x", expand=False)

        # generowanie df z wszystkimi pracowanikami
        df = sqlWorkspace.read_table(PRACOWNICY_TABLE_NAME)

        # Utworzenie Treeview
        tree = ttk.Treeview(users_table_frame, columns=list(df.columns), show='headings', height=10)
        tree.pack(side='left', fill='both')

        # Dodanie nagłówków do Treeview
        for col in df.columns:
            tree.heading(col, text=col)

        # Dodanie danych z DataFrame do Treeview
        for index, row in df.iterrows():
            tree.insert('', tk.END, values=tuple(row))

        # Utworzenie paska przewijania dla Treeview (pionowy)
        vsb = ttk.Scrollbar(users_table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='left', fill='y')

        def _on_select(event):
            if tree.selection():

                columns = tree["columns"]

                values = tree.item(tree.selection())['values']
                self.selected_user = {column: value for column, value in zip(columns, values)}

                for child in self.bar_frame.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(state='active')

        # Ustawienie funkcji do obsługi zdarzenia wyboru
        tree.bind('<ButtonRelease-1>', _on_select)


# class MainApplication(tk.Frame):
#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent)
#
#
#         self.parent = parent
#         self.menu = Menu()
#
#         self.menu.pack(fill='both', expand=True)


if __name__ == "__main__":
    # ustawienia okna
    root = tk.Tk()
    root.title("Kadry2000")
    initial_x = 400
    initial_y = 100
    root.geometry(f"1200x400+{initial_x}+{initial_y}")

    # Główna aplikacja
    MainApplication(root).pack(fill='both', expand=True)

    root.mainloop()