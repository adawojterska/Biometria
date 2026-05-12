import numpy as np
from scipy import ndimage

def get_orientation_map(img, block_size=16):
    # 1. Ręczny Sobel - klasyczne macierze
    # Ważne: ksize=3, format float dla precyzji
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    
    gx = ndimage.convolve(img.astype(float), kx, mode='nearest')
    gy = ndimage.convolve(img.astype(float), ky, mode='nearest')
    
    # 2. Obliczanie komponentów kąta (podwojony kąt dla ciągłości)
    v_x = 2 * gx * gy
    v_y = gx**2 - gy**2
    
    # 3. Wygładzanie - zamiast skomplikowanego Gaussa użyjemy ndimage.gaussian_filter
    # To jest standard w biometrii, żeby uśrednić kierunek w bloku
    v_x = ndimage.gaussian_filter(v_x, sigma=block_size/2)
    v_y = ndimage.gaussian_filter(v_y, sigma=block_size/2)
    
    # 4. Finalna orientacja (w radianach)
    orientations = 0.5 * np.arctan2(v_x, v_y)
    return orientations

def get_manual_gabor_kernel(size, sigma, theta, lambd):
    """Generuje jądro Gabora - prosta i skuteczna wersja"""
    half_s = size // 2
    y, x = np.mgrid[-half_s:half_s+1, -half_s:half_s+1]
    
    # Rotacja
    x_theta = x * np.cos(theta) + y * np.sin(theta)
    y_theta = -x * np.sin(theta) + y * np.cos(theta)
    
    # Gabor: Obwiednia Gaussa * Fala kosinusoidalna
    # lambd to długość fali (1/freq)
    phi = 0 # faza
    gamma = 0.5 # proporcje elipsy
    
    gb = np.exp(-0.5 * (x_theta**2 + (gamma**2 * y_theta**2)) / sigma**2) * \
         np.cos(2 * np.pi * x_theta / lambd + phi)
    
    return gb.astype(np.float32)

def simple_gabor(img, orientations, freq=0.1, sigma=3.0):
    img = img.astype(np.float32)
    h, w = img.shape
    out = np.zeros_like(img)
    
    num_angles = 16
    lambd = 1.0 / freq
    size = int(sigma * 3) # Rozmiar dopasowany do sigmy
    if size % 2 == 0: size += 1
    
    # Przygotuj bank filtrów
    bank = []
    for i in range(num_angles):
        angle = i * np.pi / num_angles
        # Obracamy o 90 stopni, żeby filtr był wzdłuż linii
        kernel = get_manual_gabor_kernel(size, sigma, angle + np.pi/2, lambd)
        kernel -= kernel.mean() # Usuwamy składową stałą (wyrównanie jasności)
        bank.append(kernel)
    
    # Filtrowanie całego obrazu każdym filtrem
    responses = [ndimage.convolve(img, k, mode='nearest') for k in bank]
    
    # Wybieranie najlepszej odpowiedzi na podstawie mapy orientacji
    # Orientacja jest w zakresie -pi/2 do pi/2, mapujemy na 0 do num_angles-1
    angle_idx = ((orientations + np.pi/2) / np.pi * num_angles).astype(int) % num_angles
    
    for i in range(num_angles):
        mask = (angle_idx == i)
        out[mask] = responses[i][mask]
    
    # Normalizacja końcowa do 0-255
    out = (out - out.min()) / (out.max() - out.min() + 1e-5) * 255
    return out.astype(np.uint8)