import cv2
import numpy as np
from math import sqrt


def find_endpoints(skeleton):

    endpoints = []

    rows, cols = skeleton.shape

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):

            if skeleton[r, c] == 1:

                neighbors = []

                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:

                        if dy == 0 and dx == 0:
                            continue

                        if skeleton[r + dy, c + dx] == 1:
                            neighbors.append((r + dy, c + dx))

                if len(neighbors) == 1:
                    endpoints.append((r, c, neighbors[0]))

    return endpoints


def reconnect_lines(skeleton, max_distance=8):

    repaired = skeleton.copy()

    endpoints = find_endpoints(repaired)

    for i in range(len(endpoints)):

        y1, x1, n1 = endpoints[i]

        dy1 = y1 - n1[0]
        dx1 = x1 - n1[1]

        for j in range(i + 1, len(endpoints)):

            y2, x2, n2 = endpoints[j]

            dy2 = y2 - n2[0]
            dx2 = x2 - n2[1]

            dist = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if dist > max_distance:
                continue

            # wektor między endpointami
            vx = x2 - x1
            vy = y2 - y1

            v_len = sqrt(vx * vx + vy * vy)

            if v_len == 0:
                continue

            # normalizacja
            vx /= v_len
            vy /= v_len

            d1_len = sqrt(dx1 * dx1 + dy1 * dy1)
            d2_len = sqrt(dx2 * dx2 + dy2 * dy2)

            if d1_len == 0 or d2_len == 0:
                continue

            dx1n = dx1 / d1_len
            dy1n = dy1 / d1_len

            dx2n = dx2 / d2_len
            dy2n = dy2 / d2_len

            # zgodność kierunku
            dot1 = dx1n * vx + dy1n * vy
            dot2 = -(dx2n * vx + dy2n * vy)

            if dot1 > 0.8 and dot2 > 0.8:

                cv2.line(
                    repaired,
                    (x1, y1),
                    (x2, y2),
                    1,
                    1
                )

    return repaired