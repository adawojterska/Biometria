import numpy as np
from utils.morphology import erode, dilate, opening, closing

class K3M:
    def __init__(self):
        # Tablica A0 służy do oznaczania pikseli brzegowych [cite: 1934]
        self.A0 = {3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96, 112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193, 195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247, 248, 249, 251, 252, 253, 254}
        
        # Tablice faz 1-5 usuwające piksele o rosnącej liczbie sąsiadów [cite: 1915-1941]
        self.A1 = {7, 14, 28, 56, 112, 131, 193, 224}
        self.A2 = {7, 14, 15, 28, 30, 56, 60, 112, 120, 131, 135, 193, 195, 224, 225, 240}
        self.A3 = {7, 14, 15, 28, 30, 31, 56, 60, 62, 112, 120, 124, 131, 135, 143, 193, 195, 199, 224, 225, 227, 240, 241, 248}
        self.A4 = {7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126, 131, 135, 143, 159, 193, 195, 199, 207, 224, 225, 227, 231, 240, 241, 243, 248, 249, 252}
        self.A5 = {7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126, 131, 135, 143, 159, 191, 193, 195, 199, 207, 224, 225, 227, 231, 239, 240, 241, 243, 248, 249, 251, 252, 254}
        
        # Tablica do finalnego pocieniania do 1 piksela [cite: 1942]
        self.A1pix = {3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96, 112, 120, 124, 126, 127, 129, 131, 135, 143, 159, 191, 192, 193, 195, 199, 207, 223, 224, 225, 227, 231, 239, 240, 241, 243, 247, 248, 249, 251, 252, 253, 254}
        
        # Macierz wag sąsiedztwa [cite: 1904]
        self.weight_matrix = np.array([[128, 1, 2],
                                       [64,  0, 4],
                                       [32, 16, 8]])

    def get_weight(self, neighborhood):
        neighborhood = (neighborhood > 0).astype(np.uint8)
        return np.sum(neighborhood * self.weight_matrix)

    def skeletonize(self, binary_image):
        img = binary_image.copy()
        rows, cols = img.shape
        
        while True:
            modified = False
            # Faza 0: Wyznaczanie pikseli brzegowych [cite: 1856, 1909]
            border_pixels = []
            for r in range(1, rows-1):
                for c in range(1, cols-1):
                    if img[r, c] == 1:
                        weight = self.get_weight(img[r-1:r+2, c-1:c+2])
                        if weight in self.A0:
                            border_pixels.append((r, c))
            
            # Fazy 1-5: Usuwanie pikseli [cite: 1857-1861, 1910]
            for phase_array in [self.A1, self.A2, self.A3, self.A4, self.A5]:
                to_remove = []
                for r, c in border_pixels:
                    if img[r, c] == 1:
                        weight = self.get_weight(img[r-1:r+2, c-1:c+2])
                        if weight in phase_array:
                            to_remove.append((r, c))
                
                if to_remove:
                    for r, c in to_remove:
                        img[r, c] = 0
                    modified = True
            
            if not modified:
                break
        
        # Faza końcowa: Pocienianie do szerokości 1 piksela
        changed = True

        while changed:
            changed = False
            to_remove = []

            for r in range(1, rows - 1):
                for c in range(1, cols - 1):

                    if img[r, c] == 1:

                        weight = self.get_weight(
                            img[r - 1:r + 2, c - 1:c + 2]
                        )

                        if weight in self.A1pix:
                            to_remove.append((r, c))

            if to_remove:
                for r, c in to_remove:
                    img[r, c] = 0

                changed = True
                        
        return img
    
def morphological_skeleton(binary_image):

    img = binary_image.copy().astype(np.uint8)

    skeleton = np.zeros_like(img)

    while np.any(img):

        # opening
        opened = opening(img)

        # różnica
        temp = img - opened
        temp[temp < 0] = 0

        # dodanie do skeletonu
        skeleton = np.logical_or(
            skeleton,
            temp
        ).astype(np.uint8)

            # erozja
        img = erode(img)

    return skeleton.astype(np.uint8)