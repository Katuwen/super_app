# Точка входа в приложение

import sys
import os
import customtkinter as ctk
from app.ui.views import MainWindow


# Добавляем корень проекта в путь, чтобы работали относительные импорты
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def main():
    # Настройка темы приложения
    ctk.set_appearance_mode("dark")  # Темная тема
    ctk.set_default_color_theme("blue")  # Синяя цветовая схема
    # Создание экземпляра главного окна
    app = MainWindow()
    # Запуск цикла событий
    app.mainloop()


if __name__ == "__main__":
    main()
