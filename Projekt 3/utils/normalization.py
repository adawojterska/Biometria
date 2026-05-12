import numpy as np
from collections import deque


# na podstawie:
#https://github.com/cuevas1208/fingerprint_recognition/blob/master/utils/normalization.py
#oraz ksiazki handbook of fingerprint recognition, strona w pdfie 148
def normalize_fingerprint(img, m0=100, v0=100):

    img = img.astype(np.float32)

    m = np.mean(img)
    v = np.var(img)

    h, w = img.shape

    normalized = np.zeros((h, w), dtype=np.float32)

    for y in range(h):
        for x in range(w):

            if img[y, x] > m:
                normalized[y, x] = (
                    m0 + np.sqrt((v0 * ((img[y, x] - m) ** 2)) / v)
                )

            else:
                normalized[y, x] = (
                    m0 - np.sqrt((v0 * ((img[y, x] - m) ** 2)) / v)
                )   

    normalized = np.clip(normalized, 0, 255)

    return normalized.astype(np.uint8)

