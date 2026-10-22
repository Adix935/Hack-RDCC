import time
from shared_state import current_state, config
from mock_generator import update_mock_state
from math_utils import map_to_screen
from mouse_engine import MouseController

def main():
    mouse = MouseController()
    print("==========================================")
    print("Sistemul de control a pornit.")
    print("Mouse-ul ar trebui să se miște singur acum.")
    print("-> Apasă tasta ESC pentru a opri imediat.")
    print("==========================================")
    
    while True:
        # 1. Preluăm datele (acum simulate, mai târziu le va prelua colegul din cameră)
        update_mock_state()
        
        # Extragem zona activă din configurație pentru a păstra codul curat
        az = config["active_zone"]
        
        # 2. Mapăm coordonatele nasului pe rezoluția ecranului
        target_x = map_to_screen(
            raw_val=current_state["nose_x"],
            min_bound=az["min_x"],
            max_bound=az["max_x"],
            max_res=config["screen_width"]
        )
        
        target_y = map_to_screen(
            raw_val=current_state["nose_y"],
            min_bound=az["min_y"],
            max_bound=az["max_y"],
            max_res=config["screen_height"]
        )
        
        # 3. Trimitem noile coordonate către motorul care controlează Windows-ul
        mouse.move(target_x, target_y, config["smoothing_factor"])
        
        # 4. Verificăm dacă s-a declanșat o acțiune
        if current_state["action_click"]:
            mouse.click()
            current_state["action_click"] = False 
            
        if current_state["action_right_click"]:
            mouse.right_click()
            current_state["action_right_click"] = False 
            
        if current_state["action_scroll"] != 0:
            mouse.scroll(current_state["action_scroll"])
            # Nu resetăm manual aici, lăsăm simulatorul/AI-ul să decidă când se oprește scroll-ul
            
        # 5. Sistemul de siguranță și limitarea utilizării procesorului
        mouse.check_failsafe()
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()