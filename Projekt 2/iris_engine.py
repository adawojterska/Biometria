import numpy as np
import cv2
from image_ops import threshold, opening, closing, erode, dilate

class IrisProcessor:
    @staticmethod
    def apply_morphology(img, ops):
        temp = img.copy()
        morph_map = {
            "Erozja": erode, "Dylatacja": dilate,
            "Otwarcie": opening, "Zamknięcie": closing
        }
        for op in ops:
            if op in morph_map:
                temp = morph_map[op](temp)
        return temp

    @staticmethod
    def unwrap(img, cx, cy, rp, ri, out_h=60, out_w=360):
        # Implementacja rozwinięcia (Rubber Sheet Model)
        res = np.zeros((out_h, out_w), dtype=np.uint8)
        for x in range(out_w):
            theta = 2 * np.pi * x / out_w
            for y in range(out_h):
                r = rp + (ri - rp) * (y / out_h)
                px = int(cx + r * np.cos(theta))
                py = int(cy + r * np.sin(theta))
                if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                    res[y, x] = img[py, px]
        return res