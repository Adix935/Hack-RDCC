import customtkinter as ctk
import json
import os
import threading
import time
import pyautogui
import keyboard
import winsound

CONFIG_FILE = "config.json"
pyautogui.FAILSAFE = True

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 1. MOTORUL DE GESTURI (Creierul Avansat)
# ==========================================
class GestureProcessor:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        
        # Contoare separate pentru ochi
        self.left_frames = 0
        self.right_frames = 0
        self.both_frames = 0
        
        # Praguri de cadre (la ~30 FPS)
        self.min_frames_for_click = 4      # Minim ca să nu fie un tic nervos
        self.frames_1_sec = 30             # 1 secundă (pt Dublu Click sau Drag&Drop)
        self.frames_3_sec = 90             # 3 secunde (pt Sleep Mode)
        
        # Stări speciale
        self.is_asleep = False
        self.is_dragging = False

    def process_data(self, left_eye, right_eye, mouth_ratio, config):
        blink_threshold = config.get("blink_threshold", 0.20)
        mouth_threshold = config.get("mouth_threshold", 0.05)

        left_closed = left_eye < blink_threshold
        right_closed = right_eye < blink_threshold
        mouth_open = mouth_ratio > mouth_threshold

        # --- 1. NUMĂRĂTOAREA (Calculăm ce e închis) ---
        if left_closed and right_closed:
            self.both_frames += 1
        elif left_closed and not right_closed:
            self.left_frames += 1
        elif right_closed and not left_closed:
            self.right_frames += 1

        # --- 2. DECIZIA (Când utilizatorul deschide ochii complet) ---
        if not left_closed and not right_closed:
            
            # A) A ținut AMBII ochi închiși
            if self.both_frames > 0:
                frames = self.both_frames
                print(f"[DEBUG] Ambii ochi închiși: {frames} cadre")
                
                # Regula: Peste 3 secunde -> SLEEP MODE
                if frames >= self.frames_3_sec:
                    self.is_asleep = not self.is_asleep
                    if self.is_asleep:
                        print(" APLICAȚIA A INTRAT ÎN SLEEP MODE")
                        self.ui_callback(" MOD SLEEP (Pauză)", "yellow")
                        winsound.Beep(1000, 300)
                    else:
                        print(" APLICAȚIA S-A TREZIT")
                        self.ui_callback(" MOD ACTIV", "#2FA572")
                        winsound.Beep(2000, 150)
                        winsound.Beep(2500, 150)
                        
                # Regula: Peste 1 sec (dar sub 3) -> DUBLU CLICK
                elif not self.is_asleep and frames >= self.frames_1_sec:
                    print(" DUBLU CLICK!")
                    pyautogui.doubleClick()
                
                # Resetăm tot
                self.both_frames = 0
                self.left_frames = 0
                self.right_frames = 0

            # B) A ținut doar OCHIUL STÂNG (Wink Stâng)
            elif self.left_frames > 0 and not self.is_asleep:
                frames = self.left_frames
                print(f"[DEBUG] Ochi stâng închis: {frames} cadre")
                
                if self.is_dragging:
                    # Dacă trăgea deja de un fișier, un wink scurt DEBLOCAT
                    if self.min_frames_for_click <= frames < self.frames_1_sec:
                        print(" DRAG & DROP: Eliberare fișier!")
                        pyautogui.mouseUp(button='left')
                        self.is_dragging = False
                        self.ui_callback(" MOD ACTIV", "#2FA572")
                        winsound.Beep(1500, 200) # Sunet de eliberare
                else:
                    # Regula: Wink lung (>1 sec) -> ÎNCEPE DRAG & DROP
                    if frames >= self.frames_1_sec:
                        print(" DRAG & DROP: Prindere fișier!")
                        pyautogui.mouseDown(button='left')
                        self.is_dragging = True
                        self.ui_callback(" ACTIV (TRAGE FIȘIERUL)", "#FFA500") # Portocaliu în UI
                        winsound.Beep(2500, 200) # Sunet de prindere
                        
                    # Regula: Wink scurt -> CLICK STÂNGA
                    elif self.min_frames_for_click <= frames < self.frames_1_sec:
                        print(" CLICK STÂNGA!")
                        pyautogui.click(button='left')

                self.left_frames = 0

            # C) A ținut doar OCHIUL DREPT (Wink Drept)
            elif self.right_frames > 0 and not self.is_asleep:
                frames = self.right_frames
                print(f"[DEBUG] Ochi drept închis: {frames} cadre")
                
                # Regula: Wink scurt drept -> CLICK DREAPTA
                if self.min_frames_for_click <= frames < self.frames_1_sec:
                    print(" CLICK DREAPTA!")
                    pyautogui.click(button='right')
                
                self.right_frames = 0

        # --- 3. SCROLL-UL (Gura deschisă) ---
        if not self.is_asleep and mouth_open:
            print("↕ SCROLL ACTIV! (Aici nasul va dicta direcția Sus/Jos)")
            # Îl simulăm pentru test. La final, Persoana 2 va face scroll
            # în funcție de y-ul nasului când aude că `mouth_open == True`
            pyautogui.scroll(-20) 


