import numpy as np

def to_grayscale(img):
    h, w, _ = img.shape
    gray = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            r, g, b = img[y, x]
            gray[y, x] = int(0.299*r + 0.587*g + 0.114*b)

    return gray