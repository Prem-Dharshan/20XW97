import cv2 as cv
import numpy as np

img_path = "../images/lenna.png"
img = cv.imread(img_path, 0)

height, width = img.shape[:2]

density_sliced_img = np.zeros_like(img)

for i in range(height):
    for j in range(width):

        if img[i, j] < 50:
            density_sliced_img[i, j] = 0

        elif img[i, j] < 100:
            density_sliced_img[i, j] = 60

        elif img[i, j] < 150:
            density_sliced_img[i, j] = 120

        elif img[i, j] < 200:
            density_sliced_img[i, j] = 180

        else:
            density_sliced_img[i, j] = 255


cv.imshow("Original", img)
cv.imshow("Density Sliced", density_sliced_img)

cv.waitKey(0)
cv.destroyAllWindows()
