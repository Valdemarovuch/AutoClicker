import customtkinter as ctk
from pynput import keyboard
from src.engine import ClickerEngine
from src.config import (
    DEFAULT_HOTKEY, WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_STOP, COLOR_STOP_HOVER, COLOR_START, COLOR_START_HOVER,
    GUI_MARSHAL_DELAY
)


class AutoClickerApp(ctk.CTk):
    """
    Головне вікно програми. Відповідає за GUI та делегує команди ClickerEngine.
    Thread-safe комунікація з engine через .after() для cross-thread GUI updates.
    """
    def __init__(self):
        super().__init__()

        # Ініціалізація двигуна
        self.engine = ClickerEngine()
        self.engine.start()

        # Налаштування гарячої клавіші
        self.hotkey_char = DEFAULT_HOTKEY
        self.listener = keyboard.Listener(on_press=self.on_hotkey_press)
        self.listener.start()

        # GUI налаштування
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Змінні для віджетів
        self.cps_var = ctk.DoubleVar(value=self.engine.settings["target_cps"])
        self.random_var = ctk.DoubleVar(value=self.engine.settings["randomness_pct"])
        self.button_var = ctk.StringVar(value=self.engine.settings["button"])
        self.hotkey_var = ctk.StringVar(value=self.hotkey_char.upper())
        self.status_var = ctk.StringVar(value="Статус: НЕАКТИВНО")

        self._setup_ui()
        self.update_engine_settings()

    def _setup_ui(self):
        """Створення та розміщення елементів інтерфейсу"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(
            main_frame, text="Налаштування Клікера", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # --- Секція CPS (Швидкість) ---
        cps_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cps_frame.pack(fill="x", pady=(0, 15))
        
        cps_label_title = ctk.CTkLabel(cps_frame, text="Швидкість (CPS):", anchor="w")
        cps_label_title.pack(side="left", padx=(10, 0))
        
        self.cps_value_label = ctk.CTkLabel(
            cps_frame, text=f"{self.cps_var.get():.1f}", width=40
        )
        self.cps_value_label.pack(side="right", padx=(0, 10))

        cps_slider = ctk.CTkSlider(
            main_frame, from_=1, to=200, variable=self.cps_var, 
            command=self.on_cps_change
        )
        cps_slider.pack(fill="x", padx=10, pady=(0, 10))

        # --- Секція Рандомності (Олюднення) ---
        rand_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        rand_frame.pack(fill="x", pady=(0, 15))

        rand_label_title = ctk.CTkLabel(
            rand_frame, text="Олюднення (Рандом %):", anchor="w"
        )
        rand_label_title.pack(side="left", padx=(10, 0))

        self.rand_value_label = ctk.CTkLabel(
            rand_frame, text=f"{self.random_var.get():.0f}%", width=40
        )
        self.rand_value_label.pack(side="right", padx=(0, 10))

        rand_slider = ctk.CTkSlider(
            main_frame, from_=0, to=100, variable=self.random_var, 
            command=self.on_random_change
        )
        rand_slider.pack(fill="x", padx=10, pady=(0, 10))

        # --- Секція Вибору кнопки ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 20), padx=10)
        
        btn_label = ctk.CTkLabel(btn_frame, text="Кнопка миші:")
        btn_label.pack(side="left")

        btn_option = ctk.CTkOptionMenu(
            btn_frame, values=["left", "right", "middle"], 
            variable=self.button_var, command=self.on_button_change
        )
        btn_option.pack(side="right")

        # --- Секція Гарячої клавіші ---
        hotkey_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        hotkey_frame.pack(fill="x", pady=(10, 20), padx=10)
        
        hotkey_label = ctk.CTkLabel(hotkey_frame, text="Гаряча клавіша:")
        hotkey_label.pack(side="left")

        self.hotkey_input = ctk.CTkEntry(
            hotkey_frame, width=50, textvariable=self.hotkey_var, justify="center"
        )
        self.hotkey_input.pack(side="left", padx=(10, 5))

        hotkey_btn = ctk.CTkButton(
            hotkey_frame, text="Оновити", width=80, command=self.on_hotkey_update
        )
        hotkey_btn.pack(side="left", padx=(0, 5))

        # --- Головна кнопка Старт/Стоп ---
        self.toggle_btn = ctk.CTkButton(
            main_frame, text="СТАРТ (HotKey: S)", height=50, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            command=self.toggle_clicking_gui
        )
        self.toggle_btn.pack(fill="x", padx=20, pady=(10, 5))
        
        # Статус бар
        self.status_label = ctk.CTkLabel(
            main_frame, textvariable=self.status_var, 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(5, 10))

        # Інфо
        info_label = ctk.CTkLabel(
            self, text="Натисни гарячу клавішу для старту/стопу\nЗакрий вікно для виходу", 
            text_color="gray"
        )
        info_label.pack(side="bottom", pady=10)

    # --- Callbacks ---
    def on_cps_change(self, value):
        self.cps_value_label.configure(text=f"{value:.1f}")
        self.update_engine_settings()

    def on_random_change(self, value):
        self.rand_value_label.configure(text=f"{value:.0f}%")
        self.update_engine_settings()

    def on_button_change(self, value):
        self.update_engine_settings()

    def on_hotkey_update(self):
        """Оновлення гарячої клавіші"""
        new_key = self.hotkey_var.get().lower().strip()
        if len(new_key) == 1 and new_key.isalpha():
            self.hotkey_char = new_key
            print(f"[GUI] Гаряча клавіша змінена на '{new_key.upper()}'")
        else:
            self.hotkey_var.set(self.hotkey_char.upper())
            print("[GUI] Помилка: введіть одну букву")

    def update_engine_settings(self):
        """Передає поточні значення з GUI у двигун з валідацією"""
        success = True
        success &= self.engine.update_settings("target_cps", self.cps_var.get())
        success &= self.engine.update_settings("randomness_pct", self.random_var.get())
        success &= self.engine.update_settings("button", self.button_var.get())
        
        if not success:
            # Синхронізуємо GUI назад з engine
            self.cps_var.set(self.engine.settings["target_cps"])
            self.random_var.set(self.engine.settings["randomness_pct"])
            self.button_var.set(self.engine.settings["button"])

    def toggle_clicking_gui(self):
        """Викликається при натисканні кнопки в GUI або гарячої клавіші"""
        is_active = self.engine.toggle()
        self.update_gui_state(is_active)

    def update_gui_state(self, is_active):
        """Оновлює вигляд кнопки та статус"""
        if is_active:
            self.toggle_btn.configure(
                text=f"СТОП (HotKey: {self.hotkey_char.upper()})", 
                fg_color=COLOR_STOP, hover_color=COLOR_STOP_HOVER
            )
            self.status_var.set("Статус: АКТИВНО! Клікаю...")
        else:
            self.toggle_btn.configure(
                text=f"СТАРТ (HotKey: {self.hotkey_char.upper()})", 
                fg_color=COLOR_START, hover_color=COLOR_START_HOVER
            )
            self.status_var.set("Статус: НЕАКТИВНО")

    # --- Обробка гарячих клавіш ---
    def on_hotkey_press(self, key):
        """
        Цей метод викликається з потоку pynput.
        ВАЖЛИВО: Маршалюємо GUI-оновлення в головний потік через .after()
        """
        try:
            if key.char == self.hotkey_char:
                self.after(GUI_MARSHAL_DELAY, self.toggle_clicking_gui)
        except AttributeError:
            pass

    def on_closing(self):
        """Коректне завершення роботи при закритті вікна"""
        print("Завершення роботи...")
        self.engine.stop_engine()
        self.listener.stop()
        self.destroy()
