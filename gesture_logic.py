# gesture_logic.py
import time

class GestureProcessor:
    def __init__(self):
        # Praguri pentru detectie
        self.EYE_THRESH = 0.22
        self.MOUTH_THRESH = 0.35
        
        # Timere pentru ochi (salvează momentul în care ochiul s-a închis)
        self.t_left_closed = 0.0
        self.t_right_closed = 0.0
        self.t_both_closed = 0.0
        
        # Stări anterioare (pentru a detecta momentul exact al deschiderii)
        self.was_left_closed = False
        self.was_right_closed = False
        self.was_both_closed = False
        
        # Flaguri pentru a nu repeta acțiunile cât timp ochii sunt ținuți închiși
        self.action_triggered_this_blink = False
        
        # Stări persistente ale sistemului
        self.is_dragging = False
        self.is_sleeping = False

    def process(self, ratio_l, ratio_r, ratio_mouth, vel_x, vel_y):
        """
        Analizează starea curentă și returnează un dicționar cu acțiunile de executat.
        """
        now = time.time()
        
        # 1. Determinăm starea brută a ochilor și a gurii
        l_closed = ratio_l < self.EYE_THRESH
        r_closed = ratio_r < self.EYE_THRESH
        mouth_open = ratio_mouth > self.MOUTH_THRESH
        
        # Stări exclusive (să nu interpretăm clipitul normal ca wink)
        both_closed = l_closed and r_closed
        left_wink = l_closed and not r_closed
        right_wink = r_closed and not l_closed

        # Dicționarul cu comenzi pe care actuatorul le va citi și executa
        commands = {
            "move": (0.0, 0.0),
            "scroll": (0.0, 0.0),
            "left_click": False,
            "right_click": False,
            "double_click": False,
            "toggle_drag": False,
            "toggle_sleep": False
        }

        # ==========================================
        # LOGICA PENTRU AMBII OCHI (Double Click & Sleep)
        # ==========================================
        if both_closed:
            if not self.was_both_closed:
                self.t_both_closed = now
                self.action_triggered_this_blink = False
            else:
                duration = now - self.t_both_closed
                # Sleep mode: Peste 3 secunde. Se declanșează instant.
                if duration > 3.0 and not self.action_triggered_this_blink:
                    commands["toggle_sleep"] = True
                    self.is_sleeping = not self.is_sleeping
                    self.action_triggered_this_blink = True
        else:
            if self.was_both_closed:
                duration = now - self.t_both_closed
                # Dublu click: Între 1 și 3 secunde, se declanșează la DESCHIDEREA ochilor
                if 1.0 < duration <= 3.0 and not self.action_triggered_this_blink:
                    if not self.is_sleeping:
                        commands["double_click"] = True

        # ==========================================
        # LOGICA PENTRU OCHIUL STÂNG (Click & Drag/Drop)
        # ==========================================
        if left_wink and not self.is_sleeping:
            if not self.was_left_closed:
                self.t_left_closed = now
                self.action_triggered_this_blink = False
            else:
                duration = now - self.t_left_closed
                # Selectare Drag (menținere ochi stâng > 1s). Se activează instant.
                if duration > 1.0 and not self.action_triggered_this_blink and not self.is_dragging:
                    commands["toggle_drag"] = True
                    self.is_dragging = True
                    self.action_triggered_this_blink = True
        else:
            if self.was_left_closed and not self.was_both_closed:
                duration = now - self.t_left_closed
                # Dacă a fost ținut sub 1 secundă (Wink scurt)
                if duration <= 1.0 and not self.action_triggered_this_blink:
                    if self.is_dragging:
                        # Dacă eram în Drag, un wink scurt deblochează (Drop)
                        commands["toggle_drag"] = True
                        self.is_dragging = False
                    else:
                        # Altfel e click normal
                        commands["left_click"] = True

        # ==========================================
        # LOGICA PENTRU OCHIUL DREPT (Click Dreapta)
        # ==========================================
        if right_wink and not self.is_sleeping:
            if not self.was_right_closed:
                self.t_right_closed = now
        else:
            if self.was_right_closed and not self.was_both_closed:
                duration = now - self.t_right_closed
                # Wink scurt cu ochiul drept (< 1s) = Click dreapta
                if duration <= 1.0 and not self.is_sleeping:
                    commands["right_click"] = True

        # ==========================================
        # LOGICA PENTRU CURSOR ȘI SCROLL (Nas + Gură)
        # ==========================================
        if not self.is_sleeping:
            if mouth_open:
                # Gura deschisă -> Viteza se duce în Scroll, cursorul îngheață
                commands["scroll"] = (vel_x, vel_y)
            else:
                # Gura închisă -> Viteza mută cursorul
                commands["move"] = (vel_x, vel_y)

        # Actualizare stări pentru cadrul următor
        self.was_both_closed = both_closed
        self.was_left_closed = left_wink
        self.was_right_closed = right_wink

        return commands