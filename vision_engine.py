import cv2
import math
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

current_state = {
    "nose_x": 0.0,
    "nose_y": 0.0,
    "left_eye_ratio": 0.3,
    "right_eye_ratio": 0.3,
    "mouth_ratio": 0.1,
}

# JoyStick Settings
CENTER_X = 0.5
CENTER_Y = 0.5
DEADZONE = 0.03   # 4% zonă moartă în jurul centrului pentru repaus
# Cursor speed
MAX_SPEED = 200

is_calibrated = False
calibration_frames = []
CALIBRATION_FRAME_COUNT = 45  # ~1.5 secunde la 30 fps

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def euclidean_distance(p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

NOSE_TIP = 1
EYE_TOP = 159
EYE_BOTTOM = 145
EYE_LEFT = 33
EYE_RIGHT = 133
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
RIGHT_EYE_LEFT = 362
RIGHT_EYE_RIGHT = 263
MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308


cap = cv2.VideoCapture(0)
print("Vision Engine pornit în mod Joystick. Apasă 'q' pentru a opri.")

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
            
            # Eye Ratio
            # Left Eye
            l_eye_v = euclidean_distance(face_landmarks.landmark[EYE_TOP], face_landmarks.landmark[EYE_BOTTOM])
            l_eye_h = euclidean_distance(face_landmarks.landmark[EYE_LEFT], face_landmarks.landmark[EYE_RIGHT])
            if l_eye_h > 0:
                current_state["left_eye_ratio"] = l_eye_v / l_eye_h
                
            # Right Eye
            r_eye_v = euclidean_distance(face_landmarks.landmark[RIGHT_EYE_TOP], face_landmarks.landmark[RIGHT_EYE_BOTTOM])
            r_eye_h = euclidean_distance(face_landmarks.landmark[RIGHT_EYE_LEFT], face_landmarks.landmark[RIGHT_EYE_RIGHT])
            if r_eye_h > 0:
                current_state["right_eye_ratio"] = r_eye_v / r_eye_h
                
            # Mouth 
            mouth_v_dist = euclidean_distance(face_landmarks.landmark[MOUTH_TOP], face_landmarks.landmark[MOUTH_BOTTOM])
            mouth_h_dist = euclidean_distance(face_landmarks.landmark[MOUTH_LEFT], face_landmarks.landmark[MOUTH_RIGHT])
            if mouth_h_dist > 0:
                current_state["mouth_ratio"] = mouth_v_dist / mouth_h_dist

            # JoyStick
            dx = current_state["nose_x"] - CENTER_X
            dy = current_state["nose_y"] - CENTER_Y

            mouse_velocity_x = 0.0
            mouse_velocity_y = 0.0

            if abs(dx) > DEADZONE:
                active_dx = dx - (DEADZONE if dx > 0 else -DEADZONE)
                mouse_velocity_x = active_dx * MAX_SPEED

            if abs(dy) > DEADZONE:
                active_dy = dy - (DEADZONE if dy > 0 else -DEADZONE)
                mouse_velocity_y = active_dy * MAX_SPEED

            center_px = (int(CENTER_X * w), int(CENTER_Y * h))
            nose_px = (int(current_state["nose_x"] * w), int(current_state["nose_y"] * h))
            deadzone_radius_px = int(DEADZONE * w)

            cv2.circle(image, center_px, deadzone_radius_px, (255, 120, 0), 2)
            cv2.circle(image, center_px, 3, (0, 0, 255), -1)

            in_deadzone = (abs(dx) <= DEADZONE and abs(dy) <= DEADZONE)
            nose_color = (0, 255, 0) if in_deadzone else (0, 0, 255)
            cv2.circle(image, nose_px, 5, nose_color, -1)

            if not in_deadzone:
                cv2.line(image, center_px, nose_px, (0, 165, 255), 2)

            print(f"Nose: ({current_state['nose_x']:.2f}, {current_state['nose_y']:.2f}) | "
                f"Vx: {mouse_velocity_x:5.2f} | Vy: {mouse_velocity_y:5.2f} | "
                f"L_Eye: {current_state['left_eye_ratio']:.2f} | R_Eye: {current_state['right_eye_ratio']:.2f} | "
                f"Mouth: {current_state['mouth_ratio']:.2f}")
            
    cv2.imshow('Vision Engine - Persoana 1', image)
    key = cv2.waitKey(5) & 0xFF

    if key == ord('c'):
        CENTER_X = current_state["nose_x"]
        CENTER_Y = current_state["nose_y"]
        print(f">> Recalibrare manuala reusita: Centru nou ({CENTER_X:.3f}, {CENTER_Y:.3f}) <<")

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()