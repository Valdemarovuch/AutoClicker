# AutoClicker Project Conventions

## Project Overview
A desktop auto-clicker utility written in Python using CustomTkinter for GUI and PyAutoGUI for mouse automation. The project implements a **separation-of-concerns architecture** with a background clicking engine (threading) decoupled from the GUI layer and organized into modular components.

## Project Structure
```
src/
├── __init__.py          # Package marker
├── main.py              # Entry point (pyautogui config + app startup)
├── config.py            # Constants, ranges, defaults (colors, timings, validation bounds)
├── engine.py            # ClickerEngine (background thread, thread-safe with locks)
└── ui.py                # AutoClickerApp (CustomTkinter GUI layer)
```

## Architecture & Components

### Thread-Safe GUI-Engine Pattern (Revised)
- **ClickerEngine** (`src/engine.py`): Background thread (`threading.Thread`) with `threading.Lock()` on critical state (`_clicking`, `_running`)
- **AutoClickerApp** (`src/ui.py`): CustomTkinter window that manages UI and delegates commands to engine
- **config.py**: Centralized constants, validation ranges, defaults—avoids magic numbers
- **Critical Rule**: Never access GUI widgets from `ClickerEngine`; never block the main thread from `ClickerEngine`
- **GUI Thread Safety**: Use `.after(0, callback)` to schedule operations in the main GUI thread from external threads (see `on_hotkey_press` in `ui.py`)

### Settings Flow & Validation
Settings flow unidirectionally from GUI → Engine via `engine.update_settings(key, value)`:
```python
# GUI event → update engine with validation
success = self.engine.update_settings("target_cps", self.cps_var.get())
if not success:
    # Sync GUI back to engine values on validation failure
    self.cps_var.set(self.engine.settings["target_cps"])
```
**Validation ranges** (defined in `config.py`):
- `target_cps`: 1.0–200.0 clicks/sec
- `randomness_pct`: 0–100%
- `button`: "left", "right", or "middle"

Returns `False` if validation fails; UI resynchronizes with engine state.

### Hotkey Handling
- `pynput.keyboard.Listener` runs on a separate thread and calls `on_hotkey_press` externally
- Never modify GUI directly from `on_hotkey_press`—must reschedule with `.after(0, ...)` to marshal calls back to the main thread

## Key Implementation Patterns

### Thread-Safe State Management
`ClickerEngine` uses explicit `threading.Lock()` for critical sections:
```python
def toggle(self):
    with self._lock:
        self._clicking = not self._clicking
        result = self._clicking
    return result
```
Always acquire lock when reading/writing `_clicking` or `_running` flags from different threads.

### Hotkey Configuration
Hotkey is now configurable via GUI text input in `AutoClickerApp._setup_ui()`:
- User enters a single letter in the hotkey field
- Pressing "Оновити" calls `on_hotkey_update()` which validates and updates `self.hotkey_char`
- Default hotkey: 's' (set in `config.DEFAULT_HOTKEY`)
- Validation: `if len(new_key) == 1 and new_key.isalpha()`
Randomness is applied as a ±percentage variation around base delay:
```python
# 20% randomness on 0.1s base = ±0.02s variation
variation = base_delay * (randomness_pct / 100.0)
delay = random.uniform(base_delay - variation, base_delay + variation)
```
Always clamp minimum delay to 0.001s to prevent issues.

### Efficient Idle Waiting
When not clicking, the engine sleeps 50ms (`time.sleep(0.05)`) rather than spinning—reduces CPU usage while maintaining responsive toggle response.

### Graceful Shutdown
- `stop_engine()` sets both `_running = False` and `_clicking = False` with lock protection
- `on_closing()` calls both `engine.stop_engine()` and `listener.stop()` before destroying the window
- The daemon thread exits automatically when the main program closes
- All critical sections in `run()` use `with self._lock:` to check `_running` safely

### Error Handling
`ClickerEngine.run()` wraps `pyautogui.click()` in try-except:
```python
try:
    pyautogui.click(button=self.settings["button"])
    delay = self._calculate_delay()
    time.sleep(delay)
except Exception as e:
    print(f"[Engine] Помилка при кліканні: {e}")
    time.sleep(0.1)  # Backoff on error
```
Continues operation on click failures rather than crashing the thread.

## UI/UX Conventions
- Use Ukrainian labels and status messages (see `_setup_ui` for examples)
- CPS slider: 1–50 range
- Randomness slider: 0–100% range
- Color scheme: Red (#c42b1c) for STOP state, blue (#3a7ebf) for START state
- Hotkey is hardcoded to 'S'—configurable via `self.hotkey_char` if needed

## Dependencies
- **customtkinter**: Modern dark-themed GUI
- **pyautogui**: Mouse clicking; `FAILSAFE = False` disables corner-screen safety
- **pynput**: Keyboard listener for hotkey capture
- **pillow**, **packaging**: Required by CustomTkinter

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src.main
# Or: python -c "from src.main import main; main()"
```

## Common Development Tasks

### Adding a New Setting
1. Add to `ClickerEngine.settings` dict with default
2. Add GUI widget (slider/input/option) in `_setup_ui`
3. Create callback (e.g., `on_xxx_change`) that calls `update_engine_settings()`
4. Update `update_engine_settings()` to pass new setting to engine

### Testing
Run directly: `python AutoClicker.py`  
No automated test suite; manual testing via GUI toggle and hotkey.

### Debugging
- Print statements in `ClickerEngine.run()` use `[Engine]` prefix
- GUI callbacks log to console via `print()`
- Use task manager to force-kill if frozen

## Project-Specific Gotchas
- **PyAutoGUI click timing**: Actual click may be slightly delayed; adjust CPS if click rate is inconsistent
- **Cross-thread GUI updates**: Always use `.after()` from non-GUI threads—direct modifications cause crashes
- **Random seed**: No explicit seeding; uses system clock
