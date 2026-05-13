import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np

from gui.fingerprint_window import open_fingerprint_window

from utils.binarization import global_threshold
from utils.gabor_filter import get_orientation_map, simple_gabor
from utils.grayscale import to_grayscale
from utils.histogram_equalization import clahe, histogram_equalization
from utils.morphology import opening
from utils.normalization import normalize_fingerprint
from utils.segmentation import segmentation, segmentation_global
from utils.skeletonization import K3M, morphological_skeleton
from utils.skeleton_repair import reconnect_lines, remove_short_lines
from utils.minutiae import detect_minutiae, draw_minutiae



WINDOW_W = 1050
WINDOW_H = 780

BOX_W = 260
BOX_H = 300


class GUI:
    def __init__(self, root):

        self.root = root

        self.root.title("Odciski palców - Projekt 3")

        self.root.update_idletasks()

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w // 2) - (WINDOW_W // 2)
        y = (screen_h // 2) - (WINDOW_H // 2) - 30

        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # osobne storage dla tabów
        self.placeholder_labels_k3m = {}
        self.placeholder_labels_morph = {}

        self.create_menu()
        self.create_layout()

    # =========================
    # MENU BAR
    # =========================
    def create_menu(self):

        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(
            label="Odciski palców",
            command=lambda: open_fingerprint_window(
                self.root,
                self.show_in_all_boxes
            )
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Zamknij",
            command=self.root.quit
        )

        menubar.add_cascade(
            label="Menu",
            menu=file_menu
        )

        self.root.config(menu=menubar)

    # =========================
    # LAYOUT
    # =========================
    def create_layout(self):

        # =========================
        # STYLE
        # =========================
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "TNotebook",
            background="#1e1e1e",
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#cfcfcf",
            foreground="black",
            padding=[18, 10],
            font=("Arial", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", "#f0f0f0"),
                ("active", "#dddddd")
            ]
        )

        # =========================
        # NOTEBOOK
        # =========================
        self.notebook = ttk.Notebook(self.root)

        self.notebook.pack(
            expand=True,
            fill="both"
        )

        # =========================
        # TABS
        # =========================
        self.tab_k3m = tk.Frame(
            self.notebook,
            bg="#1e1e1e"
        )

        self.tab_morph = tk.Frame(
            self.notebook,
            bg="#1e1e1e"
        )

        self.tab_compare = tk.Frame(
            self.notebook,
            bg="#1e1e1e"
        )

        self.notebook.add(
            self.tab_k3m,
            text="K3M"
        )

        self.notebook.add(
            self.tab_morph,
            text="Morfologiczna"
        )

        self.notebook.add(
            self.tab_compare,
            text="Porównanie"
        )

        titles = [
            "Oryginalny obraz",
            "Przetwarzanie wstępne",
            "Binaryzacja",
            "Szkieletyzacja",
            "Poprawa szkieletyzacji",
            "Mapa minucji"
        ]

        # =========================
        # K3M CONTAINER
        # =========================
        self.k3m_container = tk.Frame(
            self.tab_k3m,
            bg="#1e1e1e"
        )

        self.k3m_container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        for i, title in enumerate(titles):

            self.create_placeholder(
                self.k3m_container,
                title,
                i // 3,
                i % 3,
                self.placeholder_labels_k3m
            )

        # =========================
        # MORPH CONTAINER
        # =========================
        self.morph_container = tk.Frame(
            self.tab_morph,
            bg="#1e1e1e"
        )

        self.morph_container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        for i, title in enumerate(titles):

            self.create_placeholder(
                self.morph_container,
                title,
                i // 3,
                i % 3,
                self.placeholder_labels_morph
            )

        # =========================
        # COMPARE TAB
        # =========================
        tk.Label(
            self.tab_compare,
            text="Porównanie metod skeletonizacji",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 14, "bold")
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # =========================
    # PLACEHOLDER
    # =========================
    def create_placeholder(
        self,
        parent,
        title,
        row,
        col,
        storage
    ):

        frame = tk.LabelFrame(
            parent,
            text=f" {title} ",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 11, "bold"),
            width=280,
            height=340
        )

        frame.grid(
            row=row,
            column=col,
            padx=12,
            pady=12
        )

        frame.grid_propagate(False)
        frame.propagate(False)

        label = tk.Label(
            frame,
            bg="black"
        )

        label.pack(
            fill="both",
            expand=True
        )

        storage[title] = label

    # =========================
    # DISPLAY HELPER
    # =========================
    def show_image(self, img, name, storage):

        pil = Image.fromarray(img).resize((BOX_W, BOX_H))

        tk_img = ImageTk.PhotoImage(pil)

        storage[name].config(image=tk_img)
        storage[name].image = tk_img

    # =========================
    # MAIN PIPELINE
    # =========================
    def show_in_all_boxes(self, image_path):

        # =========================
        # LOAD
        # =========================
        img = Image.open(image_path).convert("RGB")

        img_np = np.array(img)

        # =========================
        # ORIGINAL
        # =========================
        self.show_image(
            img_np,
            "Oryginalny obraz",
            self.placeholder_labels_k3m
        )

        self.show_image(
            img_np,
            "Oryginalny obraz",
            self.placeholder_labels_morph
        )

        # =========================
        # PREPROCESSING
        # =========================
        gray = to_grayscale(img_np)

        normalized = normalize_fingerprint(gray)

        mask = segmentation_global(
            normalized,
            block_size=16,
            T_factor=0.4
        )

        roi = normalized * mask

        orient = get_orientation_map(
            normalized,
            block_size=16
        )

        gabor_img = simple_gabor(
            normalized,
            orient,
            freq=0.1,
            sigma=3.0
        )

        binary = global_threshold(gabor_img)

        binary_img = binary * mask

        binary_final = opening(binary_img)

        binary_final[mask == 0] = 255

        # =========================
        # INPUT FOR SKELETON
        # =========================
        input_for_k3m = (
            binary_final / 255
        ).astype(np.uint8)

        input_for_k3m = abs(1 - input_for_k3m)

        # ==================================================
        # K3M PIPELINE
        # ==================================================
        k3m_instance = K3M()

        skeleton_result_k3m = k3m_instance.skeletonize(
            input_for_k3m
        )

        repaired_k3m = reconnect_lines(
            skeleton_result_k3m,
            max_distance=7
        )

        repaired_k3m = remove_short_lines(
            repaired_k3m,
            min_length=4
        )

        endings_k3m, bifurcations_k3m = detect_minutiae(
            repaired_k3m,
            mask
        )

        minutiae_k3m = draw_minutiae(
            repaired_k3m,
            endings_k3m,
            bifurcations_k3m
        )

        skeleton_display_k3m = (
            skeleton_result_k3m * 255
        ).astype(np.uint8)

        skeleton_display_k3m = 255 - skeleton_display_k3m

        repaired_display_k3m = (
            repaired_k3m * 255
        ).astype(np.uint8)

        repaired_display_k3m = 255 - repaired_display_k3m

        # ==================================================
        # MORPH PIPELINE
        # ==================================================
        # NA RAZIE IDENTYCZNY
        # tutaj później podmienisz skeletonizację

        skeleton_result_morph = morphological_skeleton(input_for_k3m)

        repaired_morph = reconnect_lines(
            skeleton_result_morph,
            max_distance=8
        )

        repaired_morph = remove_short_lines(
            repaired_morph,
            min_length=4
        )

        endings_morph, bifurcations_morph = detect_minutiae(
            repaired_morph,
            mask
        )

        minutiae_morph = draw_minutiae(
            repaired_morph,
            endings_morph,
            bifurcations_morph
        )

        skeleton_display_morph = (
            skeleton_result_morph * 255
        ).astype(np.uint8)

        skeleton_display_morph = 255 - skeleton_display_morph

        repaired_display_morph = (
            repaired_morph * 255
        ).astype(np.uint8)

        repaired_display_morph = 255 - repaired_display_morph

        # ==================================================
        # DISPLAY K3M
        # ==================================================
        self.show_image(
            roi,
            "Przetwarzanie wstępne",
            self.placeholder_labels_k3m
        )

        self.show_image(
            binary_img,
            "Binaryzacja",
            self.placeholder_labels_k3m
        )

        self.show_image(
            skeleton_display_k3m,
            "Szkieletyzacja",
            self.placeholder_labels_k3m
        )

        self.show_image(
            repaired_display_k3m,
            "Poprawa szkieletyzacji",
            self.placeholder_labels_k3m
        )

        self.show_image(
            minutiae_k3m,
            "Mapa minucji",
            self.placeholder_labels_k3m
        )

        # ==================================================
        # DISPLAY MORPH
        # ==================================================
        self.show_image(
            roi,
            "Przetwarzanie wstępne",
            self.placeholder_labels_morph
        )

        self.show_image(
            binary_img,
            "Binaryzacja",
            self.placeholder_labels_morph
        )

        self.show_image(
            skeleton_display_morph,
            "Szkieletyzacja",
            self.placeholder_labels_morph
        )

        self.show_image(
            repaired_display_morph,
            "Poprawa szkieletyzacji",
            self.placeholder_labels_morph
        )

        self.show_image(
            minutiae_morph,
            "Mapa minucji",
            self.placeholder_labels_morph
        )