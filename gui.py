import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import processing


class App:
    def __init__(self):
        # =========================
        # GŁÓWNE OKNO
        # =========================

        self.root = tk.Tk()
        self.root.title("Aplikacja do przetwarzania obrazu")
        self.root.geometry("1600x800")

        # =========================
        # MENU
        # =========================

        self.original_image = None
        self.tk_original_image = None
        self.processed_image = None
        self.tk_processed_image = None

        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Plik", menu=file_menu)

        file_menu.add_command(label="Wczytaj obraz", command=self.load_image)
        file_menu.add_command(label="Zapisz obraz przetworzony")
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)

        # =========================
        # GŁÓWNY UKŁAD
        # =========================

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # =========================
        # LEWY PANEL – ZAKŁADKI
        # =========================

        left_panel = ttk.Frame(main_frame, width=250)
        left_panel.pack(side="left", fill="y")

        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Operacje
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Operacje")

        ttk.Button(
            tab1,
            text="Odcienie szarości",
            command=self.apply_grayscale
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab1,
            text="Korekta jasności",
            command=self.open_brightness_window
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab1,
            text="Korekta kontrastu",
            command=self.open_contrast_window
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab1,
            text="Negatyw",
            command=self.apply_negative
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab1,
            text="Binaryzacja",
            command=self.open_threshold_window
        ).pack(fill="x", pady=5, padx=10)

        # --- Filtry
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Filtry")

        ttk.Button(
            tab2,
            text="Filtr uśredniający",
            command=self.open_mean_filter_window
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab2,
            text="Filtr Gaussa",
            command=self.open_gaussian_filter_window
        ).pack(fill="x", pady=5, padx=10)
        ttk.Button(
            tab2,
            text="Filtr wyostrzający",
            command=self.apply_sharpen_filter
        ).pack(fill="x", pady=5, padx=10)

        # --- Krawędzie
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Krawędzie")

        ttk.Button(tab3, text="Krzyż Robertsa").pack(fill="x", pady=5, padx=10)
        ttk.Button(tab3, text="Operator Sobela").pack(fill="x", pady=5, padx=10)

        # --- Własny filtr
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Własny filtr")

        kernel_frame = ttk.Frame(tab4)
        kernel_frame.pack(pady=10)

        for i in range(3):
            for j in range(3):
                ttk.Entry(kernel_frame, width=5, justify="center").grid(
                    row=i, column=j, padx=3, pady=3
                )

        ttk.Button(tab4, text="Zastosuj filtr").pack(pady=10)

        # =========================
        # PANEL OBRAZÓW + HISTOGRAM (GRID)
        # =========================


        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side="left", expand=True, fill="both")

        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=3)
        content_frame.columnconfigure(2, weight=2)

        content_frame.rowconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=3)

        # --- Oryginał
        original_frame = ttk.LabelFrame(content_frame, text="Obraz oryginalny")
        original_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.original_canvas = tk.Canvas(original_frame, width=400, height=400, bg="lightgray")
        self.original_canvas.pack()

        # --- Przetworzony
        processed_frame = ttk.LabelFrame(content_frame, text="Obraz przetworzony")
        processed_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.processed_canvas = tk.Canvas(processed_frame, width=400, height=400, bg="lightgray")
        self.processed_canvas.pack()

        # --- Histogram
        histogram_frame = ttk.LabelFrame(content_frame, text="Histogram")
        histogram_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        ttk.Label(histogram_frame, text="Kanał:").pack(pady=5)

        channel_var = tk.StringVar(value="Gray")

        channel_menu = ttk.Combobox(
            histogram_frame,
            textvariable=channel_var,
            values=["RGB", "R", "G", "B", "Gray"],
            state="readonly"
        )
        channel_menu.pack(pady=5)

        hist_canvas = tk.Canvas(histogram_frame, width=350, height=350, bg="white")
        hist_canvas.pack(padx=10, pady=10)

    def run(self):
        self.root.mainloop()

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.png *.bmp *.jpeg")]
        )

        if not file_path:
            return

        # Wczytaj obraz
        self.original_image = Image.open(file_path).convert("RGB")

        # Dopasuj do rozmiaru canvas
        self.original_image.thumbnail((400, 400))

        # Konwersja do formatu Tkinter
        self.tk_original_image = ImageTk.PhotoImage(self.original_image)

        # Wyświetlenie oryginału
        self.original_canvas.delete("all")
        self.original_canvas.create_image(
            200, 200,
            image=self.tk_original_image
        )

        # Wyczyść prawe okienko (przetworzony obraz)
        self.processed_canvas.delete("all")
        self.processed_image = None
        self.tk_processed_image = None

    def apply_grayscale(self):
        if self.original_image is None:
            return

        self.processed_image = processing.grayscale(self.original_image)

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        from PIL import ImageTk
        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200, 200,
            image=self.tk_processed_image
        )


    def open_brightness_window(self):
        if self.original_image is None:
            return

        self.brightness_window = tk.Toplevel(self.root)
        self.brightness_window.title("Korekta jasności")
        self.brightness_window.geometry("300x150")

        ttk.Label(
            self.brightness_window,
            text="Wartość jasności"
        ).pack(pady=10)

        self.brightness_scale = tk.Scale(
            self.brightness_window,
            from_=-100,
            to=100,
            orient="horizontal",
            length=250,
            command=self.update_brightness
        )
        self.brightness_scale.set(0)
        self.brightness_scale.pack(pady=10)
    
    def update_brightness(self, value):
        if self.original_image is None:
            return

        value = int(value)

        self.processed_image = processing.brightness(
            self.original_image,
            value
        )

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200,
            200,
            image=self.tk_processed_image
        )

    def open_contrast_window(self):
        if self.original_image is None:
            return

        self.contrast_window = tk.Toplevel(self.root)
        self.contrast_window.title("Korekta kontrastu")
        self.contrast_window.geometry("300x150")

        ttk.Label(
            self.contrast_window,
            text="Współczynnik kontrastu"
        ).pack(pady=10)

        self.contrast_scale = tk.Scale(
            self.contrast_window,
            from_=0,
            to=300,
            orient="horizontal",
            length=250,
            command=self.update_contrast
        )

        # 100 = brak zmiany (a = 1.0)
        self.contrast_scale.set(100)
        self.contrast_scale.pack(pady=10)

    def update_contrast(self, value):
        if self.original_image is None:
            return

        # Zamiana suwaka na współczynnik a
        a = int(value) / 100.0

        self.processed_image = processing.contrast(
            self.original_image,
            a
        )

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200,
            200,
            image=self.tk_processed_image
        )
    
    def apply_negative(self):
        if self.original_image is None:
            return

        self.processed_image = processing.negative(
            self.original_image
        )

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200,
            200,
            image=self.tk_processed_image
        )

    def open_threshold_window(self):
        if self.original_image is None:
            return

        self.threshold_window = tk.Toplevel(self.root)
        self.threshold_window.title("Binaryzacja")
        self.threshold_window.geometry("300x150")

        ttk.Label(
            self.threshold_window,
            text="Próg binaryzacji"
        ).pack(pady=10)

        self.threshold_scale = tk.Scale(
            self.threshold_window,
            from_=0,
            to=255,
            orient="horizontal",
            length=250,
            command=self.update_threshold
        )

        self.threshold_scale.set(127)
        self.threshold_scale.pack(pady=10)

    def update_threshold(self, value):
        if self.original_image is None:
            return

        T = int(value)

        self.processed_image = processing.threshold(
            self.original_image,
            T
        )

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200,
            200,
            image=self.tk_processed_image
        )

    def open_mean_filter_window(self):
        if self.original_image is None:
            return

        self.mean_window = tk.Toplevel(self.root)
        self.mean_window.title("Filtr uśredniający")
        self.mean_window.geometry("250x120")

        ttk.Label(
            self.mean_window,
            text="Wartość środka (a)"
        ).pack(pady=10)

        # dozwolone wartości
        self.mean_values = [0, 1, 2, 4, 12]

        # combobox zamiast suwaka bo suwak się mulił
        self.mean_combo = ttk.Combobox(
            self.mean_window,
            values=self.mean_values,
            state="readonly"
        )
        self.mean_combo.set(1)  # domyślnie 1
        self.mean_combo.pack(pady=5)

        self.mean_combo.bind("<<ComboboxSelected>>", self.update_mean_filter)
            
    def update_mean_filter(self, event):
        if self.original_image is None:
            return

        a = int(self.mean_combo.get())

        self.processed_image = processing.mean_filter(self.original_image, a)

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))

        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200, 200,
            image=self.tk_processed_image
        )
    def open_gaussian_filter_window(self):
        if self.original_image is None:
            return

        self.gaussian_window = tk.Toplevel(self.root)
        self.gaussian_window.title("Filtr Gaussa")
        self.gaussian_window.geometry("250x120")

        ttk.Label(
            self.gaussian_window,
            text="Wybierz wartość b"
        ).pack(pady=10)

        # dozwolone wartości b
        self.gaussian_values = [1, 2, 3, 4]

        # combobox zamiast przycisku
        self.gaussian_combo = ttk.Combobox(
            self.gaussian_window,
            values=self.gaussian_values,
            state="readonly"
        )
        self.gaussian_combo.set(1)  # domyślnie 1
        self.gaussian_combo.pack(pady=5)

        # Aktualizacja obrazu przy każdej zmianie comboboxa
        self.gaussian_combo.bind("<<ComboboxSelected>>", self.update_gaussian_filter)


    def update_gaussian_filter(self, event):
        if self.original_image is None:
            return

        b = int(self.gaussian_combo.get())
        self.processed_image = processing.gaussian_filter(self.original_image, b)

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))
        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200, 200,
            image=self.tk_processed_image
        )
    def apply_sharpen_filter(self):
        if self.original_image is None:
            return

        self.processed_image = processing.sharpen_filter(self.original_image)

        display_img = self.processed_image.copy()
        display_img.thumbnail((400, 400))
        self.tk_processed_image = ImageTk.PhotoImage(display_img)

        self.processed_canvas.delete("all")
        self.processed_canvas.create_image(
            200, 200,
            image=self.tk_processed_image
        )