import time
import pyautogui
import keyboard

# Măsură de siguranță OBLIGATORIE la pyautogui! 
# Dacă mouse-ul o ia razna, trage-l brusc în orice colț al ecranului și programul va crăpa intenționat.
pyautogui.FAILSAFE = True

# ==========================================
# FAZA 2: "Creierul" (Aceasta e clasa TA)
# ==========================================
class GestureProcessor:
    def __init__(self, blink_threshold=0.20, mouth_threshold=0.05):
        # Setările de bază (le vei putea modifica mai târziu din interfața Tkinter)
        self.blink_threshold = blink_threshold
        self.mouth_threshold = mouth_threshold
        
        # Variabile de stare (State Machine)
        self.eyes_closed_frames = 0
        
        # Câte cadre (frames) trebuie să țină ochii închiși ca să declanșeze o acțiune?
        # La 30 FPS, 5 cadre înseamnă aprox 0.15 secunde.
        self.min_frames_for_click = 4
        self.max_frames_for_click = 12

    def process_data(self, eye_ratio, mouth_ratio):
        
        # --- 1. LOGICA PENTRU CLICK (Ochi) ---
        if eye_ratio < self.blink_threshold:
            # Omul are ochii închiși în acest cadru. Creștem contorul.
            self.eyes_closed_frames += 1
        else:
            # Omul a deschis ochii. Verificăm cât timp i-a ținut închiși.
            if self.eyes_closed_frames > 0:
                if self.min_frames_for_click <= self.eyes_closed_frames <= self.max_frames_for_click:
                    print(f"[ACȚIUNE] CLICK STÂNGA! (A ținut ochii închiși {self.eyes_closed_frames} cadre)")
                    
                    # DECOMENTEAZĂ LINIA DE MAI JOS DUPĂ CE VEZI CĂ LOGICA MERGE BINE ÎN CONSOLĂ
                    # pyautogui.click()
                    
                elif self.eyes_closed_frames > self.max_frames_for_click:
                    print(f"[ACȚIUNE] DOUBLE CLICK! (A ținut ochii închiși mult: {self.eyes_closed_frames} cadre)")
                    
                    # DECOMENTEAZĂ MAI JOS PT DUBLU CLICK
                    # pyautogui.doubleClick()
                
                # Resetăm contorul pentru următorul clipit
                self.eyes_closed_frames = 0

        # --- 2. LOGICA PENTRU SCROLL (Gură) ---
        if mouth_ratio > self.mouth_threshold:
            print("⬇️ [ACȚIUNE] SCROLL JOS...")
            
            # DECOMENTEAZĂ LINIA DE MAI JOS PENTRU SCROLL REAL
            # pyautogui.scroll(-40) # -40 înseamnă scroll în jos. Ajustează valoarea pentru viteză.


# ==========================================
# FAZA 1: Simulatorul (Generatorul de Date False)
# ==========================================
def run_mock_simulator():
    print("Pornește Simulatorul de Gesturi...")
    print("INSTRUCTIUNI PENTRU TINE (Testare):")
    print(" - Ține apăsat tasta 'C' pentru a simula ochii închiși.")
    print(" - Ține apăsat tasta 'V' pentru a simula gura deschisă.")
    print(" - Ține apăsat tasta 'Q' pentru a închide programul.\n")
    
    processor = GestureProcessor()
    
    # Bucla infinită (simulează feed-ul camerei web la 30 FPS)
    while True:
        # 1. Definim datele standard (om relaxat)
        current_state = {
            "eye_ratio": 0.28,   # Normal
            "mouth_ratio": 0.01  # Închis
        }
        
        # 2. Modificăm datele dacă apeși tastele (MOCKING)
        if keyboard.is_pressed('q'):
            print("Oprire simulator.")
            break
            
        if keyboard.is_pressed('c'):
            current_state["eye_ratio"] = 0.10  # Sub pragul de 0.20 -> Ochii sunt închiși
            
        if keyboard.is_pressed('v'):
            current_state["mouth_ratio"] = 0.15 # Peste pragul de 0.05 -> Gura e deschisă
            
        # 3. Trimitem datele către clasa ta ca să ia o decizie
        processor.process_data(current_state["eye_ratio"], current_state["mouth_ratio"])
        
        # 4. Dormim puțin pentru a simula cele 30 cadre pe secundă (1 secundă / 30)
        time.sleep(1 / 30)

# Punctul de pornire al scriptului
if __name__ == "__main__":
    run_mock_simulator()