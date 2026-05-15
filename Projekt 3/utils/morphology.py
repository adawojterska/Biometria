import numpy as np


#skopiowane z poprzednich projetkow
def erode(img):
    h, w = img.shape
    out = np.zeros_like(img)
    
    # Przesunięcie o 1 piksel wystarczy dla maski 3x3
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            # Wycinamy okno 3x3
            neighborhood = img[y-1:y+2, x-1:x+2]
            out[y, x] = np.min(neighborhood)
    return out

def dilate(img):
    h, w = img.shape
    out = np.zeros_like(img)
    
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            neighborhood = img[y-1:y+2, x-1:x+2]
            out[y, x] = np.max(neighborhood)
    return out

def opening(img):
    return dilate(erode(img))

def closing(img):
    return erode(dilate(img))

def erode_cross(img):

    h, w = img.shape
    out = np.zeros_like(img)

    for y in range(1, h - 1):
        for x in range(1, w - 1):

            if (
                img[y, x] == 1 and
                img[y-1, x] == 1 and
                img[y+1, x] == 1 and
                img[y, x-1] == 1 and
                img[y, x+1] == 1
            ):
                out[y, x] = 1

    return out

def dilate_cross(img):

    h, w = img.shape
    out = np.zeros_like(img)

    for y in range(1, h - 1):
        for x in range(1, w - 1):

            if img[y, x] == 1:

                out[y, x] = 1
                out[y-1, x] = 1
                out[y+1, x] = 1
                out[y, x-1] = 1
                out[y, x+1] = 1

    return out

def opening_cross(img):
    return dilate_cross(erode_cross(img))