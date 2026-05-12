import numpy as np
from collections import deque


#https://github.com/cuevas1208/fingerprint_recognition/blob/master/utils/segmentation.py
#block-wise gray-scale variance segmentation
#https://www.researchgate.net/publication/224320769_Improved_fingerprint_image_segmentation_using_new_modified_gradient_based_technique
#sekcja 2.1

#ogolnie dziala mi lepiej global segmentattion tzn treshold staly dla kazdego boxa
def segmentation_global(img, block_size=16, T_factor=0.2):

    img = img.astype(np.float32)

    h, w = img.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    global_std = np.std(img)
    threshold = T_factor * global_std

    for y in range(0, h, block_size):
        for x in range(0, w, block_size):

            block = img[y:y+block_size, x:x+block_size]

            if block.size == 0:
                continue

            block_std = np.std(block)

            if block_std > threshold:
                mask[y:y+block_size, x:x+block_size] = 1

    mask = keep_largest_component(mask)
    mask  = fill_holes(mask)
    mask = add_margin(mask, margin=8)


    return mask

def segmentation(img, block_size=16, k=1.2):

    img = img.astype(np.float32)

    h, w = img.shape
    mask = np.zeros((h, w), dtype=np.uint8)

    block_stds = []
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):

            block = img[y:y+block_size, x:x+block_size]

            if block.size == 0:
                continue

            block_stds.append(np.std(block))

    block_stds = np.array(block_stds)
    mean_std = np.mean(block_stds)
    threshold = k * mean_std
    idx = 0

    for y in range(0, h, block_size):
        for x in range(0, w, block_size):

            block = img[y:y+block_size, x:x+block_size]

            if block.size == 0:
                continue

            if block_stds[idx] > threshold:
                mask[y:y+block_size, x:x+block_size] = 1

            idx += 1

    mask = keep_largest_component(mask)
    mask  = fill_holes(mask)
    mask = add_margin(mask, margin=8)

    return mask


def keep_largest_component(mask):
    """
    Zostawia tylko największy spójny obszar (finger ROI)
    """

    h, w = mask.shape
    visited = np.zeros_like(mask)

    components = []

    def bfs(sy, sx):
        q = deque()
        q.append((sy, sx))
        comp = []

        while q:
            y, x = q.popleft()

            if y < 0 or y >= h or x < 0 or x >= w:
                continue
            if visited[y, x] or mask[y, x] == 0:
                continue

            visited[y, x] = 1
            comp.append((y, x))

            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                q.append((y+dy, x+dx))

        return comp

    for y in range(h):
        for x in range(w):
            if mask[y, x] == 1 and not visited[y, x]:
                components.append(bfs(y, x))

    if not components:
        return mask

    largest = max(components, key=len)

    clean = np.zeros_like(mask)
    for y, x in largest:
        clean[y, x] = 1

    return clean


def fill_holes(mask):
    """
    Wypełnia dziury wewnątrz największego obszaru
    """

    h, w = mask.shape

    visited = np.zeros_like(mask, dtype=np.uint8)

    q = deque()

    for x in range(w):
        if mask[0, x] == 0:
            q.append((0, x))
        if mask[h-1, x] == 0:
            q.append((h-1, x))

    for y in range(h):
        if mask[y, 0] == 0:
            q.append((y, 0))
        if mask[y, w-1] == 0:
            q.append((y, w-1))

    # =========================
    while q:
        y, x = q.popleft()

        if y < 0 or y >= h or x < 0 or x >= w:
            continue
        if visited[y, x] or mask[y, x] == 1:
            continue

        visited[y, x] = 1

        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            q.append((y+dy, x+dx))

    filled = mask.copy()

    for y in range(h):
        for x in range(w):
            if mask[y, x] == 0 and visited[y, x] == 0:
                filled[y, x] = 1

    return filled

def add_margin(mask, margin=8):
    """
    Powiększa ROI o kilka pikseli.
    Prosta dylacja bez cv2.
    """

    h, w = mask.shape

    expanded = mask.copy()

    for y in range(h):
        for x in range(w):

            if mask[y, x] == 1:

                for dy in range(-margin, margin + 1):
                    for dx in range(-margin, margin + 1):

                        ny = y + dy
                        nx = x + dx

                        if 0 <= ny < h and 0 <= nx < w:
                            expanded[ny, nx] = 1

    return expanded