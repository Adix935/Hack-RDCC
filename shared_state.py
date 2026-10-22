# shared_state.py

import pyautogui

# Detectăm automat rezoluția monitorului pe care rulează aplicația
screen_w, screen_h = pyautogui.size()

current_state = {
    "nose_x": 0.5,
    "nose_y": 0.5,
    "action_click": False,
    "action_right_click": False,
    "action_scroll": 0
}

config = {
    "screen_width": screen_w,   # Se setează dinamic (ex: 1920, 1366, 2560 etc.)
    "screen_height": screen_h,  # Se setează dinamic (ex: 1080, 768, 1440 etc.)
    "smoothing_factor": 0.15,
    "active_zone": {
        "min_x": 0.35,
        "max_x": 0.65,
        "min_y": 0.35,
        "max_y": 0.65
    }
}