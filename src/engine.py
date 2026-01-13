import threading
import time
import random
import pyautogui
from src.config import (
    DEFAULT_CPS, DEFAULT_RANDOMNESS, DEFAULT_BUTTON, DEFAULT_HOTKEY,
    CPS_MIN, CPS_MAX, RANDOMNESS_MIN, RANDOMNESS_MAX, VALID_BUTTONS,
    MIN_DELAY, IDLE_SLEEP
)


class ClickerEngine(threading.Thread):
    """
    Клас, що відповідає виключно за логіку клікання у фоновому потоці.
    Він не знає нічого про GUI.
    
    Thread-safe завдяки threading.Lock() для критичних секцій.
    """
    def __init__(self):
        super().__init__()
        self.daemon = True
        
        # Thread-safe флаги з локами
        self._lock = threading.Lock()
        self._clicking = False
        self._running = True
        
        # Налаштування (словник безпечний для простих присвоєнь під GIL)
        self.settings = {
            "target_cps": DEFAULT_CPS,
            "randomness_pct": DEFAULT_RANDOMNESS,
            "button": DEFAULT_BUTTON,
        }

    def update_settings(self, key, value):
        """
        Безпечне оновлення налаштувань з GUI потоку з валідацією.
        
        Args:
            key: назва параметра
            value: нове значення
            
        Returns:
            bool: True якщо оновлення успішне, False якщо валідація не пройшла
        """
        # Валідація
        if key == "target_cps":
            if not (CPS_MIN <= value <= CPS_MAX):
                print(f"[Engine] Помилка: CPS має бути від {CPS_MIN} до {CPS_MAX}")
                return False
        elif key == "randomness_pct":
            if not (RANDOMNESS_MIN <= value <= RANDOMNESS_MAX):
                print(f"[Engine] Помилка: Рандомність має бути від {RANDOMNESS_MIN} до {RANDOMNESS_MAX}%")
                return False
        elif key == "button":
            if value not in VALID_BUTTONS:
                print(f"[Engine] Помилка: кнопка має бути однією з {VALID_BUTTONS}")
                return False
        
        self.settings[key] = value
        return True

    def start_clicking(self):
        """Запуск клікання з thread-safe локом"""
        with self._lock:
            self._clicking = True
        print("[Engine] Старт клікання")

    def stop_clicking(self):
        """Зупинка клікання з thread-safe локом"""
        with self._lock:
            self._clicking = False
        print("[Engine] Стоп клікання")

    def toggle(self):
        """Toggle режим клікання, повертає новий стан"""
        with self._lock:
            self._clicking = not self._clicking
            result = self._clicking
        
        if result:
            print("[Engine] Старт клікання")
        else:
            print("[Engine] Стоп клікання")
        
        return result

    def stop_engine(self):
        """Повна зупинка потоку перед виходом"""
        with self._lock:
            self._clicking = False
            self._running = False

    def _calculate_delay(self):
        """
        Розраховує затримку між кліками на основі CPS та рандому.
        Рандомність застосовується як ±% від базової затримки.
        """
        cps = self.settings["target_cps"]
        if cps <= 0:
            cps = 0.1
        
        base_delay = 1.0 / cps
        random_pct = self.settings["randomness_pct"] / 100.0
        
        if random_pct > 0:
            variation = base_delay * random_pct
            min_delay = base_delay - variation
            max_delay = base_delay + variation
            return max(MIN_DELAY, random.uniform(min_delay, max_delay))
        else:
            return base_delay

    def run(self):
        """Головний цикл потоку з обробкою помилок"""
        print("[Engine] Потік запущено")
        
        while True:
            with self._lock:
                if not self._running:
                    break
                clicking = self._clicking
            
            if clicking:
                try:
                    pyautogui.click(button=self.settings["button"])
                    delay = self._calculate_delay()
                    time.sleep(delay)
                except Exception as e:
                    print(f"[Engine] Помилка при кліканні: {e}")
                    # Продовжуємо роботу, але з більшою затримкою
                    time.sleep(0.1)
            else:
                # Ефективне очікування коли не клікаємо
                time.sleep(IDLE_SLEEP)
        
        print("[Engine] Потік завершено")
