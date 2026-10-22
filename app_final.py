import customtkinter as ctk
import cv2
import mediapipe as mp
import math
import json
import os
import threading
import pyautogui
import winsound
import time

# Importăm motorul de mouse de la Persoana 2
from mouse_engine import MouseController

mp_face_mesh = mp.solutions.face_mesh

CONFIG_FILE = "config.json"
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 1. MOTORUL DE GESTURI (Real-Time Audio Feedback)
# ==========================================
class GestureProcessor:
    def __init__(self, ui_callback, mouse_controller):
        self.ui_callback = ui_callback
        self.mouse = mouse_controller 
        
        self.left_start = None
        self.right_start = None
        self.both_start = None
        
        # Timpii tăi optimizați:
        self.min_click_time = 0.1  # 100ms pt click normal
        self.time_drag = 0.7       # 0.7s pt Dublu Click / Drag & Drop
        self.time_sleep = 2.5      # 2.5s pt Sleep Mode
        
        self.is_asleep = False
        self.is_dragging = False
        
        # FLAG MAGIC: Ne asigură că acțiunea se execută o singură dată per clipire
        self.action_done = False

    def process_data(self, left_eye, right_eye, mouth_ratio, vel_x, vel_y, config):
        blink_threshold = config.get("blink_threshold", 0.20)
        mouth_threshold = config.get("mouth_threshold", 0.05)

        left_closed = left_eye < blink_threshold
        right_closed = right_eye < blink_threshold
        mouth_open = mouth_ratio > mouth_threshold
        
        current_time = time.time()

        # --- 1. AMBII OCHI ÎNCHIȘI (Sleep / Wake) ---
        if left_closed and right_closed:
            if self.both_start is None: 
                self.both_start = current_time
                self.action_done = False  # Resetăm starea la închidere
            self.left_start, self.right_start = None, None
            
            # Verificăm LIVE timpul
            duration = current_time - self.both_start
            if duration >= self.time_sleep and not self.action_done:
                self.is_asleep = not self.is_asleep
                if self.is_asleep:
                    self.ui_callback("🌙 MOD SLEEP (Pauză)", "yellow")
                    self.mouse.toggle_sleep()
                    winsound.Beep(1000, 300) # Auzi asta în timp ce ții ochii închiși!
                else:
                    self.ui_callback("☀️ MOD ACTIV", "#2FA572")
                    self.mouse.toggle_sleep()
                    winsound.Beep(2000, 150)
                    winsound.Beep(2500, 150)
                self.action_done = True # Împiedică repetarea sunetului

        # --- 2. DOAR OCHIUL STÂNG (Drag & Drop) ---
        elif left_closed and not right_closed:
            if self.left_start is None: 
                self.left_start = current_time
                self.action_done = False
            self.both_start, self.right_start = None, None
            
            # Verificăm LIVE timpul pentru Drag
            duration = current_time - self.left_start
            if duration >= self.time_drag and not self.action_done and not self.is_asleep:
                if self.is_dragging:
                    self.mouse.toggle_drag() # Drop
                    self.is_dragging = False
                    self.ui_callback("☀️ MOD ACTIV", "#2FA572")
                    winsound.Beep(1500, 200)
                else:
                    self.mouse.toggle_drag() # Drag
                    self.is_dragging = True
                    self.ui_callback("✊ ACTIV (TRAGE FIȘIERUL)", "#FFA500")
                    winsound.Beep(2500, 200)
                self.action_done = True

        # --- 3. DOAR OCHIUL DREPT (Click Dreapta - doar numără) ---
        elif right_closed and not left_closed:
            if self.right_start is None: 
                self.right_start = current_time
                self.action_done = False
            self.both_start, self.left_start = None, None

        # --- 4. LA DESCHIDEREA OCHILOR (Acțiuni scurte de click) ---
        elif not left_closed and not right_closed:
            
            # Dublu Click (ambii ochi)
            if self.both_start is not None:
                duration = current_time - self.both_start
                # Face dublu click doar dacă ai ținut destul (0.7s) dar n-ai atins sleep-ul (2.5s)
                if not self.is_asleep and not self.action_done and duration >= self.time_drag:
                    self.mouse.double_click()
                self.both_start = None

            # Click Simplu (ochi stâng)
            elif self.left_start is not None:
                duration = current_time - self.left_start
                # Dacă am deschis ochiul repede și nu se activase deja Drag-ul
                if not self.is_asleep and not self.action_done and duration >= self.min_click_time:
                    self.mouse.left_click()
                self.left_start = None

            # Click Dreapta (ochi drept)
            elif self.right_start is not None:
                duration = current_time - self.right_start
                if not self.is_asleep and not self.action_done and duration >= self.min_click_time:
                    self.mouse.right_click()
                self.right_start = None
                
            self.action_done = False # Resetăm complet

        # --- 5. CURSOR & SCROLL ---
        if not self.is_asleep:
            if mouth_open:
                SCROLL_SPEED = 3
                self.mouse.scroll(vel_y * SCROLL_SPEED, vel_x * SCROLL_SPEED)
            else:
                sens = config.get("mouse_sensitivity", 5) / 5.0
                self.mouse.move_cursor(vel_x * sens, vel_y * sens)

