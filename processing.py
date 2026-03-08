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

def convolution(image, kernel):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))

    pixels = image.load()
    new_pixels = new_image.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):

            r_sum = g_sum = b_sum = 0

            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    r, g, b = pixels[x + kx, y + ky]
                    k = kernel[ky + 1][kx + 1]

                    r_sum += r * k
                    g_sum += g * k
                    b_sum += b * k

            r_new = int(max(0, min(255, r_sum)))
            g_new = int(max(0, min(255, g_sum)))
            b_new = int(max(0, min(255, b_sum)))

            new_pixels[x, y] = (r_new, g_new, b_new)

    return new_image

# uwzględniamy możliwość dodania wagi do środka filtra, aby bardziej uwzględnić wartość centralnego piksela
# było tak na slajdzie
def mean_filter(image, a=1):

    w = 8 + a

    kernel = [
        [1/w, 1/w, 1/w],
        [1/w, a/w, 1/w],
        [1/w, 1/w, 1/w]
    ]

    return convolution(image, kernel)
    

def gaussian_filter(image, b=1):
    kernel = [
        [1, b, 1],
        [b, 2*b, b],
        [1, b, 1]
    ]
    w = sum(sum(row) for row in kernel)
    kernel_normalized = [[x / w for x in row] for row in kernel]
    return convolution(image, kernel_normalized)

#https://medium.com/skylar-salernos-tech-blog/image-convolution-filters-explained-c878f1056e78
def sharpen_filter(image):
    kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]
    return convolution(image, kernel)

def roberts(image):
    pass

def sobel(image):
    pass