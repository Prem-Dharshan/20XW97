import cv2 as cv
import numpy as np

img = cv.imread("../images/lenna.png")

height, width = img.shape[:2]


# 1. Spatial quantization by scale

scale = 0.5

spatial_scale = cv.resize(img, None, fx=scale, fy=scale)


# 2. Spatial quantization by width and height

new_width = 128
new_height = 128

spatial_wh = cv.resize(img, (new_width, new_height))


# 3. Spatial quantization by power

n = 2
factor = 2**n

spatial_power = img[::factor, ::factor]


# 4. Gray-level quantization

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

bits = 3

gray_quantized = (gray >> (8 - bits)) << (8 - bits)


# 5. Color quantization

bits = 2

color_quantized = (img >> (8 - bits)) << (8 - bits)


# Display

cv.imshow("Original", img)

cv.imshow("Spatial - Scale", spatial_scale)
cv.imshow("Spatial - Width Height", spatial_wh)
cv.imshow("Spatial - Power", spatial_power)

cv.imshow("Gray Quantization", gray_quantized)
cv.imshow("Color Quantization", color_quantized)

cv.waitKey(0)
cv.destroyAllWindows()
