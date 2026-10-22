# mouse_engine.py

import ctypes
import pyautogui
import keyboard
import time
from math_utils import lerp

# Activăm protecția nativă din pyautogui.
# Dacă algoritmul o ia razna, mută fizic mouse-ul în oricare din cele 4 colțuri ale ecranului,
# iar programul va arunca o eroare și se va opri automat.
pyautogui.FAILSAFE = True

class MouseController:
    def __init__(self):
        # Inițializăm cursorul în centrul unui ecran 1920x1080
        self.curr_x = 960.0
        self.curr_y = 540.0
        # Timpul la care s-a dat ultimul click (pentru cooldown)
        self.last_click = 0.0

    def move(self, target_x, target_y, alpha):
        """
        Netezește mișcarea folosind LERP și mută cursorul instantaneu folosind Windows API.
        """
        # Calculăm noua poziție, "alunecând" spre țintă
        self.curr_x = lerp(self.curr_x, target_x, alpha)
        self.curr_y = lerp(self.curr_y, target_y, alpha)
        
        # Apel nativ de sistem (fără lag). Necesită numere întregi (pixeli).
        ctypes.windll.user32.SetCursorPos(int(self.curr_x), int(self.curr_y))

    def click(self):
        """
        Execută un click stânga, protejat de un cooldown pentru a preveni spam-ul.
        """
        now = time.time()
        # Cooldown de 0.5 secunde
        if now - self.last_click > 0.5:
            pyautogui.click()
            print("[ACȚIUNE] Click stânga executat!")
            self.last_click = now

    def right_click(self):
        """
        Execută un click dreapta, folosind același cooldown pentru siguranță.
        """
        now = time.time()
        if now - self.last_click > 0.5:
            pyautogui.click(button='right')
            print("[ACȚIUNE] Click dreapta executat!")
            self.last_click = now

    def scroll(self, direction):
        """
        Execută scroll. Direction va fi 1 (sus) sau -1 (jos).
        Multiplicatorul 100 definește numărul de "linii" derulate.
        """
        pyautogui.scroll(100 * direction)
        print(f"[ACȚIUNE] Scroll {'sus' if direction == 1 else 'jos'} executat!")

    def check_failsafe(self):
        """
        Oprește forțat programul dacă se apasă tasta ESC.
        """
        if keyboard.is_pressed('esc'):
            print("\n[SISTEM OPRIT] Tasta ESC a fost apăsată. Se închide aplicația...")
            exit()