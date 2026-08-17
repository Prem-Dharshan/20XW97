import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

img = cv.imread("../images/lenna.png", 0)
ref = cv.imread("../images/DISC.png", 0)


def get_cdf(image):

    hist, _ = np.histogram(image.flatten(), bins=256, range=[0, 256])
    cdf = hist.cumsum()
    cdf = cdf / cdf[-1]

    return cdf


src_cdf = get_cdf(img)
ref_cdf = get_cdf(ref)

# For every source gray level, find the reference gray level
# whose CDF is closest to the source's CDF value

mapping = np.zeros(256, dtype=np.uint8)

for src_val in range(256):

    diff = np.abs(ref_cdf - src_cdf[src_val])
    mapping[src_val] = np.argmin(diff)

matched = mapping[img]

cv.imshow("Source", img)
cv.imshow("Reference", ref)
cv.imshow("Matched", matched)

cv.waitKey(0)
cv.destroyAllWindows()

plt.hist(img.ravel(), bins=256, range=[0, 256])
plt.title("Source")
plt.show()

plt.hist(ref.ravel(), bins=256, range=[0, 256])
plt.title("Reference")
plt.show()

plt.hist(matched.ravel(), bins=256, range=[0, 256])
plt.title("Matched")
plt.show()
