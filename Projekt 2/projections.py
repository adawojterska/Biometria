import numpy as np

# ===== PROJEKCJE =====
def projection_x(img):
    return np.sum(img == 255, axis=0) #liczy biale w kazdej kolumnie

def projection_y(img):
    return np.sum(img == 255, axis=1) #liczy biale w kazdym wierszu


# ===== ŚRODEK =====
#def find_center(img):
#    proj_x = projection_x(img)
#    proj_y = projection_y(img)
#
#    cx = np.argmax(proj_x)
#    cy = np.argmax(proj_y)
#
#    return cx, cy


# # ===== PROMIEŃ =====
# def find_radius(img, cx, cy):
#     h, w = img.shape
#     max_r = 0

#     for y in range(h):
#         for x in range(w):
#             if img[y, x] == 255:
#                 dist = int(np.sqrt((x - cx)**2 + (y - cy)**2))
#                 if dist > max_r:
#                     max_r = dist

#     return max_r

def find_radius(img, cx, cy):
    h, w = img.shape
    max_r = min(h, w) // 2

    for r in range(1, max_r):
        points = 0
        white = 0

        for angle in range(0, 360, 1):
            x = int(cx + r * np.cos(np.deg2rad(angle)))
            y = int(cy + r * np.sin(np.deg2rad(angle)))

            if 0 <= x < w and 0 <= y < h:
                points += 1
                if img[y, x] == 255:
                    white += 1

        if points == 0:
            continue

        ratio = white / points

        if ratio < 0.4:
            return r

    return max_r

import cv2

def get_projection_at_angle(img, angle):
    h, w = img.shape
    center = (w // 2, h // 2)
    # Macierz obrotu
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Obracamy obraz binarny
    rotated = cv2.warpAffine(img, M, (w, h))
    
    # Zwracamy sumę białych pikseli w pionie (oś X) i poziomie (oś Y) dla obróconego obrazu
    proj_x = np.sum(rotated == 255, axis=0)
    proj_y = np.sum(rotated == 255, axis=1)
    
    # Wyznaczamy szczyty (argmax) w układzie obróconym
    peak_x = np.argmax(proj_x)
    peak_y = np.argmax(proj_y)
    
    # Musimy teraz te współrzędne (peak_x, peak_y) przeliczyć z powrotem na układ 0 stopni
    # Tworzymy wektor punktu
    point = np.array([peak_x, peak_y, 1])
    # Macierz odwrotna do obrotu
    M_inv = cv2.getRotationMatrix2D(center, -angle, 1.0)
    original_coords = M_inv @ point
    
    return original_coords[0], original_coords[1]

def find_center(img):
    if not np.any(img == 255):
        return 0, 0

    points_x = []
    points_y = []

    # 1. Standardowe przecięcie (0 i 90 stopni)
    p0_x, p0_y = get_projection_at_angle(img, 0)
    points_x.append(p0_x)
    points_y.append(p0_y)

    # 2. Przecięcie pod kątem 45 stopni
    p45_x, p45_y = get_projection_at_angle(img, 45)
    points_x.append(p45_x)
    points_y.append(p45_y)
    
    # Możesz dodać więcej kątów (np. 30, 60), aby zwiększyć precyzję
    p30_x, p30_y = get_projection_at_angle(img, 30)
    points_x.append(p30_x)
    points_y.append(p30_y)

    # 3. Obliczamy średnią ze wszystkich znalezionych punktów przecięcia
    cx = int(np.mean(points_x))
    cy = int(np.mean(points_y))

    return cx, cy