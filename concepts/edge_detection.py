import cv2 as cv
import numpy as np

img = cv.imread("../images/lenna.png", 0)
height, width = img.shape

# SOBEL
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

# PREWITT
prewitt_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
prewitt_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])

# ROBERTS
roberts_x = np.array([[1, 0], [0, -1]])
roberts_y = np.array([[0, 1], [-1, 0]])

# LAPLACIAN
laplacian_4 = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
laplacian_8 = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])


def apply_3x3(img, kernel_x, kernel_y=None):

    height, width = img.shape

    padded = np.pad(img, 1, mode="constant").astype(np.float32)
    result = np.zeros((height, width), dtype=np.float32)

    for i in range(height):
        for j in range(width):

            mask = padded[i : i + 3, j : j + 3]

            if kernel_y is None:
                # Laplacian
                result[i, j] = np.sum(mask * kernel_x)
            else:
                # Sobel / Prewitt
                gx = np.sum(mask * kernel_x)
                gy = np.sum(mask * kernel_y)
                result[i, j] = np.sqrt(gx**2 + gy**2)

    magnitude = np.abs(result)
    magnitude = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)

    return magnitude.astype(np.uint8)


def apply_2x2(img, kernel_x, kernel_y):

    height, width = img.shape

    padded = np.pad(img, ((0, 1), (0, 1)), mode="constant").astype(np.float32)

    gx = np.zeros((height, width), dtype=np.float32)
    gy = np.zeros((height, width), dtype=np.float32)

    for i in range(height):
        for j in range(width):
            mask = padded[i : i + 2, j : j + 2]
            gx[i, j] = np.sum(mask * kernel_x)
            gy[i, j] = np.sum(mask * kernel_y)

    magnitude = np.sqrt(gx**2 + gy**2)
    magnitude = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)

    return magnitude.astype(np.uint8)


# Apply filters
sobel = apply_3x3(img, sobel_x, sobel_y)
prewitt = apply_3x3(img, prewitt_x, prewitt_y)
roberts = apply_2x2(img, roberts_x, roberts_y)

laplacian4 = apply_3x3(img, laplacian_4)
laplacian8 = apply_3x3(img, laplacian_8)

# Display
cv.imshow("Original", img)

cv.imshow("Sobel", sobel)
cv.imshow("Prewitt", prewitt)
cv.imshow("Roberts", roberts)

cv.imshow("Laplacian 4-Neighbour", laplacian4)
cv.imshow("Laplacian 8-Neighbour", laplacian8)

cv.waitKey(0)
cv.destroyAllWindows()

# Default OpenCV functions

# sobel_x = cv.Sobel(img, cv.CV_64F, 1, 0, 3)
# sobel_y = cv.Sobel(img, cv.CV_64F, 0, 1, 3)
# sobel = cv.convertScaleAbs(cv.magnitude(sobel_x, sobel_y))

# px = cv.filter2D(img, cv.CV_64F, prewitt_x)
# py = cv.filter2D(img, cv.CV_64F, prewitt_y)
# prewitt = cv.convertScaleAbs(cv.magnitude(px, py))

# rx = cv.filter2D(img, cv.CV_64F, roberts_x)
# ry = cv.filter2D(img, cv.CV_64F, roberts_y)
# roberts = cv.convertScaleAbs(cv.magnitude(rx, ry))

# laplacian = cv.Laplacian(img, cv.CV_64F)
# laplacian = cv.convertScaleAbs(laplacian)
