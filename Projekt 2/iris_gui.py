import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

# Twoje moduły
from image_ops import threshold, erode, dilate, opening, closing, to_grayscale_luminance
from projections import find_center, find_radius

IMG_W = 260
IMG_H = 180


class IrisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Iris Recognition")
        self.root.geometry("1300x750")
        self.root.resizable(False, False)

        self.original = None
        self.gray = None

        self.morph_ops_pupil = []
        self.morph_ops_iris = []

        self.samples = [
            ("sample1.jpg", 50, 20),
            ("sample2.jpg", 50, 20),
            ("sample3.jpg", 50, 14),
            ("sample4.jpg", 50, 14),
            ("sample5.jpg", 50, 14),
        ]

        self.root.configure(bg="#1e1e1e")
        self.root.option_add("*Font", "Arial 10")

        self.init_ui()


    # ===== UI =====
    def init_ui(self):
        main = tk.Frame(self.root, bg="#1e1e1e")
        main.pack(fill="both", expand=True)

        # ===== LEWY PANEL =====
        left = tk.Frame(main, width=250, bg="#2b2b2b")
        left.pack(side="left", fill="y", padx=10)
        left.pack_propagate(False)

        tk.Button(left, text="Przelicz", command=self.recompute,
        bg="#043040",fg="white",activebackground="#043040").pack(pady=10, fill="x")

        tk.Label(left, text="XP (źrenica)", bg="#2b2b2b", fg="white").pack()
        self.slider_XP = tk.Scale(left, from_=1, to=100, orient=tk.HORIZONTAL,
                                  bg="#2b2b2b",fg="white",troughcolor="#555", highlightthickness=0)
        self.slider_XP.set(50)
        self.slider_XP.pack()

        tk.Label(left, text="XI (tęczówka)", bg="#2b2b2b", fg="white").pack()
        self.slider_XI = tk.Scale(left, from_=1, to=100, orient=tk.HORIZONTAL,
                                  bg="#2b2b2b",fg="white",troughcolor="#555", highlightthickness=0)
        self.slider_XI.set(50)
        self.slider_XI.pack()

        tk.Label(left, text="Morfologia", bg="#2b2b2b", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        self.morph_target = tk.StringVar(value="pupil")

        tk.Radiobutton(left, text="Źrenica", variable=self.morph_target,
                       value="pupil",
                       bg="#2b2b2b",fg="white",selectcolor="#043040",activebackground="#2b2b2b").pack(anchor="w")

        tk.Radiobutton(left, text="Tęczówka", variable=self.morph_target,
                       value="iris",bg="#2b2b2b",fg="white",selectcolor="#043040",activebackground="#2b2b2b").pack(anchor="w")

        tk.Button(left, text="Erozja", command=lambda: self.add_morph("Erozja"),
        bg="#043040",fg="white",activebackground="#043040").pack(fill="x")

        tk.Button(left, text="Dylatacja", command=lambda: self.add_morph("Dylatacja"),
        bg="#043040",fg="white",activebackground="#043040").pack(fill="x")

        tk.Button(left, text="Otwarcie", command=lambda: self.add_morph("Otwarcie"),
        bg="#043040",fg="white",activebackground="#043040").pack(fill="x")

        tk.Button(left, text="Zamknięcie", command=lambda: self.add_morph("Zamknięcie"),
        bg="#043040",fg="white",activebackground="#043040").pack(fill="x")

        tk.Button(left, text="Wyczyść morfologię", command=self.clear_morph,
        bg="#043040",fg="white",activebackground="#043040").pack(pady=10)

        tk.Button(left, text="Wczytaj obraz", command=self.load_image,
        bg="#043040",fg="white",activebackground="#043040").pack(fill="x", pady=5)

        tk.Label(left, text="Proponowane zdjęcia", font=("Arial", 10, "bold"), bg="#2b2b2b", fg="white").pack(pady=10)

        for name, xp, xi in self.samples:
            tk.Button(left, text=name,
                      command=lambda n=name, xp=xp, xi=xi:
                      self.load_sample(n, xp, xi),
                      bg="#043040",fg="white",activebackground="#043040").pack(fill="x", pady=2)

        # ===== ŚRODEK =====
        center = tk.Frame(main, bg="#1e1e1e")
        center.pack(side="left", padx=10)

        self.labels = {}

        titles = [
            "Oryginał",
            "Źrenica (binary)",
            "Źrenica (morph)",
            "Tęczówka (binary)",
            "Tęczówka (morph)",
            "Okręgi",
            "Rozwinięcie"
        ]

        for i, title in enumerate(titles):
            frame = tk.Frame(center, width=IMG_W, height=IMG_H, bg="black")

            if i < 6:
                frame.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            else:
                frame.grid(row=2, column=1, padx=5, pady=5)

            frame.grid_propagate(False)

            label = tk.Label(frame, text=title, fg="white", bg="black")
            label.place(relwidth=1, relheight=1)

            self.labels[title] = label

        # ===== PRAWY PANEL =====
        right = tk.Frame(main, width=300, bg="#2b2b2b")
        right.pack(side="right", fill="y", padx=10)
        right.pack_propagate(False)

        tk.Label(right, text="PODSUMOWANIE", font=("Arial", 12, "bold"), bg="#2b2b2b", fg="white").pack(pady=10)

        self.log = tk.Text(right, height=30, width=35, bg="#1b1b1b", fg="white")
        self.log.pack()

    # ===== CORE =====
    def recompute(self):
        if self.gray is None:
            return

        P = np.mean(self.gray)

        XP = self.slider_XP.get() /10
        XI = self.slider_XI.get() /10

        PP = int(P / XP)
        PI = int(P / XI)

        pupil_bin = threshold(self.gray, PP)
        iris_bin = threshold(self.gray, PI)

        pupil_morph = pupil_bin.copy()
        iris_morph = iris_bin.copy()

        for op in self.morph_ops_pupil:
            if op == "Erozja":
                pupil_morph = erode(pupil_morph)
            elif op == "Dylatacja":
                pupil_morph = dilate(pupil_morph)
            elif op == "Otwarcie":
                pupil_morph = opening(pupil_morph)
            elif op == "Zamknięcie":
                pupil_morph = closing(pupil_morph)

        for op in self.morph_ops_iris:
            if op == "Erozja":
                iris_morph = erode(iris_morph)
            elif op == "Dylatacja":
                iris_morph = dilate(iris_morph)
            elif op == "Otwarcie":
                iris_morph = opening(iris_morph)
            elif op == "Zamknięcie":
                iris_morph = closing(iris_morph)

        circles_img = self.original.copy()

        pupil_circle = None
        iris_circle = None

        pupil_source = pupil_morph
        iris_source = iris_morph

        # źrenica
        if np.any(pupil_source == 255):
            cx, cy = find_center(pupil_source)
            r = find_radius(pupil_source, cx, cy)
            pupil_circle = (cx, cy, r)

        # tęczówka
        if pupil_circle:
            cx, cy, _ = pupil_circle
            if np.any(iris_source == 255):
                r2 = find_radius(iris_source, cx, cy)
                iris_circle = (cx, cy, r2)

        if pupil_circle:
            x, y, r = pupil_circle
            cv2.circle(circles_img, (x, y), r, (0, 0, 255), 2)

        if iris_circle:
            x, y, r = iris_circle
            cv2.circle(circles_img, (x, y), r, (0, 255, 0), 2)

        self.show("Źrenica (binary)", pupil_bin)
        self.show("Źrenica (morph)", pupil_morph)
        self.show("Tęczówka (binary)", iris_bin)
        self.show("Tęczówka (morph)", iris_morph)
        self.show("Okręgi", circles_img)

        if pupil_circle and iris_circle:
            cx, cy, rp = pupil_circle
            _, _, ri = iris_circle

            unwrapped = self.unwrap_iris(self.gray, cx, cy, rp, ri)
            self.show("Rozwinięcie", unwrapped)
        else:
            empty = np.zeros((IMG_H, IMG_W), dtype=np.uint8)
            self.show("Rozwinięcie", empty)

        self.update_log()

    def unwrap_iris(self, img, cx, cy, rp, ri, out_h=80, out_w=360):
        result = np.zeros((out_h, out_w), dtype=np.uint8)

        for x in range(out_w):
            theta = 2 * np.pi * x / out_w

            for y in range(out_h):
                r = rp + (ri - rp) * (y / out_h)

                px = round(int(cx + r * np.cos(theta)))
                py = round(int(cy + r * np.sin(theta)))

                if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                    result[y, x] = img[py, px]

        return result

    def add_morph(self, op):
        if self.morph_target.get() == "pupil":
            self.morph_ops_pupil.append(op)
        else:
            self.morph_ops_iris.append(op)

        self.update_log() 

    def clear_morph(self):
        if self.morph_target.get() == "pupil":
            self.morph_ops_pupil = []
        else:
            self.morph_ops_iris = []

        self.update_log() 

    def update_log(self):
        self.log.delete("1.0", tk.END)

        self.log.insert(tk.END, f"XP: {self.slider_XP.get()}\n")
        self.log.insert(tk.END, f"XI: {self.slider_XI.get()}\n\n")

        self.log.insert(tk.END, "Źrenica:\n")
        for i, op in enumerate(self.morph_ops_pupil):
            self.log.insert(tk.END, f"{i+1}. {op}\n")

        self.log.insert(tk.END, "\nTęczówka:\n")
        for i, op in enumerate(self.morph_ops_iris):
            self.log.insert(tk.END, f"{i+1}. {op}\n")

    def clear_results(self):
        # wyczyść listy morfologii
        self.morph_ops_pupil = []
        self.morph_ops_iris = []

        # wyczyść log
        self.log.delete("1.0", tk.END)

        # wyczyść obrazy (poza oryginałem)
        for name in self.labels:
            if name != "Oryginał":
                self.labels[name].config(image="", text=name)

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            img = Image.open(path).convert("RGB")
            self.original = np.array(img)

            self.gray = to_grayscale_luminance(self.original)

            self.clear_results() 

            self.show("Oryginał", self.original)

    def load_sample(self, filename, xp, xi):
        if not os.path.exists(filename):
            return

        img = Image.open(filename).convert("RGB")
        self.original = np.array(img)

        self.gray = to_grayscale_luminance(self.original)

        self.slider_XP.set(xp)
        self.slider_XI.set(xi)

        self.clear_results()

        self.show("Oryginał", self.original)

    def reset(self):
        for label in self.labels.values():
            label.config(image="", text="")

        self.morph_ops_pupil = []
        self.morph_ops_iris = []

        self.log.delete("1.0", tk.END)

    def show(self, name, img):
        img = Image.fromarray(img)
        if name == "Rozwinięcie":
            img.thumbnail((IMG_W, IMG_H))  # zachowuje proporcje!
        else:
            img = img.resize((IMG_W, IMG_H))

        tk_img = ImageTk.PhotoImage(img)

        self.labels[name].config(image=tk_img, text="")
        self.labels[name].image = tk_img

# ===== MAIN =====
if __name__ == "__main__":
    root = tk.Tk()
    app = IrisGUI(root)
    root.mainloop()