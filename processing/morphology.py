from PIL import Image
from processing.basic import grayscale, threshold


def process_color_mode(image, mode):
    if mode == "Czarno-białe":
        image = grayscale(image)
        image = threshold(image, 127)
    elif mode == "Szarości":
        image = grayscale(image)
    return image.convert("L")  # pracujemy na jednym kanale


def dilation(image, mode="Czarno-białe"):
    image = process_color_mode(image, mode)
    width, height = image.size
    pixels = image.load()

    new_image = Image.new("L", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):

            values = []
            for j in range(-1, 2):
                for i in range(-1, 2):
                    values.append(pixels[x + i, y + j])

            if mode == "Czarno-białe":
                # binary: OR (czyli max logiczny)
                new_pixels[x, y] = 255 if max(values) > 0 else 0
            else:
                # grayscale: max
                new_pixels[x, y] = max(values)

    return new_image.convert("RGB")


def erosion(image, mode="Czarno-białe"):
    image = process_color_mode(image, mode)
    width, height = image.size
    pixels = image.load()

    new_image = Image.new("L", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height - 1):
        for x in range(1, width - 1):

            values = []
            for j in range(-1, 2):
                for i in range(-1, 2):
                    values.append(pixels[x + i, y + j])

            if mode == "Czarno-białe":
                # binary: AND (czyli min logiczny)
                new_pixels[x, y] = 255 if min(values) == 255 else 0
            else:
                # grayscale: min
                new_pixels[x, y] = min(values)

    return new_image.convert("RGB")


def opening(image, mode="Czarno-białe"):
    return dilation(erosion(image, mode), mode)


def closing(image, mode="Czarno-białe"):
    return erosion(dilation(image, mode), mode)