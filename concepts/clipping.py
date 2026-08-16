import cv2 as cv
import numpy as np

img = cv.imread("../images/lenna.png", 0)

minimum = 50
maximum = 200

clipped = img.copy()

height, width = img.shape

for i in range(height):
    for j in range(width):

        if img[i, j] < minimum:
            clipped[i, j] = minimum

        elif img[i, j] > maximum:
            clipped[i, j] = maximum

        else:
            clipped[i, j] = img[i, j]


cv.imshow("Original", img)
cv.imshow("Clipped", clipped)

img += 100  # Brighter
clipped = np.clip(img, 50, 200)
cv.imshow("Clipped (np)", clipped)

cv.waitKey(0)
cv.destroyAllWindows()