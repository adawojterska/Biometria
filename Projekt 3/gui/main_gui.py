import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from gui.fingerprint_window import open_fingerprint_window

from utils.binarization import global_threshold
from utils.gabor_filter import  get_orientation_map, simple_gabor
from utils.grayscale import to_grayscale
from utils.histogram_equalization import clahe, histogram_equalization
from utils.morphology import closing, opening
from utils.normalization import normalize_fingerprint
from utils.segmentation import segmentation, segmentation_global
from utils.skeletonization import K3M
from utils.skeleton_repair import reconnect_lines
from utils.minutiae import detect_minutiae, draw_minutiae



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
        normalized = normalize_fingerprint(gray)
        mask = segmentation_global(normalized, block_size=16, T_factor=0.4)
        roi = normalized * mask
        orient = get_orientation_map(normalized, block_size=16)        
        gabor_img = simple_gabor(normalized, orient, freq=0.1, sigma=3.0) 
        binary = global_threshold(gabor_img)

        binary_final = binary * mask
        binary_final = opening(binary_final)
        # Zamiana czarnego tła poza maską na białe
        binary_final[mask == 0] = 255
    

        # =========================
        # SZKIELETYZACJA K3M
        # =========================
        input_for_k3m = (binary_final / 255).astype(np.uint8)
        input_for_k3m = abs(1 - input_for_k3m)
        
        k3m_instance = K3M()
        skeleton_result = k3m_instance.skeletonize(input_for_k3m)
        
        skeleton_display = (skeleton_result * 255).astype(np.uint8)
        skeleton_display = 255 - skeleton_display  # Odwrócenie kolorów (szkieletyzacja na czarno) [cite: 339]
        # =========================

        # =========================
        # NAPRAWA SZKIELETU
        # =========================
        repaired_skeleton = reconnect_lines(
            skeleton_result,
            max_distance=8
        )

        repaired_display = (repaired_skeleton * 255).astype(np.uint8)
        repaired_display = 255 - repaired_display

        # =========================
        # MAPA MINUCJI
        # =========================
        endings, bifurcations = detect_minutiae(
            repaired_skeleton,
            mask
        )


        minutiae_img = draw_minutiae(
            repaired_skeleton,
            endings,
            bifurcations
        )


        roi_pil = Image.fromarray(roi).resize((BOX_W, BOX_H))
        tk_roi = ImageTk.PhotoImage(roi_pil)

        pre_box = self.placeholder_labels["Przetwarzanie wstępne"]
        pre_box.config(image=tk_roi)
        pre_box.image = tk_roi

        binary_pil = Image.fromarray(binary_final).resize((BOX_W, BOX_H))
        tk_binary = ImageTk.PhotoImage(binary_pil)

        bin_box = self.placeholder_labels["Binaryzacja"]
        bin_box.config(image=tk_binary)
        bin_box.image = tk_binary

        skeleton_pil = Image.fromarray(skeleton_display).resize((BOX_W, BOX_H))
        tk_skeleton = ImageTk.PhotoImage(skeleton_pil)

        skel_box = self.placeholder_labels["Szkieletyzacja"]
        skel_box.config(image=tk_skeleton)
        skel_box.image = tk_skeleton

        repaired_pil = Image.fromarray(repaired_display).resize((BOX_W, BOX_H))
        tk_repaired = ImageTk.PhotoImage(repaired_pil)

        rep_box = self.placeholder_labels["Poprawa szkieletyzacji"]
        rep_box.config(image=tk_repaired)
        rep_box.image = tk_repaired

        minutiae_pil = Image.fromarray(minutiae_img).resize((BOX_W, BOX_H))
        tk_minutiae = ImageTk.PhotoImage(minutiae_pil)

        min_box = self.placeholder_labels["Mapa minucji"]
        min_box.config(image=tk_minutiae)
        min_box.image = tk_minutiae


        # =========================
        # EMPTY BOXES FOR NOW
        # =========================
        # empty_boxes = [
        #     "Mapa minucji"
        # ]

        # for key in empty_boxes:
        #     box = self.placeholder_labels[key]
        #     box.config(image="", text="")
        #     box.image = None