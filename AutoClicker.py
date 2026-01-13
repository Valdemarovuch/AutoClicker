import customtkinter as ctk
import pyautogui
import threading
import time
import random
from pynput import keyboard
from typing import Literal

# --- Налаштування зовнішнього вигляду ---
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Захист від вильоту при наведенні в кут екрана
pyautogui.FAILSAFE = False


class ClickerEngine(threading.Thread):
    """
    Клас, що відповідає виключно за логіку клікання у фоновому потоці.
    Він не знає нічого про GUI.
    """
    def __init__(self):
        super().__init__()
        self.daemon = True  # Потік завершиться, коли закриється головна програма
        self._clicking = False # Чи активний зараз процес клікання
        self._running = True   # Чи працює потік взагалі

        # Дефолтні налаштування
        self.settings = {
            "target_cps": 10.0,      # Цільова швидкість (кліків/сек)
            "randomness_pct": 20.0,  # Відсоток рандомності (0-100%)
            "button": 'left'         # Кнопка миші
        }

    def update_settings(self, key, value):
        """Безпечне оновлення налаштувань з GUI потоку"""
        self.settings[key] = value

    def start_clicking(self):
        self._clicking = True
        print("[Engine] Старт клікання")

    def stop_clicking(self):
        self._clicking = False
        print("[Engine] Стоп клікання")

    def toggle(self):
        if self._clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
        return self._clicking

    def stop_engine(self):
        """Повна зупинка потоку перед виходом"""
        self.stop_clicking()
        self._running = False

    def _calculate_delay(self):
        """Розраховує затримку між кліками на основі CPS та рандому"""
        cps = self.settings["target_cps"]
        if cps <= 0: cps = 0.1 # Захист від ділення на нуль
        
        base_delay = 1.0 / cps
        
        random_pct = self.settings["randomness_pct"] / 100.0
        if random_pct > 0:
            # Обчислюємо відхилення. Наприклад, якщо затримка 0.1с і рандом 20%,
            # то відхилення +/- 0.02с.
            variation = base_delay * random_pct
            min_delay = base_delay - variation
            max_delay = base_delay + variation
            # Гарантуємо, що затримка не від'ємна
            return max(0.001, random.uniform(min_delay, max_delay))
        else:
            return base_delay

    def run(self):
        """Головний цикл потоку"""
        print("[Engine] Потік запущено")
        while self._running:
            if self._clicking:
                pyautogui.click(button=self.settings["button"])
                delay = self._calculate_delay()
                time.sleep(delay)
            else:
                # Ефективне очікування, коли не клікаємо (не вантажить CPU)
                time.sleep(0.05)


