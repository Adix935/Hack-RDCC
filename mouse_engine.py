import ctypes
import pyautogui
import keyboard
from math_utils import lerp

# Dezactivăm failsafe-ul pyautogui (avem propriul kill-switch pe tasta Space)
pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.curr_x = float(screen_w // 2)
        self.curr_y = float(screen_h // 2)
        
        # Ținem minte dacă mouse-ul este apăsat (pentru Drag & Drop)
        self.is_dragging = False
        self.is_sleeping = False

    def move_cursor(self, vel_x, vel_y):
        # Adăugăm viteza calculată de Persoana 1 la poziția curentă
        self.curr_x += vel_x
        self.curr_y += vel_y
        
        # Clamp: ne asigurăm că mouse-ul nu iese din marginile monitorului
        self.curr_x = max(0.0, min(self.curr_x, float(self.screen_w - 1)))
        self.curr_y = max(0.0, min(self.curr_y, float(self.screen_h - 1)))
        
        ctypes.windll.user32.SetCursorPos(int(self.curr_x), int(self.curr_y))

    def scroll(self, direction_y, direction_x=0):
        # pyautogui.scroll(n) = n "click-uri" de scroll wheel
        if abs(direction_y) > 0:
            pyautogui.scroll(int(direction_y))
        if abs(direction_x) > 0:
            pyautogui.hscroll(int(direction_x))

    def left_click(self):
        pyautogui.click()
        print("[ACTUATOR] Click Stanga")

    def right_click(self):
        pyautogui.click(button='right')
        print("[ACTUATOR] Click Dreapta")

    def double_click(self):
        pyautogui.doubleClick()
        print("[ACTUATOR] Dublu Click")

    def toggle_drag(self):
        self.is_dragging = not self.is_dragging
        if self.is_dragging:
            pyautogui.mouseDown()
            print("[ACTUATOR] Drag PORNIT (mouse tinut apasat)")
        else:
            pyautogui.mouseUp()
            print("[ACTUATOR] Drop EXECUTAT (mouse eliberat)")

    def toggle_sleep(self):
        """Comută modul sleep (pauză). Mouse-ul nu mai execută comenzi."""
        self.is_sleeping = not self.is_sleeping
        if self.is_sleeping:
            print("[ACTUATOR] SLEEP MODE ACTIVAT - Mouse-ul este in pauza")
        else:
            print("[ACTUATOR] SLEEP MODE DEZACTIVAT - Mouse-ul este activ")

    def check_failsafe(self):
        """Verifică kill-switch-ul (tasta Space). Returnează True dacă trebuie să ne oprim."""
        try:
            if keyboard.is_pressed('space'):
                if self.is_dragging:
                    pyautogui.mouseUp()
                    self.is_dragging = False
                print("\n[KILL-SWITCH] Tasta SPACE a fost apasata. Iesire de urgenta!")
                return True
        except Exception:
            pass
        return False
