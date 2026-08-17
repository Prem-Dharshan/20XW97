import cv2 as cv
import numpy as np

img = cv.imread("../images/lenna.png", 0)
height, width = img.shape


# 1. Global (single) thresholding

T = 128

global_thresh = np.zeros_like(img)

for i in range(height):
    for j in range(width):

        if img[i, j] > T:
            global_thresh[i, j] = 255
        else:
            global_thresh[i, j] = 0


# 2. Band (double) thresholding

low = 80
high = 180

band_thresh = np.zeros_like(img)

for i in range(height):
    for j in range(width):

        if low <= img[i, j] <= high:
            band_thresh[i, j] = 255
        else:
            band_thresh[i, j] = 0


# 3. Adaptive (mean) thresholding

block = 15
half = block // 2
C = 5

padded = np.pad(img, half, mode="reflect")
adaptive_thresh = np.zeros_like(img)

for i in range(height):
    for j in range(width):

        window = padded[i : i + block, j : j + block]
        local_mean = window.mean()

        if img[i, j] > local_mean - C:
            adaptive_thresh[i, j] = 255
        else:
            adaptive_thresh[i, j] = 0


# Display

cv.imshow("Original", img)
cv.imshow("Global Threshold", global_thresh)
cv.imshow("Band Threshold", band_thresh)
cv.imshow("Adaptive Threshold", adaptive_thresh)

# Reference (OpenCV)
_, ref_global = cv.threshold(img, T, 255, cv.THRESH_BINARY)
ref_adaptive = cv.adaptiveThreshold(
    img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, block, C
)
cv.imshow("Global Threshold (cv)", ref_global)
cv.imshow("Adaptive Threshold (cv)", ref_adaptive)

cv.waitKey(0)
cv.destroyAllWindows()
