# voice_engine.py
import speech_recognition as sr
import pyautogui
import threading
import time

class VoiceTyper:
    def __init__(self, language="ro-RO"):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.is_running = False
        self.thread = None
        
        # Ajustare automată a sensibilității la zgomotul de fond
        self.recognizer.dynamic_energy_threshold = True

    def listen_and_type_once(self):
        """Ascultă o singură frază și o tastează direct în fereastra activă."""
        with sr.Microphone() as source:
            print("\n[VOICE] Calibrare zgomot de fond...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("[VOICE] Te ascult... Vorbește acum!")
            
            try:
                # Timeout 5s dacă nu începe să vorbească, maxim 8s fraza
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                print("[VOICE] Procesez vocea...")
                
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"[VOICE] Recunoscut: '{text}'")
                
                # Tastează textul caracter cu caracter
                pyautogui.write(text, interval=0.03)
                
                # Apasă Enter automat pentru a trimite căutarea
                time.sleep(0.2)
                pyautogui.press('enter')
                print("[VOICE] Text tastat și Enter apăsat!")
                return text
                
            except sr.WaitTimeoutError:
                print("[VOICE] Nu am auzit nimic (timeout).")
            except sr.UnknownValueError:
                print("[VOICE] Nu am înțeles ce ai spus.")
            except sr.RequestError as e:
                print(f"[VOICE] Eroare conexiune serviciu: {e}")
            return None

    def continuous_listen_loop(self):
        """Buclă care ascultă comanda de activare 'scrie'."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("[VOICE] Mod continuu pornit. Spune 'scrie [ce vrei]' oricând.")
            
            while self.is_running:
                try:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=6)
                    raw_text = self.recognizer.recognize_google(audio, language=self.language).lower()
                    print(f"[VOICE Buffer]: {raw_text}")
                    
                    # Dacă zice "scrie ..." sau "google ..."
                    if raw_text.startswith("scrie") or raw_text.startswith("scrie"):
                        query = raw_text.replace("scrie", "").replace("scrie", "").strip()
                        if query:
                            print(f"[VOICE] Execut căutare pentru: '{query}'")
                            pyautogui.write(query, interval=0.03)
                            pyautogui.press('enter')
                            
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except Exception as e:
                    print(f"[VOICE Error]: {e}")

    def start_background(self):
        """Pornește ascultarea pe un thread paralel fără să blocheze camera/mouse-ul."""
        self.is_running = True
        self.thread = threading.Thread(target=self.continuous_listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False


# TEST RAPID INDEPENDENT:
if __name__ == "__main__":
    print("Deschide Google în browser, pune cursorul pe bara de căutare.")
    print("Ai 3 secunde să dai click pe bara Google...")
    time.sleep(3)
    
    typer = VoiceTyper(language="ro-RO")
    typer.listen_and_type_once()