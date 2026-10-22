import cv2
import math
import mediapipe as mp

# Așa trebuie să arate inițializarea:
mp_face_mesh = mp.solutions.face_mesh

# --- CONTRACTUL ---
current_state = {
    "nose_x": 0.0,       # de la 0.0 la 1.0
    "nose_y": 0.0,       # de la 0.0 la 1.0
    "eye_ratio": 0.3,    # distanța dintre pleoape
    "mouth_ratio": 0.1,  # cât de deschisă e gura
}

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Funcție utilitară pentru a calcula distanța 2D între două puncte
def euclidean_distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

# Indexurile punctelor cheie din MediaPipe Face Mesh
NOSE_TIP = 1

# Ochiul stâng (folosit ca referință pentru clipit)
EYE_TOP = 159
EYE_BOTTOM = 145
EYE_LEFT = 33
EYE_RIGHT = 133

# Gură (buza superioară și inferioară interioară)
MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308

# --- Pornire Cameră Web ---
cap = cv2.VideoCapture(0)

print("Vision Engine pornit. Apasă 'q' pentru a opri.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Nu se poate citi de la camera web.")
        break

    # Oglindim imaginea (pentru a fi mai natural) și o convertim în RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Procesăm imaginea
    results = face_mesh.process(rgb_image)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # 1. Coordonatele Nasului (mapate 0.0 - 1.0)
            nose = face_landmarks.landmark[NOSE_TIP]
            current_state["nose_x"] = nose.x
            current_state["nose_y"] = nose.y
            
            # 2. Eye Aspect Ratio (EAR) - pentru ochiul stâng
            # EAR = distanța verticală / distanța orizontală
            eye_v_dist = euclidean_distance(face_landmarks.landmark[EYE_TOP], face_landmarks.landmark[EYE_BOTTOM])
            eye_h_dist = euclidean_distance(face_landmarks.landmark[EYE_LEFT], face_landmarks.landmark[EYE_RIGHT])
            
            # Evităm împărțirea la 0
            if eye_h_dist > 0:
                current_state["eye_ratio"] = eye_v_dist / eye_h_dist
                
            # 3. Mouth Aspect Ratio (MAR)
            mouth_v_dist = euclidean_distance(face_landmarks.landmark[MOUTH_TOP], face_landmarks.landmark[MOUTH_BOTTOM])
            mouth_h_dist = euclidean_distance(face_landmarks.landmark[MOUTH_LEFT], face_landmarks.landmark[MOUTH_RIGHT])
            
            if mouth_h_dist > 0:
                current_state["mouth_ratio"] = mouth_v_dist / mouth_h_dist

            # Afișăm starea pentru a valida că totul funcționează conform misiunii tale
            print(f"Nose: ({current_state['nose_x']:.3f}, {current_state['nose_y']:.3f}) | "
                  f"Eye Ratio: {current_state['eye_ratio']:.3f} | "
                  f"Mouth Ratio: {current_state['mouth_ratio']:.3f}")

    # (Opțional) Afișăm și imaginea video pentru debug, deși pentru contract contează doar datele
    cv2.imshow('Vision Engine - Persoana 1', image)
    
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()