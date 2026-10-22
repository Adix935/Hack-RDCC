import time
import math
from shared_state import current_state

def update_mock_state():
    t = time.time()
    
    current_state["nose_x"] = 0.5 + math.sin(t * 0.8) * 0.1
    current_state["nose_y"] = 0.5 + math.cos(t * 0.5) * 0.1
    
    # Click stânga la fiecare 4 secunde
    if int(t * 10) % 40 == 0:
        current_state["action_click"] = True
        
    # Click dreapta la fiecare 6 secunde
    if int(t * 10) % 60 == 30:
        current_state["action_right_click"] = True
        
    # Scroll o dată la 5 secunde (alternând sus și jos)
    if int(t) % 5 == 0:
        # Dacă secunda curentă e multiplu de 10, dăm scroll sus (1), altfel jos (-1)
        current_state["action_scroll"] = 1 if int(t) % 10 == 0 else -1
    else:
        current_state["action_scroll"] = 0