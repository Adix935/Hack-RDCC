# main.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'

import cv2
import math
import mediapipe as mp
import winsound
import threading

# Importăm modulele create de voi
import pyautogui
from mouse_engine import MouseController
from gesture_logic import GestureProcessor
from debug import DebugMonitor
from overlay import JoystickOverlay

mp_face_mesh = mp.solutions.face_mesh

current_state = {
    "nose_x": 0.0, "nose_y": 0.0, 
    "left_eye_ratio": 0.3, "right_eye_ratio": 0.3, "mouth_ratio": 0.1,
}

# JoyStick Settings
CENTER_X, CENTER_Y = 0.5, 0.5
DEADZONE = 0.04   
MAX_SPEED = 100
MIN_SPEED = 3.0

# Inițializăm modulele voastre
screen_w, screen_h = pyautogui.size()
mouse = MouseController(screen_w, screen_h)
logic = GestureProcessor() 
debugger = DebugMonitor(print_interval=0.3)
hud_overlay = JoystickOverlay(size=160, deadzone_ratio=DEADZONE, max_reach=0.15)

# Multiplicator pentru scroll (ajustează dacă e prea rapid/lent)
SCROLL_MULTIPLIER = 3

is_calibrated = False
calibration_frames = []
CALIBRATION_FRAME_COUNT = 45  

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, refine_landmarks=True,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