# ==========================================
# 2. UI & MEDIA PIPE THREAD
# ==========================================
def euclidean_distance(p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

class ControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("MotionClick - Produs Final")
        self.root.geometry("450x520")
        
        self.config = self.load_config()
        self.is_running = False
        
        screen_w, screen_h = pyautogui.size()
        self.mouse_ctrl = MouseController(screen_w, screen_h)
        self.processor = GestureProcessor(ui_callback=self.update_status_label, mouse_controller=self.mouse_ctrl)

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

        self.start_btn = ctk.CTkButton(root, text="▶ PORNEȘTE ASISTENTUL", fg_color="#2FA572", hover_color="#107C41", 
                                       font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.toggle_app)
        self.start_btn.pack(fill="x", padx=30)
        
        self.info_label = ctk.CTkLabel(root, text="*Aplicația este setată să pornească cu Windows", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray")
        self.info_label.pack(pady=10)

    # ... [Funcțiile de salvare config rămân identice] ...
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
        self.config = {"mouse_sensitivity": int(self.sens_slider.get()), "blink_threshold": round(self.blink_slider.get(), 2), "mouth_threshold": round(self.mouth_slider.get(), 2)}
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f, indent=4)

    def toggle_app(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start_btn.configure(text="⏹ OPREȘTE ASISTENTUL", fg_color="#E81123", hover_color="#B50E1B")
            self.update_status_label("☀️ MOD ACTIV", "#2FA572")
            threading.Thread(target=self.run_camera_loop, daemon=True).start()
        else:
            self.start_btn.configure(text="▶ PORNEȘTE ASISTENTUL", fg_color="#2FA572", hover_color="#107C41")
            self.update_status_label("⚫ OPRIT", "gray")

    def run_camera_loop(self):
        """Aici am integrat codul MediaPipe de la P1 și P2"""
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        CENTER_X, CENTER_Y = 0.5, 0.5
        DEADZONE = 0.04   
        MAX_SPEED = 250
        is_calibrated = False
        calibration_frames = []

        while self.is_running and cap.isOpened():
            success, image = cap.read()
            if not success: break

            image = cv2.flip(image, 1)
            h, w, _ = image.shape
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_image)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    nose = face_landmarks.landmark[1]
                    
                    if not is_calibrated:
                        calibration_frames.append((nose.x, nose.y))
                        cv2.putText(image, f"Calibrare: Tine capul drept... {len(calibration_frames)}/45", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        if len(calibration_frames) >= 45:
                            CENTER_X = sum(f[0] for f in calibration_frames) / 45
                            CENTER_Y = sum(f[1] for f in calibration_frames) / 45
                            is_calibrated = True
                        break 
                    
                    # Ratios (Ochi & Gură)
                    l_eye_v = euclidean_distance(face_landmarks.landmark[159], face_landmarks.landmark[145])
                    l_eye_h = euclidean_distance(face_landmarks.landmark[33], face_landmarks.landmark[133])
                    left_ratio = l_eye_v / l_eye_h if l_eye_h > 0 else 0.3
                    
                    r_eye_v = euclidean_distance(face_landmarks.landmark[386], face_landmarks.landmark[374])
                    r_eye_h = euclidean_distance(face_landmarks.landmark[362], face_landmarks.landmark[263])
                    right_ratio = r_eye_v / r_eye_h if r_eye_h > 0 else 0.3
                    
                    mouth_v = euclidean_distance(face_landmarks.landmark[13], face_landmarks.landmark[14])
                    mouth_h = euclidean_distance(face_landmarks.landmark[78], face_landmarks.landmark[308])
                    mouth_ratio = mouth_v / mouth_h if mouth_h > 0 else 0.1

                    # JoyStick Velocity
                    dx = nose.x - CENTER_X
                    dy = nose.y - CENTER_Y
                    vel_x, vel_y = 0.0, 0.0

                    if abs(dx) > DEADZONE: vel_x = (dx - (DEADZONE if dx > 0 else -DEADZONE)) * MAX_SPEED
                    if abs(dy) > DEADZONE: vel_y = (dy - (DEADZONE if dy > 0 else -DEADZONE)) * MAX_SPEED

                    # Procesare și trimitere comenzi
                    self.processor.process_data(left_ratio, right_ratio, mouth_ratio, vel_x, vel_y, self.config)

                    # Grafica de debug pe cameră
                    center_px = (int(CENTER_X * w), int(CENTER_Y * h))
                    nose_px = (int(nose.x * w), int(nose.y * h))
                    cv2.circle(image, center_px, int(DEADZONE * w), (255, 120, 0), 2)
                    cv2.circle(image, nose_px, 5, (0, 0, 255), -1)
                    if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                        cv2.line(image, center_px, nose_px, (0, 165, 255), 2)

            cv2.imshow('MotionClick - Camera', image)
            
            # Recalibrare manuală din fereastra camerei
            if cv2.waitKey(5) & 0xFF == ord('c') and results.multi_face_landmarks:
                CENTER_X, CENTER_Y = nose.x, nose.y

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = ctk.CTk()
    app = ControlPanel(root)
    root.mainloop()