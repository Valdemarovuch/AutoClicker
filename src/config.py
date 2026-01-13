# --- Констатни та налаштування ---

# Дефолтні значення
DEFAULT_CPS = 10.0
DEFAULT_RANDOMNESS = 20.0
DEFAULT_BUTTON = "left"
DEFAULT_HOTKEY = "s"

# Діапазони валідації
CPS_MIN = 1.0
CPS_MAX = 200.0  # Максимум 200 кліків на секунду

RANDOMNESS_MIN = 0.0
RANDOMNESS_MAX = 100.0

VALID_BUTTONS = ["left", "right", "middle"]

MIN_DELAY = 0.001  # Мінімальна затримка між кліками

# GUI налаштування
WINDOW_TITLE = "Pro AutoClicker by AI"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500

# Кольори (UI/UX)
COLOR_STOP = "#c42b1c"  # Червоний для STOP
COLOR_STOP_HOVER = "#a02317"
COLOR_START = ["#3a7ebf", "#1f538d"]  # Синій для START
COLOR_START_HOVER = ["#3273af", "#1a487d"]

# Таймаути
IDLE_SLEEP = 0.05  # Затримка коли не клікаємо
GUI_MARSHAL_DELAY = 0  # Для .after() при cross-thread call
