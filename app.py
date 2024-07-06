import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MedicationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Medication Information System")
        self.master.geometry("800x600")
        self.master.configure(bg='#f0f0f0')

        self.csv_path = resource_path('medications.csv')
        self.df = pd.read_csv(self.csv_path)

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Search")
        self.create_search_tab()

        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Add Medication")
        self.create_add_tab()

        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View All")
        self.create_view_tab()

        self.modify_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.modify_frame, text="Modify")
        self.create_modify_tab()

    def create_search_tab(self):
        search_frame = ttk.Frame(self.search_frame, padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Enter Medication Name:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_medication).pack(side=tk.LEFT)

        self.result_frame = ttk.Frame(self.search_frame, padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, width=70, height=15)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

    def create_add_tab(self):
        fields = ['Name', 'Category', 'Dosage Form', 'Strength', 'Manufacturer', 'Indication', 'Classification']
        self.add_entries = {}

        for field in fields:
            frame = ttk.Frame(self.add_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=50)
            entry.pack(side=tk.LEFT, padx=5)
            self.add_entries[field] = entry

        ttk.Button(self.add_frame, text="Add Medication", command=self.add_medication).pack(pady=10)

    def create_view_tab(self):
        self.tree = ttk.Treeview(self.view_frame, columns=list(self.df.columns), show='headings')
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.update_treeview()

        ttk.Button(self.view_frame, text="Refresh", command=self.update_treeview).pack(pady=5)

    def create_modify_tab(self):
        search_frame = ttk.Frame(self.modify_frame, padding="10")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Enter Medication Name to Modify:").pack(side=tk.LEFT)
        self.modify_search_entry = ttk.Entry(search_frame, width=30)
        self.modify_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_to_modify).pack(side=tk.LEFT)

        self.modify_result_frame = ttk.Frame(self.modify_frame, padding="10")
        self.modify_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def search_medication(self):
        medication_name = self.search_entry.get().strip()
        if not medication_name:
            self.show_result("Please enter a medication name.")
            return

        results = self.df[self.df['Name'].str.lower() == medication_name.lower()]
        
        if results.empty:
            self.show_result(f"No medication found with the name '{medication_name}'.")
        else:
            self.show_medication_choices(results, self.display_medication_info)

    def show_medication_choices(self, results, callback):
        choice_window = tk.Toplevel(self.master)
        choice_window.title("Choose Medication")
        choice_window.geometry("600x400")

        ttk.Label(choice_window, text="Multiple medications found. Please choose one:").pack(pady=10)

        tree = ttk.Treeview(choice_window, columns=list(results.columns), show='headings')
        for col in results.columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for _, row in results.iterrows():
            tree.insert('', 'end', values=list(row))

        def on_select(event):
            selected_item = tree.selection()[0]
            selected_medication = tree.item(selected_item)['values']
            choice_window.destroy()
            callback(pd.Series(dict(zip(results.columns, selected_medication))))

        tree.bind('<<TreeviewSelect>>', on_select)

    def display_medication_info(self, medication):
        self.result_text.delete(1.0, tk.END)
        
        fields = ['Name', 'Category', 'Dosage Form', 'Strength', 'Manufacturer', 'Indication', 'Classification']
        
        self.result_text.insert(tk.END, f"Information for {medication['Name']}:\n\n", "bold")
        
        for field in fields:
            self.result_text.insert(tk.END, f"{field}: ", "bold")
            self.result_text.insert(tk.END, f"{medication[field]}\n\n")

    def show_result(self, message):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)

    def add_medication(self):
        new_medication = {field: entry.get().strip() for field, entry in self.add_entries.items()}
        if not new_medication['Name']:
            messagebox.showerror("Error", "Medication name is required.")
            return
        
        self.df = self.df.append(new_medication, ignore_index=True)
        self.df.to_csv(self.csv_path, index=False)
        self.update_treeview()
        
        for entry in self.add_entries.values():
            entry.delete(0, tk.END)
        
        messagebox.showinfo("Success", f"Added {new_medication['Name']} to the database.")

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for _, row in self.df.iterrows():
            self.tree.insert('', 'end', values=list(row))

    def search_to_modify(self):
        medication_name = self.modify_search_entry.get().strip()
        if not medication_name:
            messagebox.showerror("Error", "Please enter a medication name.")
            return

        results = self.df[self.df['Name'].str.lower() == medication_name.lower()]
        
        if results.empty:
            messagebox.showerror("Error", f"No medication found with the name '{medication_name}'.")
        else:
            self.show_medication_choices(results, self.display_modify_form)

    def display_modify_form(self, medication):
        for widget in self.modify_result_frame.winfo_children():
            widget.destroy()

        self.modify_entries = {}
        for field in self.df.columns:
            frame = ttk.Frame(self.modify_result_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame, width=50)
            entry.insert(0, str(medication[field]))
            entry.pack(side=tk.LEFT, padx=5)
            self.modify_entries[field] = entry

        ttk.Button(self.modify_result_frame, text="Save Changes", 
                   command=lambda: self.save_changes(medication.name)).pack(pady=10)

    def save_changes(self, index):
        updated_medication = {field: entry.get().strip() for field, entry in self.modify_entries.items()}
        self.df.loc[self.df['Name'] == updated_medication['Name']] = updated_medication
        self.df.to_csv(self.csv_path, index=False)
        self.update_treeview()
        messagebox.showinfo("Success", f"Updated {updated_medication['Name']} in the database.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicationApp(root)
    root.mainloop()