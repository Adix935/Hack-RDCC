import ctypes
import pyautogui
import keyboard
from math_utils import lerp

pyautogui.FAILSAFE = True

class MouseController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.curr_x = float(screen_w // 2)
        self.curr_y = float(screen_h // 2)
        
        # Ținem minte dacă mouse-ul este apăsat (pentru Drag & Drop)
        self.is_dragging = False

    def move_cursor(self, target_x, target_y, alpha):
        self.curr_x = lerp(self.curr_x, target_x, alpha)
        self.curr_y = lerp(self.curr_y, target_y, alpha)
        ctypes.windll.user32.SetCursorPos(int(self.curr_x), int(self.curr_y))

    def scroll(self, direction_y, direction_x=0):
        # Înmulțim cu 120 pentru ca Windows să detecteze un pas complet de scroll
        if abs(direction_y) > 0:
            pyautogui.scroll(int(direction_y * 120))
            print(f"[ACTUATOR] Scroll Vertical: {direction_y}")
        
        if abs(direction_x) > 0:
            pyautogui.hscroll(int(direction_x * 120))
            print(f"[ACTUATOR] Scroll Orizontal: {direction_x}")

    def left_click(self):
        pyautogui.click()
        print("[ACTUATOR] Click Stânga")

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
            print("[ACTUATOR] Drag PORNIT (mouse ținut apăsat)")
        else:
            pyautogui.mouseUp()
            print("[ACTUATOR] Drop EXECUTAT (mouse eliberat)")

    def check_failsafe(self):
        if keyboard.is_pressed('space'):
            if self.is_dragging:
                pyautogui.mouseUp()
            print("\n[KILL-SWITCH] Tasta SPACE a fost apăsată. Ieșire de urgență!")
            exit()