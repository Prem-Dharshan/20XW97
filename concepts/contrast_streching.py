import cv2 as cv
import numpy as np

img = cv.imread("../images/lenna.png", 0)

minimum = 50
maximum = 200

clipped = img.copy()

height, width = img.shape

L = 50
M = 200
Imin = np.min(img)
Imax = np.max(img)

contrast = img.copy()

for i in range(height):
    for j in range(width):

        if contrast[i, j] <= L: contrast[i, j] = L

        if L <= contrast[i, j] <= M: ((Imax - Imin) / (M - L) * (contrast[i, j] - L) + Imin)

        else:
            contrast[i, j] = M


cv.imshow("Original", img)
cv.imshow("Contrast Stretched", contrast)

cv.waitKey(0)
cv.destroyAllWindows()