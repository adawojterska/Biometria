from PIL import Image

def calculate_histogram(image, channel):
    pixels = image.load()
    width, height = image.size
    hist = [0]*256

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if isinstance(pixel, tuple):
                r, g, b = pixel[:3]
            else:
                r = g = b = pixel

            if channel == 'R':
                value = r
            elif channel == 'G':
                value = g
            elif channel == 'B':
                value = b
            else:
                value = int(0.299*r + 0.587*g + 0.114*b)

            value = max(0, min(255, value))
            hist[value] += 1

    return hist

def calculate_projection(image, axis='vertical'):
    pixels = image.load()
    width, height = image.size
    
    if axis == 'vertical':
        proj = [0] * width
        for x in range(width):
            for y in range(height):
                pixel = pixels[x, y]
                # Sprawdzenie czy piksel jest krotką (RGB) czy liczbą (L)
                if isinstance(pixel, tuple):
                    r, g, b = pixel[:3]
                    gray = int(0.299*r + 0.587*g + 0.114*b)
                else:
                    gray = pixel
                proj[x] += gray
        return proj
    else:
        proj = [0] * height
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                if isinstance(pixel, tuple):
                    r, g, b = pixel[:3]
                    gray = int(0.299*r + 0.587*g + 0.114*b)
                else:
                    gray = pixel
                proj[y] += gray
        return proj