import numpy as np

def to_grayscale_luminance(img):
    h, w, _ = img.shape
    gray = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            r, g, b = img[y, x]
            gray[y, x] = int(0.299*r + 0.587*g + 0.114*b)

    return gray

#  BINARYZACJA 
def threshold(img, thresh):
    h, w = img.shape
    out = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            if img[y, x] < thresh:
                out[y, x] = 255
            else:
                out[y, x] = 0

    return out

# EROZJA 
def erode(img):
    h, w = img.shape
    out = np.zeros_like(img)

    for y in range(3, h - 3):
        for x in range(3, w - 3):

            values = []
            for j in range(-3, 4):
                for i in range(-3, 4):
                    values.append(img[y + j, x + i])

            out[y, x] = min(values)

    return out


# DYLATACJA  
def dilate(img):
    h, w = img.shape
    out = np.zeros_like(img)

    for y in range(3, h - 3):
        for x in range(3, w - 3):

            values = []
            for j in range(-3, 4):
                for i in range(-3, 4):
                    values.append(img[y + j, x + i])

            out[y, x] = max(values)

    return out


def opening(img):
    return dilate(erode(img))


def closing(img):
    return erode(dilate(img))