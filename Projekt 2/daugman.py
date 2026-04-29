import numpy as np
import cv2
from PIL import Image

# =========================
# PARAMETR DOMYŚLNY DlA GABORA
# =========================
DEFAULT_F = 1 / 4


# =========================
# 1. PASY RADIALNE \\
# =========================

def prepare_radial_bands(unwrapped, num_bands=8, crop_ratio=0.1):
    """
    8 współśrodkowych pasów (aproksymacja radialna)
    + przycięcie góra/dół (rzęsy/powieki)
    """

    h = unwrapped.shape[0]
    crop = int(h * crop_ratio)

    cropped = unwrapped[crop:h - crop, :]

    h2 = cropped.shape[0]

    # równomierne pasy (uprościenie radialności)
    band_edges = np.linspace(0, h2, num_bands + 1, dtype=int)

    bands = []
    for i in range(num_bands):
        bands.append(cropped[band_edges[i]:band_edges[i + 1], :])

    return bands


# =========================
# 2. OKNO GAUSSA (radialne)
# =========================

def gaussian_weights(size, sigma=0.5):
    x = np.linspace(-1, 1, size)
    g = np.exp(-(x ** 2) / (2 * sigma ** 2))
    return g / np.sum(g)


# =========================
# 3. 1D SYGNAŁ (POPRAWIONY ZGODNIE Z Uwagą 3)
# =========================

def band_to_1d(band, points=128):
    """
    Radialna transformacja pas → 1D sygnał
    """

    h, w = band.shape

    # 128 równych segmentów (zgodnie z instrukcją)
    segments = np.array_split(band, points, axis=1)

    weights = gaussian_weights(h, sigma=0.5)

    values = []

    for seg in segments:
        # średnia w kierunku promienia
        col_mean = np.mean(seg, axis=1)

        # stabilizacja (usunięcie DC)
        col_mean = col_mean - np.mean(col_mean)

        # uśrednienie Gauss radialne
        weighted = np.sum(col_mean * weights)

        values.append(weighted)

    signal = np.array(values, dtype=np.float32)

    # normalizacja (ważne dla Gabora)
    signal = signal - np.mean(signal)
    signal = signal / np.std(signal)

    return signal


# =========================
# 4. GABOR 1D (zgodny z teorią)
# =========================

def gabor_filter(signal, f=DEFAULT_F):
    sigma = 0.5 * np.pi * f
    lambd = 1 / f

    x = np.arange(len(signal)) - len(signal) / 2

    gaussian = np.exp(-(x ** 2) / (2 * sigma ** 2))

    real = np.cos(2 * np.pi * x / lambd)
    imag = np.sin(2 * np.pi * x / lambd)

    kernel = gaussian * (real + 1j * imag)
    kernel = kernel / np.sum(np.abs(kernel))

    return np.convolve(signal, kernel, mode="same")


# =========================
# 5. KODOWANIE PASA
# =========================

def encode_band(band, f=DEFAULT_F):
    signal = band_to_1d(band)
    filtered = gabor_filter(signal, f)

    real_bits = (filtered.real < 0).astype(np.uint8)
    imag_bits = (filtered.imag < 0).astype(np.uint8)

    return np.vstack([imag_bits, real_bits])  # 2 × 128


# =========================
# 6. IRIS CODE
# =========================

def encode_iris(bands, f=DEFAULT_F):
    code_img = encode_iris_image(bands, f)
    return code_img.flatten()


def encode_iris_image(bands, f=DEFAULT_F):
    codes = [encode_band(b, f) for b in bands]
    return np.vstack(codes)  # (16, 128)


# =========================
# 7. HAMMING DISTANCE
# =========================

def hamming_distance(code1, code2):
    return np.mean(code1 != code2)
