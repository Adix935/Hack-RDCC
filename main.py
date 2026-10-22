# main.py
import cv2
import time
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh


from shared_state import config
from math_utils import calculate_ratio, calculate_velocity
from mouse_engine import MouseController

# Indexuri MediaPipe
NOSE_TIP = 1

# Ochi Stâng (perspectiva utilizatorului după flip)
EYE_L_TOP, EYE_L_BOT = 159, 145
EYE_L_LEFT, EYE_L_RIGHT = 33, 133

# Ochi Drept (perspectiva utilizatorului după flip)
EYE_R_TOP, EYE_R_BOT = 386, 374
EYE_R_LEFT, EYE_R_RIGHT = 362, 263

# Gură
MOUTH_TOP, MOUTH_BOT = 13, 14
MOUTH_LEFT, MOUTH_RIGHT = 78, 308

def main():
    # 1. Inițializări
    mouse = MouseController(config["screen_width"], config["screen_height"])
    
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, 
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(0)

    # 2. Variabile pentru cronometrarea gesturilor
    l_closed_start = 0.0
    r_closed_start = 0.0
    both_closed_start = 0.0
    
    l_was_closed = False
    r_was_closed = False
    both_was_closed = False

    print("\n[SISTEM] Vision Engine Avansat pornit!")
    print("[COMENZI ACTIVE]:")
    print(" - Wink Stâng scurt (<1s): Click Stânga")
    print(" - Wink Stâng lung (>1s): Start Drag (alt wink scurt pt Drop)")
    print(" - Wink Drept scurt (<1s): Click Dreapta")
    print(" - Ambii ochi închiși (1s - 3s): Dublu Click")
    print(" - Ambii ochi închiși (>3s): Sleep Mode (Pauză)")
    print(" - Gură deschisă + mișcare cap: Scroll")
    print("Apasă ESC pe tastatură pentru a ieși de urgență.\n")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Imagine în oglindă pentru un control intuitiv
        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # --- CALCUL RAPOARTE ANATOMICE ---
            ratio_l = calculate_ratio(landmarks, EYE_L_TOP, EYE_L_BOT, EYE_L_LEFT, EYE_L_RIGHT)
            ratio_r = calculate_ratio(landmarks, EYE_R_TOP, EYE_R_BOT, EYE_R_LEFT, EYE_R_RIGHT)
            ratio_m = calculate_ratio(landmarks, MOUTH_TOP, MOUTH_BOT, MOUTH_LEFT, MOUTH_RIGHT)

            # Stări curente pe baza threshold-urilor din config
            l_is_closed = ratio_l < config["eye_closed_threshold"]
            r_is_closed = ratio_r < config["eye_closed_threshold"]
            mouth_is_open = ratio_m > config["mouth_open_threshold"]
            both_are_closed = l_is_closed and r_is_closed
            
            now = time.time()

            # --- LOGICA GESTURILOR (TIMERE) ---
            
            # 1. AMBII OCHI
            if both_are_closed:
                if not both_was_closed:
                    both_closed_start = now 
                else:
                    duration = now - both_closed_start
                    # Trecerea în Sleep Mode după 3 secunde
                    if duration > config["time_sleep_mode"]:
                        mouse.toggle_sleep()
                        both_closed_start = now + 2.0  # Prevenim comutarea repetată instantanee
            else:
                if both_was_closed:
                    duration = now - both_closed_start
                    # Dublu Click dacă a fost ținut între 1s și 3s
                    if config["time_double_click"] < duration < config["time_sleep_mode"]:
                        mouse.double_click()
            
            # 2. OCHI STÂNG (Izolat)
            if l_is_closed and not r_is_closed:
                if not l_was_closed:
                    l_closed_start = now
                else:
                    duration = now - l_closed_start
                    # Dacă e ținut peste 1s -> Declanșează Drag & Drop
                    if duration > config["time_drag_drop"] and not mouse.is_dragging:
                        mouse.toggle_drag_drop()
            else:
                if l_was_closed and not both_was_closed:
                    duration = now - l_closed_start
                    # La deschiderea ochiului, dacă wink-ul a fost scurt:
                    if duration < config["time_drag_drop"]:
                        if mouse.is_dragging:
                            mouse.toggle_drag_drop() # Oprește Drag (execută Drop)
                        else:
                            mouse.left_click()       # Click simplu

            # 3. OCHI DREPT (Izolat)
            if r_is_closed and not l_is_closed:
                if not r_was_closed:
                    r_closed_start = now
            else:
                if r_was_closed and not both_was_closed:
                    duration = now - r_closed_start
                    # Wink scurt cu ochiul drept -> Click dreapta
                    if duration < 1.0:
                        mouse.right_click()

            # --- ACTUALIZARE STĂRI PENTRU CADRUL URMĂTOR ---
            both_was_closed = both_are_closed
            l_was_closed = l_is_closed and not r_is_closed
            r_was_closed = r_is_closed and not l_is_closed

            # --- MIȘCARE & SCROLL (JOYSTICK) ---
            nose = landmarks[NOSE_TIP]
            vel_x = calculate_velocity(nose.x, 0.5, 0.04, config["max_speed"])
            vel_y = calculate_velocity(nose.y, 0.5, 0.04, config["max_speed"])

            if mouth_is_open:
                # Mod Scroll
                mouse.scroll_continuous(vel_x, vel_y, config["scroll_speed"])
            else:
                # Mod Normal
                mouse.move_cursor(vel_x, vel_y)

        # Verificăm tasta ESC de urgență
        mouse.check_failsafe()
        
        # Afișare pentru feedback vizual
        cv2.imshow('Vision Engine Avansat', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()