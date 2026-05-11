import numpy as np


def histogram_equalization(img):
    h, w = img.shape
    size = h * w

    hist = [0] * 256
    for y in range(h):
        for x in range(w):
            hist[img[y, x]] += 1

    cdf = [0] * 256
    cdf[0] = hist[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + hist[i]

    cdf_min = next(x for x in cdf if x > 0)

    lut = [0] * 256
    for i in range(256):
        lut[i] = int((cdf[i] - cdf_min) / (size - cdf_min) * 255)

    out = np.zeros((h, w), dtype=np.uint8)

    for y in range(h):
        for x in range(w):
            out[y, x] = lut[img[y, x]]

    return np.array(out, dtype=np.uint8)