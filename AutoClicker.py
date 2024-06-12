import pyautogui
import threading
import time
from pynput import keyboard

# Визначаємо змінні
button = 'left'  # Кнопка миші для кліка ('left', 'right', 'middle')
start_stop_key = keyboard.KeyCode(char='s')  # Гаряча клавіша для запуску та зупинки автоклікера
exit_key = keyboard.KeyCode(char='e')  # Гаряча клавіша для виходу з програми

class AutoClicker(threading.Thread):
    def __init__(self, button):
        super().__init__()
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                pyautogui.click(button=self.button)
            time.sleep(0.1)

def on_press(key):
    if key == start_stop_key:
        if click_thread.running:
            click_thread.stop_clicking()
        else:
            click_thread.start_clicking()
    elif key == exit_key:
        click_thread.exit()
        return False

if __name__ == "__main__":
    click_thread = AutoClicker(button)
    click_thread.start()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
