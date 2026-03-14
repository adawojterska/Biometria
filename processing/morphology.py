from PIL import Image
from processing.basic import grayscale, threshold

#https://github.com/szkocot/Python-CV-PL-guide/blob/master/docs/5_Operacje_Morfologiczne.md
#https://docs.opencv.org/4.x/db/df6/tutorial_erosion_dilatation.html
#https://fiveable.me/computer-vision-and-image-processing/unit-2/morphological-operations/study-guide/qei8xWoaVVgcogAN
def process_color_mode(image, mode):
    if mode == "Czarno-białe":
        image = grayscale(image)
        image = threshold(image, 127)
    elif mode == "Szarości":
        image = grayscale(image)
    return image

def dilation(image, mode="Czarno-białe"):
    image = process_color_mode(image, mode)
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height-1):
        for x in range(1, width-1):
            values = []
            for j in range(-1, 2):
                for i in range(-1, 2):
                    r, g, b = pixels[x+i, y+j]
                    values.append(r)
            max_val = max(values)
            new_pixels[x, y] = (max_val, max_val, max_val)
    return new_image

def erosion(image, mode="Czarno-białe"):
    image = process_color_mode(image, mode)
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", (width, height))
    new_pixels = new_image.load()

    for y in range(1, height-1):
        for x in range(1, width-1):
            values = []
            for j in range(-1, 2):
                for i in range(-1, 2):
                    r, g, b = pixels[x+i, y+j]
                    values.append(r)
            min_val = min(values)
            new_pixels[x, y] = (min_val, min_val, min_val)
    return new_image

def opening(image, mode="Czarno-białe"):
    return dilation(erosion(image, mode), mode)

def closing(image, mode="Czarno-białe"):
    return erosion(dilation(image, mode), mode)