import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import os

# Import modułów logicznych
from image_ops import to_grayscale_luminance, threshold
from projections import find_center, find_radius
from iris_engine import IrisProcessor

# --- REDUKCJA WYMIARÓW ---
BIG_IMG_W = 380
BIG_IMG_H = 190  # Zmniejszono z 220
SIDE_IMG_W = 220
SIDE_IMG_H = 140  # Zmniejszono z 160
# -------------------------

class IrisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Rozpoznawania Tęczówki - Biometria")
        # Zmniejszono wysokość okna z 820 na 720
        self.root.geometry("1300x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        self.processor = IrisProcessor()
        self.original = None
        self.gray = None
        self.labels = {}

        self.morph_ops_pupil = []
        self.morph_ops_iris = []

        self.samples = [
            ("sample1.jpg", 50, 20), ("sample2.jpg", 50, 20),
            ("sample3.jpg", 50, 14), ("sample4.jpg", 50, 14),
            ("sample5.jpg", 50, 14),
        ]

        self.init_menu()
        self.init_ui()

    def init_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Wczytaj własny obraz...", command=self.load_image)
        file_menu.add_separator()
        file_menu.add_command(label="Zamknij", command=self.root.quit)
        menubar.add_cascade(label="Plik", menu=file_menu)

        samples_menu = tk.Menu(menubar, tearoff=0)
        for name, xp, xi in self.samples:
            samples_menu.add_command(
                label=f"Otwórz {name}",
                command=lambda n=name, x_p=xp, x_i=xi: self.load_sample(n, x_p, x_i)
            )
        menubar.add_cascade(label="Przykładowe obrazy", menu=samples_menu)
        self.root.config(menu=menubar)

    def init_ui(self):
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill="both", expand=True)

        # --- LEWY PANEL ---
        left_panel = tk.Frame(main_container, width=250, bg="#2b2b2b")
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        left_panel.pack_propagate(False)

        tk.Button(left_panel, text="PRZELICZ", command=self.recompute,
                  bg="#043040", fg="white", activebackground="#043040").pack(pady=5, fill="x", padx=10)

        # Sekcja suwaków
        tk.Label(left_panel, text="XP (źrenica)", bg="#2b2b2b", fg="white", font=("Arial", 9)).pack()
        self.slider_XP = tk.Scale(left_panel, from_=1, to=100, orient=tk.HORIZONTAL, 
                                  bg="#2b2b2b", fg="white", highlightthickness=0)
        self.slider_XP.set(50); self.slider_XP.pack(fill="x", padx=10)

        tk.Label(left_panel, text="XI (tęczówka)", bg="#2b2b2b", fg="white", font=("Arial", 9)).pack()
        self.slider_XI = tk.Scale(left_panel, from_=1, to=100, orient=tk.HORIZONTAL, 
                                  bg="#2b2b2b", fg="white", highlightthickness=0)
        self.slider_XI.set(50); self.slider_XI.pack(fill="x", padx=10)

        # Sekcja morfologii
        tk.Label(left_panel, text="Morfologia", bg="#2b2b2b", fg="white", font=("Arial", 9, "bold")).pack(pady=5)
        self.morph_target = tk.StringVar(value="pupil")
        tk.Radiobutton(left_panel, text="Źrenica", variable=self.morph_target, value="pupil", 
                       bg="#2b2b2b", fg="white", selectcolor="#043040", font=("Arial", 8)).pack(anchor="w", padx=10)
        tk.Radiobutton(left_panel, text="Tęczówka", variable=self.morph_target, value="iris", 
                       bg="#2b2b2b", fg="white", selectcolor="#043040", font=("Arial", 8)).pack(anchor="w", padx=10)

        for op in ["Erozja", "Dylatacja", "Otwarcie", "Zamknięcie"]:
            tk.Button(left_panel, text=op, command=lambda o=op: self.add_morph(o), 
                      bg="#043040", fg="white", font=("Arial", 8)).pack(fill="x", pady=1, padx=10)
        
        tk.Button(left_panel, text="Wyczyść kroki", command=self.clear_morph, 
                  bg="#043040", fg="white", font=("Arial", 8)).pack(pady=5, padx=10)

        # Kontener oryginału
        orig_container = tk.LabelFrame(left_panel, text=" Oryginał ", bg="#2b2b2b", fg="white",
                                       width=SIDE_IMG_W + 10, height=SIDE_IMG_H + 25)
        orig_container.pack(side="bottom", padx=5, pady=10)
        orig_container.pack_propagate(False)
        
        self.labels["Oryginał"] = tk.Label(orig_container, bg="black")
        self.labels["Oryginał"].pack(fill="both", expand=True)

        # --- ŚRODKOWY PANEL ---
        center_panel = tk.Frame(main_container, bg="#1e1e1e")
        center_panel.pack(side="left", fill="both", expand=True)

        grid_container = tk.Frame(center_panel, bg="#1e1e1e")
        grid_container.pack(expand=True)

        process_titles = [
            "Źrenica (binary)", "Źrenica (morph)",
            "Tęczówka (binary)", "Tęczówka (morph)",
            "Okręgi", "Rozwinięcie"
        ]

        for i, title in enumerate(process_titles):
            # Ustawiamy mniejszą wysokość ramek
            frame = tk.LabelFrame(grid_container, text=f" {title} ", bg="#1e1e1e", fg="white",
                                   width=BIG_IMG_W + 10, height=BIG_IMG_H + 25)
            frame.grid(row=i // 2, column=i % 2, padx=8, pady=3)
            frame.pack_propagate(False)
            
            label = tk.Label(frame, bg="black")
            label.pack(fill="both", expand=True)
            self.labels[title] = label

        # --- PRAWY PANEL ---
        right_panel = tk.Frame(main_container, width=280, bg="#2b2b2b")
        right_panel.pack(side="right", fill="y", padx=10)
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="PODSUMOWANIE", font=("Arial", 11, "bold"), bg="#2b2b2b", fg="white").pack(pady=10)
        self.log = tk.Text(right_panel, width=32, bg="#1b1b1b", fg="white", relief="flat", font=("Consolas", 8))
        self.log.pack(padx=10, pady=5, fill="both", expand=True)

    # ===== LOGIKA =====

    def _process_new_image(self, path, is_sample=False):
        img = Image.open(path).convert("RGB")
        self.original = np.array(img)
        self.gray = to_grayscale_luminance(self.original)
        
        # Domyślne kroki TYLKO dla źrenicy, tęczówka zostaje pusta (szybszy start)
        if is_sample:
            self.morph_ops_pupil = ["Zamknięcie", "Otwarcie"]
        else:
            self.morph_ops_pupil = []
        
        self.morph_ops_iris = [] # Tęczówka zawsze czysta na starcie
            
        self.update_log()
        self.clear_results()
        self.show("Oryginał", self.original)

    def show(self, name, img):
        if name not in self.labels:
            return

        img_pil = Image.fromarray(img)

        if name == "Oryginał":
            img_pil = self.resize_with_padding(img_pil, SIDE_IMG_W, SIDE_IMG_H)
        else:
            img_pil = self.resize_with_padding(img_pil, BIG_IMG_W, BIG_IMG_H)

        tk_img = ImageTk.PhotoImage(img_pil)
        self.labels[name].config(image=tk_img)
        self.labels[name].image = tk_img

    def load_image(self):
            """Wczytywanie własnego pliku - bez domyślnej morfologii."""
            path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png *.bmp")])
            if path: 
                self._process_new_image(path, is_sample=False)

    def load_sample(self, filename, xp, xi):
        """Wczytywanie sampla - z domyślną morfologią."""
        path = os.path.join("testowe_obrazy", filename)
        if os.path.exists(path):
            self.slider_XP.set(xp)
            self.slider_XI.set(xi)
            # Przekazujemy True, aby aktywować domyślne kroki
            self._process_new_image(path, is_sample=True)
            self.recompute()

    def recompute(self):
        if self.gray is None: return
        avg_b = np.mean(self.gray)
        pp = int(avg_b / (self.slider_XP.get() / 10))
        pi = int(avg_b / (self.slider_XI.get() / 10))
        p_bin = threshold(self.gray, pp)
        i_bin = threshold(self.gray, pi)
        p_morph = self.processor.apply_morphology(p_bin, self.morph_ops_pupil)
        i_morph = self.processor.apply_morphology(i_bin, self.morph_ops_iris)
        cx, cy = find_center(p_morph)
        rp = find_radius(p_morph, cx, cy)
        ri = find_radius(i_morph, cx, cy)
        circles_img = self.original.copy()
        cv2.circle(circles_img, (cx, cy), rp, (255, 0, 0), 2)
        cv2.circle(circles_img, (cx, cy), ri, (0, 255, 0), 2)
        unwrapped = self.processor.unwrap(self.gray, cx, cy, rp, ri)
        
        for t, img in zip(["Źrenica (binary)", "Źrenica (morph)", "Tęczówka (binary)", 
                           "Tęczówka (morph)", "Okręgi", "Rozwinięcie"], 
                          [p_bin, p_morph, i_bin, i_morph, circles_img, unwrapped]):
            self.show(t, img)
        self.update_log()

    def add_morph(self, op):
        if self.morph_target.get() == "pupil": self.morph_ops_pupil.append(op)
        else: self.morph_ops_iris.append(op)
        self.update_log()

    def clear_morph(self):
        """Usuwa wszystkie kroki dla wybranego celu (źrenica/tęczówka)."""
        if self.morph_target.get() == "pupil": 
            self.morph_ops_pupil = []
        else: 
            self.morph_ops_iris = []
        self.update_log()
        # Automatyczne przeliczenie po wyczyszczeniu ułatwia pracę
        self.recompute()

    def update_log(self):
        self.log.delete("1.0", tk.END)

        self.log.insert(tk.END, "Parametry:\n")
        self.log.insert(tk.END, f"XP (źrenica): {self.slider_XP.get()}\n")
        self.log.insert(tk.END, f"XI (tęczówka): {self.slider_XI.get()}\n\n")

        self.log.insert(tk.END, "Operacje morfologiczne:\n\n")

        self.log.insert(tk.END, "Źrenica:\n")
        self.log.insert(
            tk.END,
            (" -> ".join(self.morph_ops_pupil) + "\n\n") if self.morph_ops_pupil else "\n"
        )

        self.log.insert(tk.END, "Tęczówka:\n")
        self.log.insert(
            tk.END,
            (" -> ".join(self.morph_ops_iris)) if self.morph_ops_iris else ""
        )

    def clear_results(self):
        for name in self.labels:
            if name != "Oryginał": 
                self.labels[name].config(image="")
                self.labels[name].image = None

    def resize_with_padding(self, img_pil, target_w, target_h):
        img_pil.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Tworzymy czarne tło
        new_img = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        
        # Wyśrodkowanie obrazu
        x = (target_w - img_pil.width) // 2
        y = (target_h - img_pil.height) // 2
        
        new_img.paste(img_pil, (x, y))
        return new_img