# ==========================================
# 2. PANOU DE CONTROL MODERN & THREADING
# ==========================================
class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MotionClick - AI Assistant")
        self.root.geometry("450x520")
        
        self.config = self.load_config()
        self.is_running = False
        
        self.processor = GestureProcessor(ui_callback=self.update_status_label)

        self.title_label = ctk.CTkLabel(root, text="Setări Accesibilitate", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=(20, 20))

        self.status_label = ctk.CTkLabel(root, text="⚫ OPRIT", text_color="gray", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.pack(pady=(0, 20))

        self.lbl_sens = ctk.CTkLabel(root, text=f"Sensibilitate Mouse: {self.config.get('mouse_sensitivity', 5)}")
        self.lbl_sens.pack(anchor="w", padx=30)
        self.sens_slider = ctk.CTkSlider(root, from_=1, to=10, number_of_steps=9, command=self.update_sens_label)
        self.sens_slider.set(self.config.get("mouse_sensitivity", 5))
        self.sens_slider.pack(fill="x", padx=30, pady=(0, 20))

        self.lbl_blink = ctk.CTkLabel(root, text=f"Sensibilitate Clipire (Prag): {self.config.get('blink_threshold', 0.20):.2f}")
        self.lbl_blink.pack(anchor="w", padx=30)
        self.blink_slider = ctk.CTkSlider(root, from_=0.10, to=0.40, number_of_steps=30, command=self.update_blink_label)
        self.blink_slider.set(self.config.get("blink_threshold", 0.20))
        self.blink_slider.pack(fill="x", padx=30, pady=(0, 20))

        self.lbl_mouth = ctk.CTkLabel(root, text=f"Sensibilitate Gură (Prag): {self.config.get('mouth_threshold', 0.05):.2f}")
        self.lbl_mouth.pack(anchor="w", padx=30)
        self.mouth_slider = ctk.CTkSlider(root, from_=0.01, to=0.20, number_of_steps=19, command=self.update_mouth_label)
        self.mouth_slider.set(self.config.get("mouth_threshold", 0.05))
        self.mouth_slider.pack(fill="x", padx=30, pady=(0, 30))

        self.start_btn = ctk.CTkButton(root, text=" PORNEȘTE ASISTENTUL", fg_color="#2FA572", hover_color="#107C41", 
                                       font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.toggle_app)
        self.start_btn.pack(fill="x", padx=30)
        
        self.info_label = ctk.CTkLabel(root, text="*Aplicația este setată să pornească cu Windows", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray")
        self.info_label.pack(pady=10)

    def update_sens_label(self, value):
        self.lbl_sens.configure(text=f"Sensibilitate Mouse: {int(value)}")
        self.save_config()
    def update_blink_label(self, value):
        self.lbl_blink.configure(text=f"Sensibilitate Clipire: {value:.2f}")
        self.save_config()
    def update_mouth_label(self, value):
        self.lbl_mouth.configure(text=f"Sensibilitate Gură: {value:.2f}")
        self.save_config()

    def update_status_label(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"blink_threshold": 0.20, "mouth_threshold": 0.05, "mouse_sensitivity": 5}

    def save_config(self, *args):
        self.config = {
            "mouse_sensitivity": int(self.sens_slider.get()),
            "blink_threshold": round(self.blink_slider.get(), 2),
            "mouth_threshold": round(self.mouth_slider.get(), 2)
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def toggle_app(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.configure(text="⏹ OPREȘTE ASISTENTUL", fg_color="#E81123", hover_color="#B50E1B")
            self.update_status_label(" MOD ACTIV", "#2FA572")
            threading.Thread(target=self.run_background_loop, daemon=True).start()
        else:
            self.start_btn.configure(text="▶ PORNEȘTE ASISTENTUL", fg_color="#2FA572", hover_color="#107C41")
            self.update_status_label(" OPRIT", "gray")

    def run_background_loop(self):
        while self.is_running:
            # Structura de date nouă trimisă de Persoana 1
            current_state = {
                "left_eye": 0.28, 
                "right_eye": 0.28, 
                "mouth_ratio": 0.01
            }
            
            # Simulator de gesturi cu taste:
            if keyboard.is_pressed('a'):  # Wink STÂNGA
                current_state["left_eye"] = 0.10
            if keyboard.is_pressed('d'):  # Wink DREAPTA
                current_state["right_eye"] = 0.10
            if keyboard.is_pressed('s'):  # Ambii ochi închiși
                current_state["left_eye"] = 0.10
                current_state["right_eye"] = 0.10
            if keyboard.is_pressed('v'):  # Gură deschisă
                current_state["mouth_ratio"] = 0.15
            
            # Trimitem pachetul la procesor
            self.processor.process_data(
                current_state["left_eye"], 
                current_state["right_eye"], 
                current_state["mouth_ratio"], 
                self.config
            )
            time.sleep(1 / 30)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ControlPanel(root)
    root.mainloop()