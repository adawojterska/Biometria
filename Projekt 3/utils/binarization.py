import numpy as np

def global_threshold(img):
    # 1. Oblicz histogram
    hist, _ = np.histogram(img, bins=256, range=(0, 256))
    
    total = img.size
    current_max = -1
    threshold = 0
    
    sum_total = np.dot(np.arange(256), hist)
    sum_back = 0
    weight_back = 0
    
    for i in range(256):
        weight_back += hist[i]
        if weight_back == 0: continue
        
        weight_fore = total - weight_back
        if weight_fore == 0: break
        
        sum_back += i * hist[i]
        mean_back = sum_back / weight_back
        mean_fore = (sum_total - sum_back) / weight_fore
        
        # Wariancja międzyklasowa
        var_between = weight_back * weight_fore * (mean_back - mean_fore) ** 2
        
        if var_between > current_max:
            current_max = var_between
            threshold = i
            
    # 2. Zastosuj wyliczony próg
    output = np.zeros_like(img, dtype=np.uint8)
    output[img >= threshold] = 255
    output[img < threshold] = 0
    
    return output