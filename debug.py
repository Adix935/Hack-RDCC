import cv2
import time

class DebugMonitor:
    def __init__(self, print_interval=0.2):
        self.last_print_time = 0
        self.print_interval = print_interval  # Intervalul in secunde pentru afisarea in terminal

    def draw_hud(self, image, state, vx, vy):
        """Desenează valorile AI în timp real direct pe fereastra video."""
        y_offset = 80
        color = (255, 255, 255) # Alb
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        thickness = 1

        cv2.putText(image, "--- AI STATS ---", (20, y_offset), font, scale, (0, 255, 255), thickness)
        cv2.putText(image, f"Nas X, Y: {state['nose_x']:.3f}, {state['nose_y']:.3f}", (20, y_offset + 20), font, scale, color, thickness)
        cv2.putText(image, f"Vx, Vy:   {vx:.1f}, {vy:.1f}", (20, y_offset + 40), font, scale, color, thickness)
        cv2.putText(image, f"Ochi St.: {state['left_eye_ratio']:.3f}", (20, y_offset + 60), font, scale, color, thickness)
        cv2.putText(image, f"Ochi Dr.: {state['right_eye_ratio']:.3f}", (20, y_offset + 80), font, scale, color, thickness)
        cv2.putText(image, f"Gura:     {state['mouth_ratio']:.3f}", (20, y_offset + 100), font, scale, color, thickness)
        
        return image

    def print_terminal(self, state, vx, vy):
        """Afișează log-urile în consolă la intervale regulate pentru a putea fi citite."""
        current_time = time.time()
        if current_time - self.last_print_time > self.print_interval:
            print(f"[DEBUG] Nas:({state['nose_x']:.2f}, {state['nose_y']:.2f}) | "
                  f"Viteza:({vx:5.1f}, {vy:5.1f}) | "
                  f"Ochi:(S:{state['left_eye_ratio']:.2f}, D:{state['right_eye_ratio']:.2f}) | "
                  f"Gura:{state['mouth_ratio']:.2f}")
            self.last_print_time = current_time