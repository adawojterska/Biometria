from PIL import Image
from .convolution import convolution

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
    kernel_normalized = [[x/w for x in row] for row in kernel]
    return convolution(image, kernel_normalized)

#https://medium.com/skylar-salernos-tech-blog/image-convolution-filters-explained-c878f1056e78
def sharpen_filter(image):
    kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]
    return convolution(image, kernel)