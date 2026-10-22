import tkinter as tk
import json
import os
import threading
import time
import pyautogui
import keyboard

CONFIG_FILE = "config.json"
pyautogui.FAILSAFE = True

# ==========================================
# 1. MOTORUL DE GESTURI (Test Logic)
# ==========================================
class GestureProcessor:
    def __init__(self):
        self.eyes_closed_frames = 0
        self.min_frames_for_click = 4
        self.max_frames_for_click = 12

    def process_data(self, eye_ratio, mouth_ratio, config):
        """Preia datele și setările la fiecare cadru."""
        # Citim pragurile direct din dicționarul de config trimis de UI
        blink_threshold = config.get("blink_threshold", 0.20)
        mouth_threshold = config.get("mouth_threshold", 0.05)

        # --- LOGICA DE CLICK ---
        if eye_ratio < blink_threshold:
            self.eyes_closed_frames += 1
        else:
            if self.eyes_closed_frames > 0:
                if self.min_frames_for_click <= self.eyes_closed_frames <= self.max_frames_for_click:
                    print(f" CLICK STÂNGA! (Prag activ: {blink_threshold})")
                    pyautogui.click()
                elif self.eyes_closed_frames > self.max_frames_for_click:
                    print(" DOUBLE CLICK!")
                    pyautogui.doubleClick()
                self.eyes_closed_frames = 0

        # --- LOGICA DE SCROLL ---
        if mouth_ratio > mouth_threshold:
            print("⬇ SCROLL JOS...")
            pyautogui.scroll(-40)

# ==========================================
# 2. PANOUR DE CONTROL (UI) ȘI THREAD-UL
# ==========================================
class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MotionClick - Asistent AI")
        self.root.geometry("400x350")
        self.root.configure(padx=20, pady=20)

        self.config = self.load_config()
        self.is_running = False
        self.processor = GestureProcessor()

        # UI Elements
        tk.Label(root, text="Setări Accesibilitate", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        tk.Label(root, text="Sensibilitate Mouse (Viteza):").pack(anchor="w")
        self.sens_slider = tk.Scale(root, from_=1, to=10, orient="horizontal", command=self.save_config)
        self.sens_slider.set(self.config.get("mouse_sensitivity", 5))
        self.sens_slider.pack(fill="x")

        tk.Label(root, text="Prag Clipire (Ochi):").pack(anchor="w")
        self.blink_slider = tk.Scale(root, from_=0.10, to=0.40, resolution=0.01, orient="horizontal", command=self.save_config)
        self.blink_slider.set(self.config.get("blink_threshold", 0.20))
        self.blink_slider.pack(fill="x")

        tk.Label(root, text="Prag Gură (Scroll):").pack(anchor="w")
        self.mouth_slider = tk.Scale(root, from_=0.01, to=0.20, resolution=0.01, orient="horizontal", command=self.save_config)
        self.mouth_slider.set(self.config.get("mouth_threshold", 0.05))
        self.mouth_slider.pack(fill="x", pady=(0, 20))

        self.start_btn = tk.Button(root, text="▶ PORNEȘTE ASISTENTUL", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.toggle_app)
        self.start_btn.pack(fill="x", ipady=10)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"blink_threshold": 0.20, "mouth_threshold": 0.05, "mouse_sensitivity": 5}

    def save_config(self, event=None):
        self.config = {
            "mouse_sensitivity": self.sens_slider.get(),
            "blink_threshold": self.blink_slider.get(),
            "mouth_threshold": self.mouth_slider.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def toggle_app(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.config(text="⏹ OPREȘTE ASISTENTUL", bg="#f44336")
            print(" Asistent pornit!")
            
            # Pornim "motorul" pe un fir de execuție separat (Thread)
            # Ca să nu blocheze interfața vizuală.
            threading.Thread(target=self.run_background_loop, daemon=True).start()
        else:
            self.start_btn.config(text="▶ PORNEȘTE ASISTENTUL", bg="#4CAF50")
            print(" Asistent oprit!")

    def run_background_loop(self):
        """Aceasta este bucla care simulează camera web."""
        while self.is_running:
            current_state = {"eye_ratio": 0.28, "mouth_ratio": 0.01}
            
            if keyboard.is_pressed('c'):
                current_state["eye_ratio"] = 0.10
            if keyboard.is_pressed('v'):
                current_state["mouth_ratio"] = 0.15
            
            # Trimitem datele și config-ul ACTUALIZAT către logica de gesturi
            self.processor.process_data(current_state["eye_ratio"], current_state["mouth_ratio"], self.config)
            time.sleep(1 / 30)

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlPanel(root)
    root.mainloop()