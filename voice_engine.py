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
                
                text_procesat = text.lower().strip()

                # 1. Șterge absolut tot din câmpul de text
                if any(cmd in text_procesat for cmd in ["șterge tot", "sterge tot", "șterge to", "sterge to", "anulează tot", "anuleaza tot", "clear"]):
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('backspace')
                    print("[VOICE] Comandă executată: Șterge tot")

                # 2. Șterge ultimul cuvânt scris
                elif any(cmd in text_procesat for cmd in ["șterge", "sterge", "șterge cuvântul", "sterge cuvantul", "șterge cuvântu", "sterge cuvantu"]):
                    pyautogui.hotkey('ctrl', 'backspace')
                    print("[VOICE] Comandă executată: Șterge ultimul cuvânt")

                # 3. Șterge un singur caracter (o singură literă)
                elif any(cmd in text_procesat for cmd in ["șterge litera", "sterge litera", "șterge o liter", "sterge o liter", "șterge un caracter", "sterge un caracter", "șterge un caracte", "sterge un caracte", "backspace"]):
                    pyautogui.press('backspace')
                    print("[VOICE] Comandă executată: Șterge o literă")

                # 4. Comanda de căutare (tastează ce urmează după "caută" și apasă Enter)
                elif text_procesat.startswith("caută"):
                    cuvant_cautat = text_procesat.replace("caută", "").strip()
                    pyautogui.write(cuvant_cautat, interval=0.03)
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    print(f"[VOICE] Comandă executată: Căutare după '{cuvant_cautat}'")

                # 5. Mod dictare normală: doar scrie textul
                elif text_procesat.startswith("scrie"):
                    text_de_scris = text_procesat.replace("scrie", "", 1).strip()
                    if text_de_scris:
                        pyautogui.write(text_de_scris + " ", interval=0.03)
                        print(f"[VOICE] Comandă executată: Scrie '{text_de_scris}'")

                # 6. Orice altceva este ignorat 
                else:
                    print(f"[VOICE] Ignorat (fără comandă validă): '{text_procesat}'")
                
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
            print("[VOICE] Mod continuu pornit. Aștept comenzi ('scrie', 'caută', 'șterge')...")
            
            while self.is_running:
                try:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=6)
                    raw_text = self.recognizer.recognize_google(audio, language=self.language)
                    print(f"[VOICE Buffer]: {raw_text}")
                    
                    text_procesat = raw_text.lower().strip()

                    # 1. Șterge absolut tot (Cea mai lungă/specifică)
                    if any(cmd in text_procesat for cmd in ["șterge tot", "sterge tot", "șterge to", "sterge to", "anulează tot", "anuleaza tot", "clear"]):
                        pyautogui.hotkey('ctrl', 'a')
                        pyautogui.press('backspace')
                        print("[VOICE] Comandă executată: Șterge tot")

                    # 2. Șterge un singur caracter (Mutat mai sus pentru că e mai specific decât "șterge" simplu)
                    elif any(cmd in text_procesat for cmd in ["șterge litera", "sterge litera", "șterge o liter", "sterge o liter", "șterge o lite", "sterge o lite", "șterge un caracter", "sterge un caracter", "șterge un caracte", "sterge un caracte", "backspace"]):
                        pyautogui.press('backspace')
                        print("[VOICE] Comandă executată: Șterge o literă")

                    # 3. Șterge ultimul cuvânt (Lăsat ultimul pentru că "șterge" face match pe aproape orice)
                    elif any(cmd in text_procesat for cmd in ["șterge", "sterge", "șterge cuvântul", "sterge cuvantul", "șterge cuvântu", "sterge cuvantu"]):
                        pyautogui.hotkey('ctrl', 'backspace')
                        print("[VOICE] Comandă executată: Șterge ultimul cuvânt")

                    # 4. Comanda de căutare (tastează + Enter)
                    elif text_procesat.startswith("caută"):
                        cuvant_cautat = text_procesat.replace("caută", "", 1).strip()
                        if cuvant_cautat:
                            pyautogui.write(cuvant_cautat, interval=0.03)
                            time.sleep(0.2)
                            pyautogui.press('enter')
                            print(f"[VOICE] Comandă executată: Căutare după '{cuvant_cautat}'")

                    # 5. Dictare normală: doar scrie textul
                    elif text_procesat.startswith("scrie"):
                        text_de_scris = text_procesat.replace("scrie", "", 1).strip()
                        if text_de_scris:
                            pyautogui.write(text_de_scris + " ", interval=0.03)
                            print(f"[VOICE] Comandă executată: Scrie '{text_de_scris}'")

                    # 6. Ignoră ce nu e comandă
                    else:
                        print(f"[VOICE] Ignorat (fără comandă validă): '{text_procesat}'")

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