def euclidean_distance(p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

NOSE_TIP = 1
EYE_TOP, EYE_BOTTOM = 159, 145
EYE_LEFT, EYE_RIGHT = 33, 133
RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM = 386, 374
RIGHT_EYE_LEFT, RIGHT_EYE_RIGHT = 362, 263
MOUTH_TOP, MOUTH_BOTTOM = 13, 14
MOUTH_LEFT, MOUTH_RIGHT = 78, 308

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("=== MotionClick - Produs Final ===")
print("Comenzi tastatura:")
print("  'c' = Recalibrare pozitie neutra")
print("  'q' = Oprire normala")
print("  SPACE = Kill-Switch (oprire de urgenta)")
print("Comenzi faciale:")
print("  Misca capul = Misca cursorul")
print("  Wink stang scurt = Click stanga")
print("  Wink stang lung (>1s) = Drag & Drop")
print("  Wink drept scurt = Click dreapta")
print("  Ambii ochi 1-3s = Dublu Click")
print("  Ambii ochi >3s = Sleep/Wake")
print("  Gura deschisa + miscare cap = Scroll")
print("=" * 40)

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success: 
            break

        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Nose Coordinates
                nose = face_landmarks.landmark[NOSE_TIP]
                current_state["nose_x"] = nose.x
                current_state["nose_y"] = nose.y

                if not is_calibrated:
                    calibration_frames.append((nose.x, nose.y))
                    cv2.putText(image, f"Calibrare pozitie neutra... {len(calibration_frames)}/{CALIBRATION_FRAME_COUNT}",
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    if len(calibration_frames) >= CALIBRATION_FRAME_COUNT:
                        CENTER_X = sum(f[0] for f in calibration_frames) / len(calibration_frames)
                        CENTER_Y = sum(f[1] for f in calibration_frames) / len(calibration_frames)
                        is_calibrated = True
                        print(f">> Calibrare finalizata! Nou Centru: ({CENTER_X:.3f}, {CENTER_Y:.3f}) <<")
                    break 
                
                # Ratios
                l_eye_v = euclidean_distance(face_landmarks.landmark[EYE_TOP], face_landmarks.landmark[EYE_BOTTOM])
                l_eye_h = euclidean_distance(face_landmarks.landmark[EYE_LEFT], face_landmarks.landmark[EYE_RIGHT])
                if l_eye_h > 0: current_state["left_eye_ratio"] = l_eye_v / l_eye_h
                    
                r_eye_v = euclidean_distance(face_landmarks.landmark[RIGHT_EYE_TOP], face_landmarks.landmark[RIGHT_EYE_BOTTOM])
                r_eye_h = euclidean_distance(face_landmarks.landmark[RIGHT_EYE_LEFT], face_landmarks.landmark[RIGHT_EYE_RIGHT])
                if r_eye_h > 0: current_state["right_eye_ratio"] = r_eye_v / r_eye_h
                    
                mouth_v_dist = euclidean_distance(face_landmarks.landmark[MOUTH_TOP], face_landmarks.landmark[MOUTH_BOTTOM])
                mouth_h_dist = euclidean_distance(face_landmarks.landmark[MOUTH_LEFT], face_landmarks.landmark[MOUTH_RIGHT])
                if mouth_h_dist > 0: current_state["mouth_ratio"] = mouth_v_dist / mouth_h_dist

                face_width = euclidean_distance(face_landmarks.landmark[33], face_landmarks.landmark[263])
                
                if face_width > 0:
                    mouth_width_ratio = mouth_h_dist / face_width
                    
                    # Dacă buzele sunt țuguiate, lățimea gurii scade sub 33% din lățimea feței
                    if mouth_width_ratio < 0.33:
                        CENTER_X = current_state["nose_x"]
                        CENTER_Y = current_state["nose_y"]

                # JoyStick
                dx = current_state["nose_x"] - CENTER_X
                dy = current_state["nose_y"] - CENTER_Y

                mouse_velocity_x = 0.0
                mouse_velocity_y = 0.0

                if abs(dx) > DEADZONE:
                    active_dx = dx - (DEADZONE if dx > 0 else -DEADZONE)
                    sign_x = 1 if dx > 0 else -1
                    # Pleacă direct cu MIN_SPEED, apoi accelerează
                    mouse_velocity_x = sign_x * (abs(active_dx) * MAX_SPEED + MIN_SPEED)

                if abs(dy) > DEADZONE:
                    active_dy = dy - (DEADZONE if dy > 0 else -DEADZONE)
                    sign_y = 1 if dy > 0 else -1
                    mouse_velocity_y = sign_y * (abs(active_dy) * MAX_SPEED + MIN_SPEED)

                # ==========================================================
                # INTEGRAREA ACTUATORULUI ȘI A LOGICII
                # ==========================================================
                if is_calibrated:
                    # 1. Trimitem datele către Creier
                    comenzi = logic.process(
                        current_state["left_eye_ratio"], 
                        current_state["right_eye_ratio"], 
                        current_state["mouth_ratio"], 
                        mouse_velocity_x, 
                        mouse_velocity_y
                    )
                    
                    # 2. Executăm comenzile fizice pe Windows
                    if comenzi["move"] != (0.0, 0.0):
                        mouse.move_cursor(comenzi["move"][0], comenzi["move"][1])
                        
                    if comenzi["scroll"] != (0.0, 0.0):
                        mouse.scroll(
                            comenzi["scroll"][1] * SCROLL_MULTIPLIER, 
                            comenzi["scroll"][0] * SCROLL_MULTIPLIER 
                        )
                        
                    if comenzi["left_click"]: mouse.left_click()
                    if comenzi["right_click"]: mouse.right_click()
                    if comenzi["double_click"]: mouse.double_click()
                    if comenzi["toggle_drag"]: 
                        mouse.toggle_drag()
                        # Fără threading, pauza va fi de doar 200ms (insesizabil la o acțiune intenționată)
                        if logic.is_dragging:
                            winsound.Beep(500, 200) # Ton mai ascuțit când prinzi fișierul
                        else:
                            winsound.Beep(350, 200) # Ton mai grav când îl lași
                    if comenzi["toggle_sleep"]: mouse.toggle_sleep()

                    # 3. Kill-Switch pe tasta Space
                    if mouse.check_failsafe():
                        raise KeyboardInterrupt
                # ==========================================================

                # Grafica lui Persoana 1
                center_px = (int(CENTER_X * w), int(CENTER_Y * h))
                nose_px = (int(current_state["nose_x"] * w), int(current_state["nose_y"] * h))
                deadzone_radius_px = int(DEADZONE * w)

                cv2.circle(image, center_px, deadzone_radius_px, (255, 120, 0), 2)
                cv2.circle(image, center_px, 3, (0, 0, 255), -1)

                in_deadzone = (abs(dx) <= DEADZONE and abs(dy) <= DEADZONE)
                nose_color = (0, 255, 0) if in_deadzone else (0, 0, 255)
                cv2.circle(image, nose_px, 5, nose_color, -1)
                hud_overlay.update(dx, dy, in_deadzone)
  
                if not in_deadzone:
                    cv2.line(image, center_px, nose_px, (0, 165, 255), 2)

                # HUD - Status pe ecran
                if logic.is_sleeping:
                    cv2.putText(image, "SLEEP MODE (ambii ochi >3s pt wake)", 
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                elif logic.is_dragging:
                    cv2.putText(image, "DRAG MODE (wink stang scurt pt drop)", 
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                else:
                    cv2.putText(image, "ACTIV", 
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                debugger.draw_hud(image, current_state, mouse_velocity_x, mouse_velocity_y)
                debugger.print_terminal(current_state, mouse_velocity_x, mouse_velocity_y)

        cv2.imshow('MotionClick - Produs Final', image)
        key = cv2.waitKey(5) & 0xFF

        if key == ord('c'):
            CENTER_X = current_state["nose_x"]
            CENTER_Y = current_state["nose_y"]
            print(f">> Recalibrare manuala reusita: Centru nou ({CENTER_X:.3f}, {CENTER_Y:.3f}) <<")

        if key == ord('q'):
            break

except KeyboardInterrupt:
    print("\nProgram oprit de utilizator.")
except Exception as e:
    print(f"\n[EROARE] Programul s-a oprit: {e}")
    import traceback
    traceback.print_exc()
finally:
    cap.release()
    cv2.destroyAllWindows()
    hud_overlay.close()
    print("Camera eliberata. La revedere!")
