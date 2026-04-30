import numpy as np

# PROJEKCJE 
def projection_x(img):
    return np.sum(img == 255, axis=0) #liczy biale w kazdej kolumnie

def projection_y(img):
    return np.sum(img == 255, axis=1) #liczy biale w kazdym wierszu


def find_radius(img, cx, cy):
    h, w = img.shape
    max_r = min(h, w) // 2

    for r in range(1, max_r):
        points = 0
        white = 0

        for angle in range(0, 360, 1):
            x = int(cx + r * np.cos(np.deg2rad(angle)))
            y = int(cy + r * np.sin(np.deg2rad(angle)))

            if 0 <= x < w and 0 <= y < h:
                points += 1
                if img[y, x] == 255:
                    white += 1

        if points == 0:
            continue

        ratio = white / points

        if ratio < 0.4:
            return r

    return max_r

def get_center_at_angle(img, angle_deg):
    h, w = img.shape
    # pobieramy współrzędne wszystkich białych pikseli
    y_indices, x_indices = np.where(img == 255)
    
    if len(x_indices) == 0:
        return None

    alpha = np.deg2rad(angle_deg)
    
    # rzutujemy punkty na nowe osie obrócone o kąt alpha
    # x_prime to rzut pionowy pod kątem, y_prime to rzut poziomy pod kątem
    x_prime = x_indices * np.cos(alpha) + y_indices * np.sin(alpha)
    y_prime = -x_indices * np.sin(alpha) + y_indices * np.cos(alpha)
    
    #szukamy środkowej wartości rzutów punktów w obróconym układzie.
    #mediana wyznacza środek rozkładu i jest odporna na szum oraz odstające piksele.
    peak_x_prime = np.median(x_prime)
    peak_y_prime = np.median(y_prime)
    
    #cofamy obrót- wracamy z układu obróconego do normalnego
    cx = peak_x_prime * np.cos(-alpha) + peak_y_prime * np.sin(-alpha)
    cy = -peak_x_prime * np.sin(-alpha) + peak_y_prime * np.cos(-alpha)
    
    return cx, cy

def find_center(img):
    if not np.any(img == 255):
        return 130, 90 # Domyślny środek dla obrazka 260x180

    # zbieramy kandydatów na środek z różnych kątów
    angles = [0, 30, 60, 90]
    results_x = []
    results_y = []

    for a in angles:
        res = get_center_at_angle(img, a)
        if res:
            results_x.append(res[0])
            results_y.append(res[1])

    # Ostateczny środek to średnia z przecięć wszystkich par projekcji
    cx = int(np.mean(results_x))
    cy = int(np.mean(results_y))

    return cx, cy