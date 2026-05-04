import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"

class BookCatalog:
    def __init__(self, root):
        self.root = root
        self.root.title("Книжный каталог")
        self.root.geometry("750x500")
        self.books = self.load_books()
        self.create_widgets()
        self.refresh_list()

    def load_books(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_books(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)

    def create_widgets(self):
        # Панель ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить / Редактировать книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.genre_combo = ttk.Combobox(input_frame, values=["Роман", "Детектив", "Фантастика", "Наука", "Поэзия", "Другое"], width=27)
        self.genre_combo.grid(row=2, column=1, padx=5, pady=2)
        self.genre_combo.set("Роман")

        ttk.Label(input_frame, text="Оценка (1-5):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.rating_spin = ttk.Spinbox(input_frame, from_=1, to=5, width=27)
        self.rating_spin.grid(row=3, column=1, padx=5, pady=2)
        self.rating_spin.set(5)

        ttk.Label(input_frame, text="Статус:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.status_combo = ttk.Combobox(input_frame, values=["Прочитана", "Читаю", "Брошена", "В планах"], width=27)
        self.status_combo.grid(row=4, column=1, padx=5, pady=2)
        self.status_combo.set("В планах")

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_book).pack(side="left", padx=5)

        # Фильтр
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(filter_frame, text="Фильтр по статусу:").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="Все")
        filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   values=["Все", "Прочитана", "Читаю", "Брошена", "В планах"], width=15)
        filter_menu.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Применить", command=self.refresh_list).pack(side="left", padx=10)

        # Таблица книг
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(list_frame, columns=("Название", "Автор", "Жанр", "Оценка", "Статус"), show="headings")
        for col in ("Название", "Автор", "Жанр", "Оценка", "Статус"):
            self.tree.heading(col, text=col)
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=100)
        self.tree.column("Оценка", width=60)
        self.tree.column("Статус", width=100)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        if not title or not author:
            messagebox.showerror("Ошибка", "Заполните название и автора")
            return
        try:
            rating = int(self.rating_spin.get())
            if rating < 1 or rating > 5:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Оценка должна быть от 1 до 5")
            return
        for book in self.books:
            if book["title"].lower() == title.lower() and book["author"].lower() == author.lower():
                messagebox.showerror("Ошибка", "Такая книга уже есть")
                return
        new_book = {"title": title, "author": author, "genre": self.genre_combo.get(),
                    "rating": rating, "status": self.status_combo.get()}
        self.books.append(new_book)
        self.save_books()
        self.refresh_list()
        self.clear_entries()
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена")

    def update_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите книгу для обновления")
            return
        item = self.tree.item(selected[0])
        old_title, old_author = item["values"][0], item["values"][1]
        new_title = self.title_entry.get().strip()
        new_author = self.author_entry.get().strip()
        if not new_title or not new_author:
            messagebox.showerror("Ошибка", "Название и автор не могут быть пустыми")
            return
        try:
            rating = int(self.rating_spin.get())
            if rating < 1 or rating > 5:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Оценка от 1 до 5")
            return
        for i, book in enumerate(self.books):
            if book["title"] == old_title and book["author"] == old_author:
                self.books[i] = {"title": new_title, "author": new_author,
                                 "genre": self.genre_combo.get(), "rating": rating,
                                 "status": self.status_combo.get()}
                break
        self.save_books()
        self.refresh_list()
        self.clear_entries()
        messagebox.showinfo("Успех", "Книга обновлена")

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите книгу для удаления")
            return
        item = self.tree.item(selected[0])
        title, author = item["values"][0], item["values"][1]
        if messagebox.askyesno("Подтверждение", f"Удалить '{title}' {author}?"):
            self.books = [b for b in self.books if not (b["title"] == title and b["author"] == author)]
            self.save_books()
            self.refresh_list()
            self.clear_entries()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        filter_status = self.filter_var.get()
        for book in self.books:
            if filter_status == "Все" or book["status"] == filter_status:
                self.tree.insert("", "end", values=(book["title"], book["author"],
                                                    book["genre"], book["rating"], book["status"]))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.clear_entries()
            self.title_entry.insert(0, values[0])
            self.author_entry.insert(0, values[1])
            self.genre_combo.set(values[2])
            self.rating_spin.set(values[3])
            self.status_combo.set(values[4])

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("Роман")
        self.rating_spin.set(5)
        self.status_combo.set("В планах")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookCatalog(root)
    root.mainloop()