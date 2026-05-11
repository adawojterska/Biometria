import tkinter as tk
from tkinter import ttk

# Rozmiar okna
WINDOW_W = 1400
WINDOW_H = 800

# Rozmiary placeholderów
BOX_W = 500
BOX_H = 180


class BiometricGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Biometryczny")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg="#1e1e1e")

        self.create_tabs()

    def create_tabs(self):
        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "TNotebook",
            background="#1e1e1e",
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background="#2b2b2b",
            foreground="white",
            padding=[20, 10],
            font=("Arial", 10, "bold")
        )

        style.map(
            "TNotebook.Tab",
            background=[("selected", "#043040")]
        )

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # =========================
        # TAB 1
        # =========================
        tab1 = tk.Frame(notebook, bg="#1e1e1e")
        notebook.add(tab1, text="Analiza")

        self.create_layout(tab1)

    def create_placeholder(self, parent, title, row, col):
        frame = tk.LabelFrame(
            parent,
            text=f" {title} ",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 10, "bold"),
            width=BOX_W,
            height=BOX_H
        )

        frame.grid(row=row, column=col, padx=15, pady=15)
        frame.grid_propagate(False)

        placeholder = tk.Label(
            frame,
            bg="black"
        )

        placeholder.pack(fill="both", expand=True, padx=5, pady=5)

    def create_layout(self, parent):

        container = tk.Frame(parent, bg="#1e1e1e")
        container.pack(expand=True)

        # =========================
        # RZĄD 1
        # =========================
        self.create_placeholder(
            container,
            "Oryginalny obraz",
            0,
            0
        )

        self.create_placeholder(
            container,
            "Oryginalny obraz przetworzony",
            0,
            1
        )

        # =========================
        # RZĄD 2
        # =========================
        self.create_placeholder(
            container,
            "Binaryzacja",
            1,
            0
        )

        self.create_placeholder(
            container,
            "Szkieletyzacja",
            1,
            1
        )

        # =========================
        # RZĄD 3
        # =========================
        self.create_placeholder(
            container,
            "Szkieletyzacja przetworzona",
            2,
            0
        )

        self.create_placeholder(
            container,
            "Mapa minucji",
            2,
            1
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = BiometricGUI(root)
    root.mainloop()