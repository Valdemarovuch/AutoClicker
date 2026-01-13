"""
Pro AutoClicker - Точка входу
"""
import customtkinter as ctk
import pyautogui
from src.ui import AutoClickerApp

# Налаштування зовнішнього вигляду
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Захист від вильоту при наведенні в кут екрана
pyautogui.FAILSAFE = False


def main():
    """Главна функція"""
    app = AutoClickerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
