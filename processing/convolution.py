from PIL import Image

def clamp(value):
    return max(0, min(255, int(value)))

def convolution(image: Image.Image, kernel: list) -> Image.Image:
    width, height = image.size
    output_image = Image.new("RGB", (width, height))
    input_pixels = image.load()
    output_pixels = output_image.load()

    kernel_size = len(kernel)
    a = kernel_size // 2

    # Oblicz sumę wag kernela
    kernel_sum = sum(sum(row) for row in kernel)
    if kernel_sum == 0:
        kernel_sum = 1  

    for y in range(a, height - a):
        for x in range(a, width - a):
            r_sum = g_sum = b_sum = 0.0
            for j in range(kernel_size):
                for i in range(kernel_size):
                    xi = x + i - a
                    yj = y + j - a
                    input_r, input_g, input_b = input_pixels[xi, yj]
                    weight = kernel[j][i]
                    r_sum += input_r * weight
                    g_sum += input_g * weight
                    b_sum += input_b * weight

            # Normalizacja przez sumę wag
            r_sum /= kernel_sum
            g_sum /= kernel_sum
            b_sum /= kernel_sum

            output_pixels[x, y] = (clamp(r_sum), clamp(g_sum), clamp(b_sum))

    return output_image