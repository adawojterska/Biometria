from PIL import Image

# http://www.algorytm.org/przetwarzanie-obrazow/skala-szarosci.html
def grayscale(image):
    width, height = image.size
    gray_image = Image.new("RGB", (width, height))

    # Pobranie pikseli
    pixels = image.load()
    gray_pixels = gray_image.load()

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            # Wzór luminancji
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)

            gray_pixels[x, y] = (gray, gray, gray)

    return gray_image

# http://www.algorytm.org/przetwarzanie-obrazow/zmiana-jasnosci-obrazu.html
def brightness(image, value):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))

    pixels = image.load()
    new_pixels = new_image.load()

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            r_new = max(0, min(255, r + value))
            g_new = max(0, min(255, g + value))
            b_new = max(0, min(255, b + value))

            new_pixels[x, y] = (r_new, g_new, b_new)

    return new_image

# http://www.algorytm.org/przetwarzanie-obrazow/zmiana-kontrastu-obrazu.html
def contrast(image, a):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))

    pixels = image.load()
    new_pixels = new_image.load()

    imax = 255
    midpoint = imax / 2

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            r_new = a * (r - midpoint) + midpoint
            g_new = a * (g - midpoint) + midpoint
            b_new = a * (b - midpoint) + midpoint

            # Ograniczenie zakresu
            r_new = int(max(0, min(255, r_new)))
            g_new = int(max(0, min(255, g_new)))
            b_new = int(max(0, min(255, b_new)))

            new_pixels[x, y] = (r_new, g_new, b_new)

    return new_image

# http://www.algorytm.org/przetwarzanie-obrazow/negatyw-obrazu.html
def negative(image):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))

    pixels = image.load()
    new_pixels = new_image.load()

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            r_new = 255 - r
            g_new = 255 - g
            b_new = 255 - b

            new_pixels[x, y] = (r_new, g_new, b_new)

    return new_image

def threshold(image, T):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))

    pixels = image.load()
    new_pixels = new_image.load()

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            # Najpierw przeliczamy na szarość
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)

            if gray >= T:
                value = 255
            else:
                value = 0

            new_pixels[x, y] = (value, value, value)

    return new_image

def mean_filter(image):
    pass

def gaussian_filter(image):
    pass

def sharpen_filter(image):
    pass

def roberts(image):
    pass

def sobel(image):
    pass