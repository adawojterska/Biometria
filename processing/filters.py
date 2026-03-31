from PIL import Image
from .convolution import convolution

# uwzględniamy możliwość dodania wagi do środka filtra, aby bardziej uwzględnić wartość centralnego piksela
# było tak na slajdzie
def mean_filter(image, a=1):
    kernel = [
        [1, 1, 1],
        [1, a, 1],
        [1, 1, 1]
    ]
    return convolution(image, kernel)

def gaussian_filter(image, b=1):
    kernel = [
        [1, b, 1],
        [b, b**2, b],
        [1, b, 1]
    ]
    return convolution(image, kernel)

#https://medium.com/skylar-salernos-tech-blog/image-convolution-filters-explained-c878f1056e78
def sharpen_filter(image):
    kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]
    return convolution(image, kernel)