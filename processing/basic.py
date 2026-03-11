from PIL import Image

# http://www.algorytm.org/przetwarzanie-obrazow/skala-szarosci.html
def grayscale(image):
    width, height = image.size
    gray_image = Image.new("RGB", (width, height))
    pixels = image.load()
    gray_pixels = gray_image.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            gray = int(0.299*r + 0.587*g + 0.114*b)
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
            new_pixels[x, y] = (clamp(r+value), clamp(g+value), clamp(b+value))
    return new_image

# http://www.algorytm.org/przetwarzanie-obrazow/zmiana-kontrastu-obrazu.html
def contrast(image, a):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))
    pixels = image.load()
    new_pixels = new_image.load()
    midpoint = 255 / 2
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            r_new = int(clamp(a*(r-midpoint)+midpoint))
            g_new = int(clamp(a*(g-midpoint)+midpoint))
            b_new = int(clamp(a*(b-midpoint)+midpoint))
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
            new_pixels[x, y] = (255-r, 255-g, 255-b)
    return new_image

def threshold(image, T):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))
    pixels = image.load()
    new_pixels = new_image.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            gray = int(0.299*r + 0.587*g + 0.114*b)
            value = 255 if gray >= T else 0
            new_pixels[x, y] = (value, value, value)
    return new_image

def clamp(val):
    return max(0, min(255, int(val)))