"""Voce: „caută …” tastează fraza în fereastra activă și apasă Enter."""
import ctypes
import sys
import threading
import time

PREFIXES = (
    "caută pe google",
    "cauta pe google",
    "caută",
    "cauta",
    "google",
)


def search_query(raw):
    """Textul de după cuvântul de activare. None dacă fraza nu e o căutare."""
    if not raw:
        return None
    lowered = raw.strip().lower()
    for prefix in PREFIXES:
        if lowered.startswith(prefix):
            rest = raw.strip()[len(prefix):].strip(" :,.-")
            return rest or None
    return None


def copy_text(text):
    """Pune textul în clipboard. pyautogui.write nu știe diacritice."""
    if sys.platform == "win32":
        _copy_windows(text)
        return
    import pyperclip

    pyperclip.copy(text)


def _copy_windows(text):
    from ctypes import wintypes

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.CloseClipboard.restype = wintypes.BOOL
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    payload = (text + "\0").encode("utf-16-le")
    if not user32.OpenClipboard(None):
        raise OSError("Nu pot deschide clipboard-ul.")
    try:
        user32.EmptyClipboard()
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(payload))
        if not handle:
            raise OSError("Nu pot aloca clipboard-ul.")
        locked = kernel32.GlobalLock(handle)
        ctypes.memmove(locked, payload, len(payload))
        kernel32.GlobalUnlock(handle)
        if not user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise OSError("Nu pot scrie în clipboard.")
    finally:
        user32.CloseClipboard()


def type_query(text):
    import pyautogui

    pyautogui.PAUSE = 0
    copy_text(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.12)
    pyautogui.press("enter")


class VoiceTyper:
    def __init__(self, language="ro-RO"):
        self.language = language
        self.is_running = False
        self.status = "Voce oprită"
        self.thread = None
        self._recognizer = None

    def start_background(self):
        """Pornește ascultarea. Întoarce un mesaj de eroare dacă microfonul nu e disponibil."""
        if self.is_running:
            return None
        try:
            import speech_recognition  # noqa: F401
        except ImportError:
            self.status = "Lipsește SpeechRecognition. Rulează pip install -r requirements.txt"
            return self.status
        self.is_running = True
        self.status = "Pornesc microfonul..."
        self.thread = threading.Thread(target=self._loop, name="voice", daemon=True)
        self.thread.start()
        return None

    def stop(self):
        self.is_running = False
        self.status = "Voce oprită"

    def _loop(self):
        try:
            import speech_recognition as sr
        except ImportError:
            self.status = "Lipsește SpeechRecognition."
            self.is_running = False
            return
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.6
        self._recognizer = recognizer
        try:
            with sr.Microphone() as source:
                self.status = "Calibrez microfonul..."
                print("[VOICE] Calibrare zgomot de fond...")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
                self.status = "Spune: caută și ce vrei să cauți"
                print("[VOICE] Mod continuu. Spune 'caută ...'.")
                while self.is_running:
                    self._hear(recognizer, source, sr)
        except OSError as exc:
            self.status = f"Microfon indisponibil: {exc}"
            print(f"[VOICE] {self.status}")
        except Exception as exc:
            self.status = f"Voce oprită: {exc}"
            print(f"[VOICE Error] {exc}")
        finally:
            self.is_running = False
            if self.status.startswith("Spune:") or self.status.startswith("Ascult") or self.status.startswith("Caut"):
                self.status = "Voce oprită"

    def _hear(self, recognizer, source, sr):
        try:
            self.status = "Ascult... spune caută și fraza"
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=8)
            self.status = "Procesez vocea..."
            raw = recognizer.recognize_google(audio, language=self.language)
            print(f"[VOICE] {raw}")
            query = search_query(raw)
            if query is None:
                self.status = f"Am auzit „{raw}”. Spune caută și fraza."
                return
            self.status = f"Caut: {query}"
            print(f"[VOICE] Cautare: {query}")
            type_query(query)
            self.status = f"Am căutat: {query}"
        except sr.WaitTimeoutError:
            if self.is_running:
                self.status = "Spune: caută și ce vrei să cauți"
        except sr.UnknownValueError:
            self.status = "Nu am înțeles. Mai spune o dată: caută ..."
        except sr.RequestError as exc:
            self.status = f"Serviciul vocal nu răspunde: {exc}"
            print(f"[VOICE] {self.status}")
            time.sleep(1.0)
        except Exception as exc:
            self.status = f"Eroare voce: {exc}"
            print(f"[VOICE Error] {exc}")
            time.sleep(0.4)
