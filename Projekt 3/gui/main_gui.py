import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from gui.fingerprint_window import open_fingerprint_window

from processing.grayscale import to_grayscale
from processing.histogram_equalization import histogram_equalization


WINDOW_W = 1050
WINDOW_H = 750

BOX_W = 260
BOX_H = 300


class GUI:
    def __init__(self, root):
        self.root = root

        self.root.title("Odciski palców - Projekt 3")

        # =========================
        # CENTER + SHIFT UP
        # =========================
        self.root.update_idletasks()

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w // 2) - (WINDOW_W // 2)
        y = (screen_h // 2) - (WINDOW_H // 2) - 60

        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        self.placeholder_labels = {}

        self.create_menu()
        self.create_layout()

    # =========================
    # MENU
    # =========================
    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(
            label="Odciski palców",
            command=lambda: open_fingerprint_window(self.root, self.show_in_all_boxes)
        )

        file_menu.add_separator()
        file_menu.add_command(label="Zamknij", command=self.root.quit)

        menubar.add_cascade(label="Menu", menu=file_menu)
        self.root.config(menu=menubar)

    # =========================
    # MAIN UI
    # =========================
    def create_layout(self):

        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(expand=True)

        titles = [
            "Oryginalny obraz",
            "Przetwarzanie wstępne",
            "Binaryzacja",
            "Szkieletyzacja",
            "Poprawa szkieletyzacji",
            "Mapa minucji"
        ]

        for i, title in enumerate(titles):
            self.create_placeholder(main_container, title, i // 3, i % 3)

    # =========================
    # PLACEHOLDER
    # =========================
    def create_placeholder(self, parent, title, row, col):

        frame = tk.LabelFrame(
            parent,
            text=f" {title} ",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 11, "bold"),
            width=280,
            height=340
        )

        frame.grid(row=row, column=col, padx=12, pady=12)

        frame.grid_propagate(False)
        frame.propagate(False)

        label = tk.Label(frame, bg="black")
        label.pack(fill="both", expand=True)

        self.placeholder_labels[title] = label

    # =========================
    # GRAYSCALE
    # =========================
    def to_grayscale(self, img):
        h, w, _ = img.shape
        gray = np.zeros((h, w), dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                r, g, b = img[y, x]
                gray[y, x] = int(0.299*r + 0.587*g + 0.114*b)

        return gray

    # =========================
    # HISTOGRAM EQUALIZATION
    # =========================
    def histogram_equalization(self, img):
        h, w = img.shape
        size = h * w

        hist = [0] * 256

        for y in range(h):
            for x in range(w):
                hist[img[y, x]] += 1

        cdf = [0] * 256
        cdf[0] = hist[0]

        for i in range(1, 256):
            cdf[i] = cdf[i - 1] + hist[i]

        cdf_min = next(v for v in cdf if v > 0)

        lut = [0] * 256

        for i in range(256):
            lut[i] = int((cdf[i] - cdf_min) / (size - cdf_min) * 255)

        out = np.zeros((h, w), dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                out[y, x] = lut[img[y, x]]

        return out

    # =========================
    # IMAGE APPLY (PIPELINE)
    # =========================
    def show_in_all_boxes(self, image_path):

        # =========================
        # LOAD IMAGE
        # =========================
        img = Image.open(image_path).convert("RGB")
        img_np = np.array(img)

        # =========================
        # ORIGINAL
        # =========================
        original_pil = Image.fromarray(img_np).resize((BOX_W, BOX_H))
        tk_original = ImageTk.PhotoImage(original_pil)

        orig_box = self.placeholder_labels["Oryginalny obraz"]
        orig_box.config(image=tk_original)
        orig_box.image = tk_original

        # =========================
        # PROCESSING PIPELINE
        # =========================
        gray = to_grayscale(img_np)
        enhanced = histogram_equalization(gray)

        enhanced_pil = Image.fromarray(enhanced).resize((BOX_W, BOX_H))
        tk_enhanced = ImageTk.PhotoImage(enhanced_pil)

        pre_box = self.placeholder_labels["Przetwarzanie wstępne"]
        pre_box.config(image=tk_enhanced)
        pre_box.image = tk_enhanced

        # =========================
        # EMPTY BOXES FOR NOW
        # =========================
        empty_boxes = [
            "Binaryzacja",
            "Szkieletyzacja",
            "Poprawa szkieletyzacji",
            "Mapa minucji"
        ]

        for key in empty_boxes:
            box = self.placeholder_labels[key]
            box.config(image="", text="")
            box.image = None