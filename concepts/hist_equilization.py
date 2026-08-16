import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

img = cv.imread("../images/lenna.png", 0)
height, width = img.shape

hist, bins = np.histogram(img.flatten(), bins=256, range=[0, 256])

cdf = hist.cumsum()

cdf_min = cdf[cdf > 0].min()

N = cdf.max()

equalized = ((cdf - cdf_min) / (N - cdf_min) * 255).astype(np.uint8)

result = equalized[img]

cv.imshow("Original", img)
cv.imshow("Equalized", result)

cv.waitKey(0)
cv.destroyAllWindows()

plt.hist(img.ravel(), bins=256, range=[0, 256])
plt.title("Original")
plt.show()

plt.hist(equalized.ravel(), bins=256, range=[0, 256])
plt.title("Equalized")
plt.show()
