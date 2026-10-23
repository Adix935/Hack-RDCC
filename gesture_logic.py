import time

class GestureProcessor:
    def __init__(self):
        # Praguri pentru detectie
        self.EYE_THRESH = 0.22
        self.WINK_THRESH = 0.16
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
        self.drag_beep_played = False
 
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

        l_wink_closed = ratio_l < self.WINK_THRESH
        r_wink_closed = ratio_r < self.WINK_THRESH

        mouth_open = ratio_mouth > self.MOUTH_THRESH

        # Stări exclusive (să nu interpretăm clipitul normal ca wink)
        both_closed = l_closed and r_closed
        left_wink = l_wink_closed and (ratio_r > self.EYE_THRESH + 0.02)
        right_wink = r_wink_closed and (ratio_l > self.EYE_THRESH + 0.02)

        # Dicționarul cu comenzi pe care actuatorul le va citi și executa
        commands = {
            "move": (0.0, 0.0),
            "scroll": (0.0, 0.0),
            "left_click": False,
            "right_click": False,
            "double_click": False,
            "toggle_drag": False,
            "toggle_sleep": False,
            "drag_ready_beep": False
        }

        # ==========================================
        # LOGICA PENTRU AMBII OCHI (Double Click & Sleep)
        # ==========================================
        if both_closed:
            if not self.was_both_closed:
                self.t_both_closed = now
                self.action_triggered_this_blink = False
                self.drag_beep_played = False  # Resetăm flag-ul
            else:
                duration = now - self.t_both_closed
                
                # --- NOU: Trimitem semnalul sonor fix când am intrat în intervalul valid ---
                if duration > 0.4 and not self.drag_beep_played and not self.action_triggered_this_blink:
                    commands["drag_ready_beep"] = True
                    self.drag_beep_played = True

                # Sleep mode: Peste 3 secunde. Se declanșează instant.
                if duration > 3.0 and not self.action_triggered_this_blink:
                    commands["toggle_sleep"] = True
                    self.is_sleeping = not self.is_sleeping
                    self.action_triggered_this_blink = True
        else:
            if self.was_both_closed:
                duration = now - self.t_both_closed
                # Drag & Drop: Între 0.4 și 1.5 secunde, se declanșează la DESCHIDEREA ochilor
                if 0.4 < duration <= 1.5 and not self.action_triggered_this_blink:
                    if not self.is_sleeping:
                        commands["toggle_drag"] = True
                        self.is_dragging = not self.is_dragging

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
                # Wink intenționat: ținut minim 0.15s, maxim 1s
                if duration <= 1.0 and not self.action_triggered_this_blink:
                    if self.is_dragging:
                        commands["toggle_drag"] = True
                        self.is_dragging = False
                    else:
                        commands["left_click"] = True

        # ==========================================
        # LOGICA PENTRU OCHIUL DREPT (Click)
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
