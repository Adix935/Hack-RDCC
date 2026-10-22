import pyautogui

screen_w, screen_h = pyautogui.size()

current_state = {
    "nose_x": 0.5,
    "nose_y": 0.5,
    "test_left_click": False,
    "test_right_click": False,
    "test_double_click": False,
    "test_toggle_drag": False,
    "test_scroll_y": 0,
    "test_scroll_x": 0
}

config = {
    "screen_width": screen_w,
    "screen_height": screen_h,
    "smoothing_factor": 0.15,
    "active_zone": {
        "min_x": 0.35, "max_x": 0.65,
        "min_y": 0.35, "max_y": 0.65
    }
}