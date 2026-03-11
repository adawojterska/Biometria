from PIL import Image

def clamp(val):
    return max(0, min(255, int(val)))

def convolution(image: Image.Image, kernel: list) -> Image.Image:
    width, height = image.size
    new_image = Image.new("RGB", (width, height))
    pixels = image.load()
    new_pixels = new_image.load()

    size = len(kernel)
    offset = size // 2  

    for y in range(offset, height - offset):
        for x in range(offset, width - offset):
            r_sum = g_sum = b_sum = 0.0
            for ky in range(size):
                for kx in range(size):
                    px = x + kx - offset
                    py = y + ky - offset
                    r, g, b = pixels[px, py]
                    k = kernel[ky][kx]
                    r_sum += r * k
                    g_sum += g * k
                    b_sum += b * k
            new_pixels[x, y] = (clamp(r_sum), clamp(g_sum), clamp(b_sum))

    return new_image