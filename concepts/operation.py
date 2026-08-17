# Arithmetic and Logical

import cv2 as cv
import numpy as np

img1 = cv.imread("../images/lenna.png", 0)
img2 = cv.imread("../images/DISC.png", 0)
img2 = cv.resize(img2, (img1.shape[1], img1.shape[0]))

height, width = img1.shape


# Arithmetic operations

addition = np.zeros_like(img1)
subtraction = np.zeros_like(img1)
multiplication = np.zeros_like(img1)
division = np.zeros_like(img1)

for i in range(height):
    for j in range(width):

        a = int(img1[i, j])
        b = int(img2[i, j])

        addition[i, j] = min(a + b, 255)
        subtraction[i, j] = max(a - b, 0)
        multiplication[i, j] = min(a * b, 255)
        division[i, j] = a // b if b != 0 else 0


# Logical operations (on binarized images)

_, bin1 = cv.threshold(img1, 128, 255, cv.THRESH_BINARY)
_, bin2 = cv.threshold(img2, 128, 255, cv.THRESH_BINARY)

AND = np.zeros_like(img1)
OR = np.zeros_like(img1)
XOR = np.zeros_like(img1)
NOT = np.zeros_like(img1)

for i in range(height):
    for j in range(width):

        a = bin1[i, j] > 0
        b = bin2[i, j] > 0

        AND[i, j] = 255 if (a and b) else 0
        OR[i, j] = 255 if (a or b) else 0
        XOR[i, j] = 255 if (a != b) else 0
        NOT[i, j] = 255 if not a else 0


# Display

cv.imshow("Image 1", img1)
cv.imshow("Image 2", img2)

cv.imshow("Addition", addition)
cv.imshow("Subtraction", subtraction)
cv.imshow("Multiplication", multiplication)
cv.imshow("Division", division)

cv.imshow("AND", AND)
cv.imshow("OR", OR)
cv.imshow("XOR", XOR)
cv.imshow("NOT", NOT)

cv.waitKey(0)
cv.destroyAllWindows()
