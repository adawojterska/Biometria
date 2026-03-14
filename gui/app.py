import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

from processing.basic import grayscale, brightness, contrast, negative, threshold
from processing.convolution import convolution
from processing.filters import mean_filter, gaussian_filter, sharpen_filter
from processing.edges import prewitt, sobel, roberts
from analysis.histogram import calculate_histogram
from processing.morphology import dilation, erosion, opening, closing

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aplikacja do przetwarzania obrazu")
        self.root.geometry("1600x900")

        self.original_image = None
        self.processed_image = None
        self.tk_original_image = None
        self.tk_processed_image = None

        # ================= MENU =================
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Wczytaj obraz", command=self.load_image)
        file_menu.add_command(label="Zapisz obraz przetworzony", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)

        sample_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Przykładowe obrazy", menu=sample_menu)
        self.sample_folder = "test_images"
        self.sample_images = [f for f in os.listdir(self.sample_folder)
                              if f.lower().endswith((".jpg", ".png", ".jpeg", ".bmp"))]
        for img_name in self.sample_images:
            sample_menu.add_command(
                label=img_name,
                command=lambda name=img_name: self.load_image_from_path(os.path.join(self.sample_folder, name))
            )

        # ================= GŁÓWNY UKŁAD =================
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # LEWY PANEL
        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side="left", fill="y")

        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Operacje
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Operacje")

        ttk.Button(tab1, text="Odcienie szarości",
                   command=lambda: self.apply_operation_with_history(grayscale, "Odcienie szarości")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab1, text="Negatyw",
                   command=lambda: self.apply_operation_with_history(negative, "Negatyw")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab1, text="Korekta jasności",
                   command=lambda: self.open_brightness_window("Korekta jasności")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab1, text="Korekta kontrastu",
                   command=lambda: self.open_contrast_window("Korekta kontrastu")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab1, text="Binaryzacja",
                   command=lambda: self.open_threshold_window("Binaryzacja")).pack(fill="x", pady=5, padx=10)

        # --- Filtry
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Filtry")

        ttk.Button(tab2, text="Filtr uśredniający",
                   command=lambda: self.open_mean_filter_window("Filtr uśredniający")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab2, text="Filtr Gaussa",
                   command=lambda: self.open_gaussian_filter_window("Filtr Gaussa")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab2, text="Filtr wyostrzający",
                   command=lambda: self.apply_operation_with_history(sharpen_filter, "Filtr wyostrzający")).pack(fill="x", pady=5, padx=10)

        # --- Krawędzie
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Krawędzie")

        ttk.Button(tab3, text="Krzyż Robertsa",
                   command=lambda: self.apply_operation_with_history(roberts, "Krzyż Robertsa")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab3, text="Operator Sobela",
                   command=lambda: self.apply_operation_with_history(sobel, "Operator Sobela")).pack(fill="x", pady=5, padx=10)
        ttk.Button(tab3, text="Operator Prewitta",
                   command=lambda: self.apply_operation_with_history(prewitt, "Operator Prewitta")).pack(fill="x", pady=5, padx=10)

        # PANEL OBRAZÓW + HISTOGRAM
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side="left", expand=True, fill="both")

        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=3)
        content_frame.columnconfigure(2, weight=2)

        # Oryginał
        original_frame = ttk.LabelFrame(content_frame, text="Obraz oryginalny")
        original_frame.grid(row=0, column=0, padx=10, pady=10)
        self.original_canvas = tk.Canvas(original_frame, width=400, height=400, bg="lightgray")
        self.original_canvas.pack()

        # Przetworzony
        processed_frame = ttk.LabelFrame(content_frame, text="Obraz przetworzony")
        processed_frame.grid(row=0, column=1, padx=10, pady=10)
        self.processed_canvas = tk.Canvas(processed_frame, width=400, height=400, bg="lightgray")
        self.processed_canvas.pack()

        # HISTORIA
        history_frame = ttk.LabelFrame(content_frame, text="Historia zmian")
        history_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        self.history_listbox = tk.Listbox(history_frame, height=12)
        self.history_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        reset_btn = ttk.Button(history_frame, text="Resetuj", command=self.reset_history, width=15)
        reset_btn.grid(row=1, column=0, columnspan=2, pady=5)

        # Histogram
        histogram_frame = ttk.LabelFrame(content_frame, text="Histogram")
        histogram_frame.grid(row=0, column=2, padx=10, pady=10)
        ttk.Label(histogram_frame, text="Kanał:").pack(pady=5)

        self.channel_var = tk.StringVar(value="Gray")
        channel_menu = ttk.Combobox(
            histogram_frame,
            textvariable=self.channel_var,
            values=["R", "G", "B", "Gray"],
            state="readonly"
        )
        channel_menu.pack(pady=5)
        channel_menu.bind("<<ComboboxSelected>>", lambda e: self.update_histogram())

        self.hist_canvas = tk.Canvas(histogram_frame, width=350, height=350, bg="white")
        self.hist_canvas.pack(padx=10, pady=10)

        # --- Własny filtr z dynamiczną maską
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Własny filtr")

        # Wybór rozmiaru maski
        size_frame = ttk.Frame(tab4)
        size_frame.pack(pady=5)
        ttk.Label(size_frame, text="Rozmiar maski:").pack(side="left", padx=5)
        mask_size_var = tk.IntVar(value=3)
        size_combo = ttk.Combobox(size_frame, textvariable=mask_size_var, state="readonly", values=[3, 5, 7])
        size_combo.pack(side="left", padx=5)

        kernel_frame = ttk.Frame(tab4)
        kernel_frame.pack(pady=10)

        entries = []

        def create_kernel_entries(size):
            nonlocal entries
            for widget in kernel_frame.winfo_children():
                widget.destroy()
            entries = []
            for i in range(size):
                row_entries = []
                for j in range(size):
                    e = ttk.Entry(kernel_frame, width=5, justify="center")
                    e.grid(row=i, column=j, padx=3, pady=3)
                    e.insert(0, "0")
                    row_entries.append(e)
                entries.append(row_entries)

        create_kernel_entries(mask_size_var.get())

        def on_size_change(event):
            create_kernel_entries(mask_size_var.get())

        size_combo.bind("<<ComboboxSelected>>", on_size_change)

        def get_kernel_values():
            size = mask_size_var.get()
            kernel = []
            for i in range(size):
                row = []
                for j in range(size):
                    try:
                        val = float(entries[i][j].get())
                    except ValueError:
                        val = 0.0
                    row.append(val)
                kernel.append(row)
            return kernel

        def apply_custom_filter_gui():
            if self.processed_image is None:
                return
            kernel = get_kernel_values()  # pobranie dynamicznej maski NxN
            new_img = convolution(self.processed_image, kernel)  # użycie uniwersalnej funkcji
            self.processed_image = new_img
            self.display_processed_image(new_img)
            self.add_to_history(f"Własny filtr {len(kernel)}x{len(kernel)}")

        ttk.Button(tab4, text="Zastosuj filtr", command=apply_custom_filter_gui).pack(pady=10)
        # --- Morfologia
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="Morfologia")
        # --- Wybór trybu kolorów dla operacji morfologicznych
        ttk.Label(tab5, text="Tryb kolorów przed operacją:").pack(pady=(10, 0), padx=10)

        self.color_mode_var = tk.StringVar(value="Czarno-białe")
        color_options = [ "Szarości", "Czarno-białe"]
        ttk.Combobox(tab5, textvariable=self.color_mode_var, values=color_options, state="readonly").pack(pady=5, padx=10)
        ttk.Button(tab5, text="Dylatacja",
                command=lambda: self.apply_operation_with_history(
                    lambda img: dilation(img, mode=self.color_mode_var.get()), "Dylatacja")
                ).pack(fill="x", pady=5, padx=10)

        ttk.Button(tab5, text="Erozja",
                command=lambda: self.apply_operation_with_history(
                    lambda img: erosion(img, mode=self.color_mode_var.get()), "Erozja")
                ).pack(fill="x", pady=5, padx=10)

        ttk.Button(tab5, text="Otwarcie",
                command=lambda: self.apply_operation_with_history(
                    lambda img: opening(img, mode=self.color_mode_var.get()), "Otwarcie")
                ).pack(fill="x", pady=5, padx=10)

        ttk.Button(tab5, text="Zamknięcie",
                command=lambda: self.apply_operation_with_history(
                    lambda img: closing(img, mode=self.color_mode_var.get()), "Zamknięcie")
                ).pack(fill="x", pady=5, padx=10)
                # Domyślny obraz Lena
        self.load_default_image()

    # ================= FUNKCJE =================
    def run(self):
        self.root.mainloop()

    def load_default_image(self):
        default_path = os.path.join(self.sample_folder, "lena.png")
        if os.path.exists(default_path):
            self.load_image_from_path(default_path)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp *.jpeg")]
        )
        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, path):
        try:
            self.original_image = Image.open(path).convert("RGB")
            self.processed_image = self.original_image.copy()

            display_img = self.original_image.copy()
            display_img.thumbnail((400, 400))
            self.tk_original_image = ImageTk.PhotoImage(display_img)
            self.original_canvas.delete("all")
            self.original_canvas.create_image(200, 200, image=self.tk_original_image)

            self.display_processed_image(self.processed_image)
            self.history_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać obrazu: {e}")

    def save_image(self):
        if self.processed_image is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if file_path:
            self.processed_image.save(file_path)

    def apply_operation(self, operation, *args):
        if self.original_image is None:
            return
        base_image = self.processed_image if self.processed_image else self.original_image
        self.processed_image = operation(base_image, *args)
        self.display_processed_image(self.processed_image)

    def apply_operation_with_history(self, operation, effect_name, *args):
        self.apply_operation(operation, *args)
        self.add_to_history(effect_name)

    def display_processed_image(self, preview_img=None):
        if preview_img is None:
            preview_img = self.processed_image
        display_img = preview_img.copy()
        display_img.thumbnail((400, 400))
        self.tk_processed_image = ImageTk.PhotoImage(display_img)
        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(200, 200, image=self.tk_processed_image)
        self.update_histogram(preview_img)

    def add_to_history(self, effect_name):
        self.history_listbox.insert(tk.END, effect_name)

    def reset_history(self):
        if self.original_image is None:
            return
        self.processed_image = self.original_image.copy()
        self.display_processed_image(self.processed_image)
        self.history_listbox.delete(0, tk.END)

    # ---------------- MODALNE OKNA ----------------
    def open_brightness_window(self, title):
        self._open_param_window(title, "Wartość jasności", -100, 100, 0, brightness)

    def open_contrast_window(self, title):
        self._open_param_window(title, "Współczynnik kontrastu", 0, 300, 100, contrast, scale_factor=0.01)

    def open_threshold_window(self, title):
        self._open_param_window(title, "Próg binaryzacji", 0, 255, 127, threshold)

    def open_mean_filter_window(self, title):
        self._open_combobox_window(title, "Wybierz wartość a", [0, 1, 2, 4, 12], mean_filter)

    def open_gaussian_filter_window(self, title):
        self._open_combobox_window(title, "Wybierz wartość b", [1, 2, 3, 4], gaussian_filter)

    def _open_param_window(self, title, label_text, min_val, max_val, default, operation, scale_factor=1):
        if self.original_image is None:
            return
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("400x180")
        window.resizable(False, False)
        window.grab_set()

        ttk.Label(window, text=label_text).pack(pady=10)
        scale = tk.Scale(window, from_=min_val, to=max_val, orient="horizontal", length=300)
        scale.set(default)
        scale.pack(padx=20, pady=10)

        def update_preview(val):
            value = int(val) * scale_factor
            base_image = self.processed_image if self.processed_image else self.original_image
            preview_image = operation(base_image, value)
            self.display_processed_image(preview_image)

        scale.config(command=update_preview)

        def apply_effect():
            value = scale.get() * scale_factor
            self.apply_operation_with_history(operation, title, value)
            window.destroy()

        ttk.Button(window, text="Zastosuj", command=apply_effect).pack(pady=10)

    def _open_combobox_window(self, title, label_text, options, operation):
        if self.original_image is None:
            return
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("300x180")
        window.resizable(False, False)
        window.grab_set()

        ttk.Label(window, text=label_text).pack(pady=10)
        combo = ttk.Combobox(window, values=options, state="readonly")
        combo.set(options[0])
        combo.pack(padx=20, pady=10)

        def update_preview(event):
            value = int(combo.get())
            base_image = self.processed_image if self.processed_image else self.original_image
            preview_image = operation(base_image, value)
            self.display_processed_image(preview_image)

        combo.bind("<<ComboboxSelected>>", update_preview)

        def apply_effect():
            value = int(combo.get())
            self.apply_operation_with_history(operation, title, value)
            window.destroy()

        ttk.Button(window, text="Zastosuj", command=apply_effect).pack(pady=10)

    # ---------------- HISTOGRAM ----------------
    def update_histogram(self, img=None):
        if self.original_image is None:
            return
        if img is None:
            img = self.processed_image if self.processed_image else self.original_image
        channel = self.channel_var.get()
        hist_data = calculate_histogram(img, channel)
        self.hist_canvas.delete("all")
        canvas_w, canvas_h = 350, 350
        max_val = max(hist_data) if max(hist_data) > 0 else 1
        bar_width = canvas_w / 256

        if channel == "R":
            color = "#FF0000"
        elif channel == "G":
            color = "#00FF00"
        elif channel == "B":
            color = "#0000FF"
        else:
            color = "#808080"

        for i in range(256):
            bar_h = (hist_data[i] / max_val) * (canvas_h - 20)
            x0, y0 = i * bar_width, canvas_h
            x1, y1 = (i + 1) * bar_width, canvas_h - bar_h
            self.hist_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)

        self.hist_canvas.create_rectangle(0, 0, canvas_w, canvas_h, outline="#CCCCCC")


if __name__ == "__main__":
    app = App()
    app.run()