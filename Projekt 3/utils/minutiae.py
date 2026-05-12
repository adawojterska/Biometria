import numpy as np
from utils.morphology import erode
import cv2


def crossing_number(neighbors):

    cn = 0

    for i in range(8):

        cn += abs(
            int(neighbors[i]) -
            int(neighbors[(i + 1) % 8])
        )

    return cn / 2


def detect_minutiae(skeleton, mask):

    # Pewność że skeleton ma wartości 0/1
    skeleton = (skeleton > 0).astype(np.uint8)

    rows, cols = skeleton.shape

    # =========================
    # POMNIEJSZENIE MASKI
    # =========================
    eroded_mask = mask.copy()

    eroded_mask = mask.copy()

    # Wielokrotna erozja maski 3x3
    for _ in range(15):
        eroded_mask = erode(eroded_mask)

    endings = []
    bifurcations = []


    for r in range(1, rows - 1):
        for c in range(1, cols - 1):

            # Tylko ridge
            if skeleton[r, c] != 1:
                continue

            # Pomijanie brzegu ROI
            if eroded_mask[r, c] == 0:
                continue

 
            p2 = skeleton[r - 1, c]
            p3 = skeleton[r - 1, c + 1]
            p4 = skeleton[r, c + 1]
            p5 = skeleton[r + 1, c + 1]
            p6 = skeleton[r + 1, c]
            p7 = skeleton[r + 1, c - 1]
            p8 = skeleton[r, c - 1]
            p9 = skeleton[r - 1, c - 1]

            neighbors = [
                p2, p3, p4, p5,
                p6, p7, p8, p9
            ]


            cn = crossing_number(neighbors)


            if abs(cn - 1) < 0.1:

                if np.sum(neighbors) == 1:
                    endings.append((r, c))


            # =========================
            elif abs(cn - 3) < 0.1:

                if np.sum(neighbors) >= 3:
                    bifurcations.append((r, c))

    return endings, bifurcations


def draw_minutiae(skeleton, endings, bifurcations):

    # Białe tło + czarny skeleton
    img = (255 - skeleton * 255).astype(np.uint8)

    # Konwersja do BGR
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # =========================
    # ENDINGS - CZERWONE
    # =========================
    for r, c in endings:

        cv2.circle(
            img,
            (c, r),
            3,
            (0, 0, 255),
            -1
        )

    # =========================
    # BIFURCATIONS - NIEBIESKIE
    # =========================
    for r, c in bifurcations:

        cv2.circle(
            img,
            (c, r),
            3,
            (255, 0, 0),
            -1
        )

    return img