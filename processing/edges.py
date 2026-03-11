import math

from PIL import Image
from processing.basic import grayscale
from processing.convolution import convolution

#https://pl.wikipedia.org/wiki/Krzy%C5%BC_Robertsa
def roberts(image):
    gray = grayscale(image)
    pixels = gray.load()
    width, height = gray.size

    new_image = Image.new("RGB", (width, height))
    new_pixels = new_image.load()

    for y in range(height - 1):
        for x in range(width - 1):
            gx = pixels[x, y][0] - pixels[x + 1, y + 1][0]
            gy = pixels[x + 1, y][0] - pixels[x, y + 1][0]
            g = int(min(255, (abs(gx) + abs(gy))))
            new_pixels[x, y] = (g, g, g)

    return new_image

#https://en.wikipedia.org/wiki/Sobel_operator
#https://medium.com/@twinnroshan/understanding-and-implementing-edge-detection-in-c-with-sobel-operator-31159f26587c
def sobel(image):
    gray = grayscale(image)  # konwersja do odcieni szarości
    pixels = gray.load()
    width, height = gray.size

    # Kernels Sobela
    gx_kernel = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]
    gy_kernel = [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ]

    new_image = Image.new("RGB", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sumx = 0.0
            sumy = 0.0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    px = x + kx
                    py = y + ky
                    val = pixels[px, py][0]  # wartość szarości
                    sumx += val * gx_kernel[ky + 1][kx + 1]
                    sumy += val * gy_kernel[ky + 1][kx + 1]

            g_val = int(min(255, math.sqrt(sumx**2 + sumy**2)))
            new_pixels[x, y] = (g_val, g_val, g_val)

    return new_image

#https://www.geeksforgeeks.org/software-engineering/edge-detection-using-prewitt-scharr-and-sobel-operator/
def prewitt(image):
    gray = grayscale(image)
    pixels = gray.load()
    width, height = gray.size

    # Kernels Prewitta
    gx_kernel = [
        [-1, 0, 1],
        [-1, 0, 1],
        [-1, 0, 1]
    ]
    gy_kernel = [
        [-1, -1, -1],
        [0, 0, 0],
        [1, 1, 1]
    ]

    new_image = Image.new("RGB", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sumx = sumy = 0.0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    px = x + kx
                    py = y + ky
                    val = pixels[px, py][0]
                    sumx += val * gx_kernel[ky + 1][kx + 1]
                    sumy += val * gy_kernel[ky + 1][kx + 1]

            g_val = int(min(255, math.sqrt(sumx**2 + sumy**2)))
            new_pixels[x, y] = (g_val, g_val, g_val)

    return new_image

