import math
import time
from shared_state import current_state

def update_mock_data():
    t = time.time()
    
    # Nasul se mișcă lent în cerc
    current_state["nose_x"] = 0.5 + math.sin(t * 0.8) * 0.1
    current_state["nose_y"] = 0.5 + math.cos(t * 0.5) * 0.1
    
    # Resetăm toate acțiunile la fiecare cadru
    current_state["test_left_click"] = False
    current_state["test_right_click"] = False
    current_state["test_double_click"] = False
    current_state["test_toggle_drag"] = False
    current_state["test_scroll_y"] = 0
    current_state["test_scroll_x"] = 0

    # Un ciclu repetitiv de 15 secunde pentru a testa tot
    cycle = int(t * 10) % 150  # Înmulțim cu 10 ca să prindem fracțiuni de secundă
    
    if cycle == 30:   # Secunda 3
        current_state["test_left_click"] = True
    elif cycle == 60: # Secunda 6
        current_state["test_right_click"] = True
    elif cycle == 90: # Secunda 9
        current_state["test_double_click"] = True
    elif 110 <= cycle <= 112: 
        current_state["test_toggle_drag"] = True
    elif 118 <= cycle <= 120: 
        current_state["test_toggle_drag"] = True # Drop
        
    # TESTĂM TOATE CELE 4 DIRECȚII DE SCROLL:
    elif 125 <= cycle <= 129: 
        current_state["test_scroll_y"] = 1  # Scroll SUS
    elif 130 <= cycle <= 134: 
        current_state["test_scroll_y"] = -1 # Scroll JOS
    elif 135 <= cycle <= 139: 
        current_state["test_scroll_x"] = -1 # Scroll STÂNGA
    elif 140 <= cycle <= 144: 
        current_state["test_scroll_x"] = 1  # Scroll DREAPTA