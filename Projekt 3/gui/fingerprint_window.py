import tkinter as tk
from PIL import Image, ImageTk
import os


def open_fingerprint_window(root, on_apply_callback):

    selected = {"path": None, "frame": None}

    window = tk.Toplevel(root)
    window.preview_images = []
    window.title("Odciski palców")
    window.transient(root)
    window.grab_set()

    def close_window():
        window.grab_release()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", close_window)

    window.update_idletasks()
    w, h = 620, 700
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2) - 40
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.configure(bg="#1e1e1e")

    folder = "odciski_zdjecia"

    if not os.path.exists(folder):
        tk.Label(window, text="Brak folderu", fg="white", bg="#1e1e1e").pack()
        return

    top_container = tk.Frame(window, bg="#1e1e1e")
    top_container.pack(side="top", fill="both", expand=True)

    canvas = tk.Canvas(top_container, bg="#1e1e1e", highlightthickness=0)
    scrollbar = tk.Scrollbar(top_container, orient="vertical", command=canvas.yview)

    scroll_frame = tk.Frame(canvas, bg="#1e1e1e")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    center = tk.Frame(scroll_frame, bg="#1e1e1e")
    center.pack()

    grid = tk.Frame(center, bg="#1e1e1e")
    grid.pack()

    files = [f for f in os.listdir(folder)
             if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]

    cols = 4

    def toggle(path, frame):

        if selected["path"] == path:
            frame.config(highlightbackground="#1e1e1e")
            selected["path"] = None
            selected["frame"] = None
            apply_btn.config(state="disabled", bg="gray")
            return

        if selected["frame"]:
            selected["frame"].config(highlightbackground="#1e1e1e")

        frame.config(highlightbackground="#1E90FF")

        selected["path"] = path
        selected["frame"] = frame

        apply_btn.config(state="normal", bg="#043040")

    for idx, file in enumerate(files):

        path = os.path.join(folder, file)

        img = Image.open(path)
        img.thumbnail((150, 150))

        tk_img = ImageTk.PhotoImage(img)
        window.preview_images.append(tk_img)

        row = idx // cols
        col = idx % cols

        frame = tk.Frame(
            grid,
            bg="#1e1e1e",
            highlightthickness=2,
            highlightbackground="#1e1e1e"
        )

        frame.grid(row=row, column=col, padx=12, pady=12)

        lbl = tk.Label(frame, image=tk_img, bg="#1e1e1e")
        lbl.pack()

        lbl.bind("<Button-1>", lambda e, p=path, f=frame: toggle(p, f))

        tk.Label(frame, text=file, fg="white", bg="#1e1e1e", font=("Arial", 8)).pack()

    footer = tk.Frame(window, bg="#2b2b2b", height=60)
    footer.pack(side="bottom", fill="x")
    footer.pack_propagate(False)

    btn_container = tk.Frame(footer, bg="#2b2b2b")
    btn_container.pack(expand=True)

    def apply():
        if selected["path"]:
            on_apply_callback(selected["path"])
        close_window()

    apply_btn = tk.Button(
        btn_container,
        text="Zastosuj",
        bg="gray",
        fg="white",
        state="disabled",
        width=15,
        command=apply
    )
    apply_btn.pack(side="left", padx=10)

    tk.Button(
        btn_container,
        text="Zamknij",
        bg="#444444",
        fg="white",
        width=15,
        command=close_window
    ).pack(side="left", padx=10)