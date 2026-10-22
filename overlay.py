import tkinter as tk

class JoystickOverlay:
    def __init__(self, size=150, deadzone_ratio=0.04, max_reach=0.2):
        self.size = size
        self.center = size // 2
        # max_reach reprezinta cat de mult (in dx/dy) inseamna marginea widgetului
        self.max_reach = max_reach 
        
        self.root = tk.Tk()
        self.root.overrideredirect(True) # Fără bară de titlu și margini
        self.root.wm_attributes("-topmost", True) # Mereu deasupra ferestrelor
        self.root.wm_attributes("-transparentcolor", "black") # Negrul devine complet invizibil!
        
        # Pozitionare: implicit îl punem în dreapta-jos a ecranului
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{size}x{size}+{screen_w - size - 50}+{screen_h - size - 150}")
        
        self.canvas = tk.Canvas(self.root, width=size, height=size, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        # Calculam marimea deadzone-ului în pixeli (raportat la fereastra noastra)
        dz_radius = int((deadzone_ratio / max_reach) * (size / 2))
        
        # Desenăm limitele HUD-ului
        # Cercul exterior (limita maximă)
        self.canvas.create_oval(2, 2, size-2, size-2, outline="gray", dash=(1, 3))
        
        # Cercul de deadzone (zona neutră)
        self.canvas.create_oval(
            self.center - dz_radius, self.center - dz_radius,
            self.center + dz_radius, self.center + dz_radius,
            outline="white"
        )
        
        # Indicatorul central
        self.canvas.create_oval(self.center - 2, self.center - 2, self.center + 2, self.center + 2, fill="white")
        
        # Punctul care reprezintă nasul
        self.nose_indicator = self.canvas.create_oval(
            self.center - 6, self.center - 6,
            self.center + 6, self.center + 6,
            fill="lime", outline="green"
        )

    def update(self, dx, dy, in_deadzone):
        """Apelezi funcția asta la fiecare frame din mediapipe."""
        # Schimbam culoarea: Verde dacă e în repaus, Roșu/Portocaliu dacă se mișcă
        color = "lime" if in_deadzone else "orange"
        self.canvas.itemconfig(self.nose_indicator, fill=color)
        
        # Mapăm deplasarea dx/dy în coordonate de pixeli pe overlay-ul nostru
        px_x = self.center + (dx / self.max_reach) * (self.size / 2)
        px_y = self.center + (dy / self.max_reach) * (self.size / 2)
        
        # Ne asigurăm că punctul nu iese vizual din marginea widget-ului
        px_x = max(6, min(self.size - 6, px_x))
        px_y = max(6, min(self.size - 6, px_y))
        
        # Mutăm punctul
        self.canvas.coords(
            self.nose_indicator,
            px_x - 6, px_y - 6,
            px_x + 6, px_y + 6
        )
        
        # Forțăm interfața să se redeseneze (fără să blocheze restul codului)
        self.root.update()
        
    def close(self):
        self.root.destroy()