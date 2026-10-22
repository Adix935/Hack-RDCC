import time
from shared_state import current_state, config
from mock_generator import update_mock_data
from math_utils import map_to_screen
from mouse_engine import MouseController

def main():
    mouse = MouseController(config["screen_width"], config["screen_height"])
    print("Actuator COMPLET pornit. Ține apăsat SPACE pentru a opri.")
    
    # Pauză să pui mâna pe Space
    time.sleep(2)
    
    while True:
        # 1. Generezi datele false
        update_mock_data()
        
        # 2. Mapezi coordonatele pe ecran
        target_x = map_to_screen(current_state["nose_x"], config["active_zone"]["min_x"], config["active_zone"]["max_x"], config["screen_width"])
        target_y = map_to_screen(current_state["nose_y"], config["active_zone"]["min_y"], config["active_zone"]["max_y"], config["screen_height"])
        
        # 3. Miști cursorul netezit
        mouse.move_cursor(target_x, target_y, config["smoothing_factor"])
        
        # 4. Apelezi acțiunile (Click-uri, Drag, Scroll) pe baza testului
        if current_state["test_left_click"]: mouse.left_click()
        if current_state["test_right_click"]: mouse.right_click()
        if current_state["test_double_click"]: mouse.double_click()
        if current_state["test_toggle_drag"]: mouse.toggle_drag()
        
        if current_state["test_scroll_y"] != 0 or current_state["test_scroll_x"] != 0:
            mouse.scroll(current_state["test_scroll_y"], current_state["test_scroll_x"])
        
        # 5. Verifici Kill-Switch-ul
        mouse.check_failsafe()
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()