class AutoClickerApp(ctk.CTk):
    """
    Головне вікно програми. Відповідає за відображення та взаємодію з користувачем.
    """
    def __init__(self):
        super().__init__()

        # --- Ініціалізація двигуна ---
        self.engine = ClickerEngine()
        self.engine.start() # Запускаємо фоновий потік

        # --- Налаштування гарячої клавіші ---
        self.hotkey_char = 's'
        self.listener = keyboard.Listener(on_press=self.on_hotkey_press)
        self.listener.start()

        # --- Налаштування вікна GUI ---
        self.title("Pro AutoClicker by AI")
        self.geometry("400x450")
        self.resizable(False, False)

        # --- Змінні для віджетів ---
        self.cps_var = ctk.DoubleVar(value=10.0)
        self.random_var = ctk.DoubleVar(value=20.0)
        self.button_var = ctk.StringVar(value="left")
        self.status_var = ctk.StringVar(value="Статус: НЕАКТИВНО")

        self._setup_ui()
        # Оновлюємо двигун початковими значеннями з GUI
        self.update_engine_settings()

    def _setup_ui(self):
        """Створення та розміщення елементів інтерфейсу"""
        # Заголовок
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_frame, text="Налаштування Клікера", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))

        # --- Секція CPS (Швидкість) ---
        cps_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cps_frame.pack(fill="x", pady=(0, 15))
        
        cps_label_title = ctk.CTkLabel(cps_frame, text="Швидкість (CPS):", anchor="w")
        cps_label_title.pack(side="left", padx=(10, 0))
        
        self.cps_value_label = ctk.CTkLabel(cps_frame, text=f"{self.cps_var.get():.1f}", width=40)
        self.cps_value_label.pack(side="right", padx=(0, 10))

        cps_slider = ctk.CTkSlider(main_frame, from_=1, to=50, variable=self.cps_var, command=self.on_cps_change)
        cps_slider.pack(fill="x", padx=10, pady=(0, 10))

        # --- Секція Рандомності (Олюднення) ---
        rand_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        rand_frame.pack(fill="x", pady=(0, 15))

        rand_label_title = ctk.CTkLabel(rand_frame, text="Олюднення (Рандом %):", anchor="w")
        rand_label_title.pack(side="left", padx=(10, 0))

        self.rand_value_label = ctk.CTkLabel(rand_frame, text=f"{self.random_var.get():.0f}%", width=40)
        self.rand_value_label.pack(side="right", padx=(0, 10))

        rand_slider = ctk.CTkSlider(main_frame, from_=0, to=100, variable=self.random_var, command=self.on_random_change)
        rand_slider.pack(fill="x", padx=10, pady=(0, 10))

        # --- Секція Вибору кнопки ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 20), padx=10)
        
        btn_label = ctk.CTkLabel(btn_frame, text="Кнопка миші:")
        btn_label.pack(side="left")

        btn_option = ctk.CTkOptionMenu(btn_frame, values=["left", "right", "middle"], variable=self.button_var, command=self.on_button_change)
        btn_option.pack(side="right")

        # --- Головна кнопка Старт/Стоп ---
        self.toggle_btn = ctk.CTkButton(main_frame, text="СТАРТ (HotKey: S)", height=50, font=ctk.CTkFont(size=16, weight="bold"), command=self.toggle_clicking_gui)
        self.toggle_btn.pack(fill="x", padx=20, pady=(10, 5))
        
        # Статус бар
        self.status_label = ctk.CTkLabel(main_frame, textvariable=self.status_var, font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(5, 10))

        # Інфо
        info_label = ctk.CTkLabel(self, text="Натисни 'S' для старту/стопу\nЗакрий вікно для виходу", text_color="gray")
        info_label.pack(side="bottom", pady=10)

    # --- Callbacks (Реакції на дії в GUI) ---
    def on_cps_change(self, value):
        self.cps_value_label.configure(text=f"{value:.1f}")
        self.update_engine_settings()

    def on_random_change(self, value):
        self.rand_value_label.configure(text=f"{value:.0f}%")
        self.update_engine_settings()

    def on_button_change(self, value):
        self.update_engine_settings()

    def update_engine_settings(self):
        """Передає поточні значення з GUI у двигун"""
        self.engine.update_settings("target_cps", self.cps_var.get())
        self.engine.update_settings("randomness_pct", self.random_var.get())
        self.engine.update_settings("button", self.button_var.get())

    def toggle_clicking_gui(self):
        """Викликається при натисканні кнопки в GUI або гарячої клавіші"""
        is_active = self.engine.toggle()
        self.update_gui_state(is_active)

    def update_gui_state(self, is_active):
        """Оновлює вигляд кнопки та статус"""
        if is_active:
            self.toggle_btn.configure(text="СТОП (HotKey: S)", fg_color="#c42b1c", hover_color="#a02317") # Червоний колір
            self.status_var.set("Статус: АКТИВНО! Клікаю...")
        else:
            self.toggle_btn.configure(text="СТАРТ (HotKey: S)", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#3273af", "#1a487d"]) # Стандартний синій
            self.status_var.set("Статус: НЕАКТИВНО")

    # --- Обробка гарячих клавіш ---
    def on_hotkey_press(self, key):
        """Цей метод викликається з потоку pynput"""
        try:
            if key.char == self.hotkey_char:
                # ВАЖЛИВО: Не можна змінювати GUI з іншого потоку напряму.
                # Використовуємо .after(0, callback), щоб запланувати виконання
                # методу в головному потоці GUI.
                self.after(0, self.toggle_clicking_gui)
        except AttributeError:
            pass

    def on_closing(self):
        """Коректне завершення роботи при закритті вікна"""
        print("Завершення роботи...")
        self.engine.stop_engine()
        self.listener.stop()
        self.destroy()


if __name__ == "__main__":
    app = AutoClickerApp()
    # Встановлюємо обробник закриття вікна (хрестик)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()