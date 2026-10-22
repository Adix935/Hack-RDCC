import tkinter as tk
from tkinter import ttk
import json
import os

CONFIG_FILE = "config.json"

class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MotionClick - Control Panel")
        self.root.geometry("400x350")
        self.root.configure(padx=20, pady=20)

        # Încărcăm setările vechi (dacă există) sau punem valori default
        self.config = self.load_config()

        # Titlu
        tk.Label(root, text="Setări Accesibilitate", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        # --- SLIDER 1: Sensibilitate Mouse (Pentru Colegul 2) ---
        tk.Label(root, text="Sensibilitate Mouse (Viteza):", font=("Arial", 10)).pack(anchor="w")
        self.sens_slider = tk.Scale(root, from_=1, to=10, orient="horizontal", command=self.save_config)
        self.sens_slider.set(self.config.get("mouse_sensitivity", 5))
        self.sens_slider.pack(fill="x", pady=(0, 15))

        # --- SLIDER 2: Prag Clipire (Pentru Tine) ---
        tk.Label(root, text="Cât de tare închizi ochii pt CLICK (Prag):", font=("Arial", 10)).pack(anchor="w")
        self.blink_slider = tk.Scale(root, from_=0.10, to=0.40, resolution=0.01, orient="horizontal", command=self.save_config)
        self.blink_slider.set(self.config.get("blink_threshold", 0.20))
        self.blink_slider.pack(fill="x", pady=(0, 15))

        # --- SLIDER 3: Prag Gură (Pentru Tine) ---
        tk.Label(root, text="Cât deschizi gura pt SCROLL (Prag):", font=("Arial", 10)).pack(anchor="w")
        self.mouth_slider = tk.Scale(root, from_=0.01, to=0.20, resolution=0.01, orient="horizontal", command=self.save_config)
        self.mouth_slider.set(self.config.get("mouth_threshold", 0.05))
        self.mouth_slider.pack(fill="x", pady=(0, 20))

        # --- BUTON START / STOP ---
        self.is_running = False
        self.start_btn = tk.Button(root, text="▶ PORNEȘTE ASISTENTUL", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.toggle_app)
        self.start_btn.pack(fill="x", ipady=10)

    def load_config(self):
        """Citește setările salvate anterior."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {} # Dacă nu există fișierul, returnează gol

    def save_config(self, event=None):
        """Salvează valorile din slidere direct în fișierul JSON."""
        self.config = {
            "mouse_sensitivity": self.sens_slider.get(),
            "blink_threshold": self.blink_slider.get(),
            "mouth_threshold": self.mouth_slider.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        
        # Printează în consolă ca să vezi că funcționează
        print(f"Setări salvate: {self.config}")

    def toggle_app(self):
        """Logica pentru butonul de Start/Stop"""
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.config(text="⏹ OPREȘTE ASISTENTUL", bg="#f44336")
            print("ASISTENTUL A PORNIT (Aici vom lega codul tău de gesturi și cel al colegilor!)")
        else:
            self.start_btn.config(text="▶ PORNEȘTE ASISTENTUL", bg="#4CAF50")
            print("ASISTENTUL S-A OPRIT")

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlPanel(root)
    root.mainloop()