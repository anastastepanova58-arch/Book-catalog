import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ---------- Конфигурация ----------
DATA_FILE = "movies.json"

# ---------- Работа с данными ----------
def load_movies():
    """Загружает список фильмов из JSON-файла."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_movies(movies):
    """Сохраняет список фильмов в JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

def add_movie_to_storage(title, genre, year, rating):
    """Добавляет фильм в хранилище и возвращает обновлённый список."""
    movies = load_movies()
    movies.append({
        "title": title,
        "genre": genre,
        "year": year,
        "rating": rating,
        "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_movies(movies)
    return movies

def update_table(movies, tree):
    """Обновляет таблицу переданным списком фильмов."""
    for row in tree.get_children():
        tree.delete(row)
    for m in movies:
        tree.insert("", tk.END, values=(
            m["title"],
            m["genre"],
            m["year"],
            f"{m['rating']:.1f}" if isinstance(m['rating'], (int, float)) else m['rating']
        ))

# ---------- Фильтрация ----------
def filter_movies(genre_filter, year_filter):
    """Возвращает отфильтрованный список фильмов."""
    movies = load_movies()
    filtered = movies[:]

    if genre_filter and genre_filter != "Все жанры":
        filtered = [m for m in filtered if m["genre"].lower() == genre_filter.lower()]
    if year_filter:
        try:
            year_int = int(year_filter)
            filtered = [m for m in filtered if m["year"] == year_int]
        except ValueError:
            pass  # если год не число, игнорируем фильтр
    return filtered

# ---------- GUI и обработчики ----------
def refresh_table(tree, combobox_genre, entry_year):
    genre = combobox_genre.get()
    year = entry_year.get()
    filtered = filter_movies(genre, year)
    update_table(filtered, tree)

def on_add(tree, entry_title, entry_genre, entry_year, entry_rating, combobox_genre, entry_year_filter):
    # Получаем данные
    title = entry_title.get().strip()
    genre = entry_genre.get().strip()
    year_str = entry_year.get().strip()
    rating_str = entry_rating.get().strip()

    # Проверки
    if not title:
        messagebox.showwarning("Ошибка", "Название фильма не может быть пустым.")
        return
    if not genre:
        messagebox.showwarning("Ошибка", "Укажите жанр.")
        return
    try:
        year = int(year_str)
        if year < 1888 or year > datetime.now().year + 5:
            messagebox.showwarning("Ошибка", f"Год должен быть от 1888 до {datetime.now().year + 5}.")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Год должен быть целым числом.")
        return

    try:
        rating = float(rating_str)
        if rating < 0 or rating > 10:
            messagebox.showwarning("Ошибка", "Рейтинг должен быть от 0 до 10.")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Рейтинг должен быть числом (например, 8.5).")
        return

    # Добавляем
    add_movie_to_storage(title, genre, year, rating)
    # Очищаем поля
    entry_title.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_year.delete(0, tk.END)
    entry_rating.delete(0, tk.END)
    # Обновляем таблицу и фильтры
    refresh_table(tree, combobox_genre, entry_year_filter)
    # Обновляем выпадающий список жанров (добавляем новый, если его нет)
    update_genre_combobox(combobox_genre)

def update_genre_combobox(combobox):
    movies = load_movies()
    genres = sorted(set(m["genre"] for m in movies))
    combobox['values'] = ["Все жанры"] + genres
    if combobox.get() not in combobox['values']:
        combobox.set("Все жанры")

# ---------- Создание основного окна ----------
root = tk.Tk()
root.title("Movie Library – Личная кинотека")
root.geometry("800x500")
root.resizable(False, True)

# Панель добавления фильма
frame_add = ttk.LabelFrame(root, text="Добавить фильм", padding=10)
frame_add.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_add, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_title = ttk.Entry(frame_add, width=30)
entry_title.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_add, text="Жанр:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
entry_genre = ttk.Entry(frame_add, width=15)
entry_genre.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_add, text="Год выпуска:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_year = ttk.Entry(frame_add, width=10)
entry_year.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_add, text="Рейтинг (0–10):").grid(row=1, column=2, sticky="e", padx=5, pady=5)
entry_rating = ttk.Entry(frame_add, width=10)
entry_rating.grid(row=1, column=3, padx=5, pady=5)

btn_add = ttk.Button(frame_add, text="Добавить фильм", command=lambda: on_add(
    tree, entry_title, entry_genre, entry_year, entry_rating, combo_genre_filter, entry_year_filter))
btn_add.grid(row=2, column=0, columnspan=4, pady=10)

# Панель фильтрации
frame_filter = ttk.LabelFrame(root, text="Фильтрация", padding=10)
frame_filter.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_filter, text="Жанр:").grid(row=0, column=0, padx=5, pady=5)
combo_genre_filter = ttk.Combobox(frame_filter, width=15)
combo_genre_filter.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_filter, text="Год выпуска:").grid(row=0, column=2, padx=5, pady=5)
entry_year_filter = ttk.Entry(frame_filter, width=10)
entry_year_filter.grid(row=0, column=3, padx=5, pady=5)

btn_filter = ttk.Button(frame_filter, text="Применить фильтр", command=lambda: refresh_table(
    tree, combo_genre_filter, entry_year_filter))
btn_filter.grid(row=0, column=4, padx=10, pady=5)

btn_reset = ttk.Button(frame_filter, text="Сбросить фильтры", command=lambda: reset_filters(
    combo_genre_filter, entry_year_filter, tree))
btn_reset.grid(row=0, column=5, padx=5, pady=5)

# Таблица фильмов
frame_table = ttk.LabelFrame(root, text="Список фильмов", padding=10)
frame_table.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("Название", "Жанр", "Год", "Рейтинг")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=12)
tree.heading("Название", text="Название")
tree.heading("Жанр", text="Жанр")
tree.heading("Год", text="Год")
tree.heading("Рейтинг", text="Рейтинг")
tree.column("Название", width=250)
tree.column("Жанр", width=120)
tree.column("Год", width=80)
tree.column("Рейтинг", width=80)
tree.pack(fill="both", expand=True)

# Кнопка обновления таблицы (показ всех)
btn_show_all = ttk.Button(frame_table, text="Показать все фильмы", command=lambda: refresh_table(
    tree, combo_genre_filter, entry_year_filter))
btn_show_all.pack(pady=5)

# ---------- Дополнительные функции ----------
def reset_filters(combobox, entry_year, tree):
    combobox.set("Все жанры")
    entry_year.delete(0, tk.END)
    refresh_table(tree, combobox, entry_year)

# Инициализация
def init_app():
    # Загружаем существующие фильмы
    update_genre_combobox(combo_genre_filter)
    combo_genre_filter.set("Все жанры")
    refresh_table(tree, combo_genre_filter, entry_year_filter)

init_app()

root.mainloop()
