import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew, entropy
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops


def display_images(images, columns=2, figsize=(8, 10)):
    rows = (len(images) + columns - 1) // columns
    plt.figure(figsize=figsize)

    for i, (title, image) in enumerate(images.items(), start=1):
        plt.subplot(rows, columns, i)
        plt.imshow(image, cmap="gray")
        plt.title(title)
        plt.axis("off")

    plt.tight_layout()
    plt.show()

img = cv.imread("../images/building.jpg")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

images = {"Original": cv.cvtColor(img, cv.COLOR_BGR2RGB), "Grayscale": gray}
display_images(images, columns=2, figsize=(10, 4))

small = cv.resize(gray, (64, 64))
raw_feature = small.flatten()
print("Raw feature dimension:", raw_feature.shape)

hist = cv.calcHist([gray], [0], None, [256], [0, 256]).ravel()
hist_norm = hist / hist.sum()
stats = [gray.mean(), gray.std(), skew(gray.ravel()), entropy(hist_norm + 1e-12)]
print("Mean, Std, Skewness, Entropy:", stats)

eq = cv.equalizeHist(gray)
images = {"Original": gray, "Equalized": eq}
display_images(images, columns=2, figsize=(10, 4))

plt.figure(figsize=(10, 4))
for i, (title, image) in enumerate(images.items(), start=1):
    plt.subplot(1, 2, i)
    plt.hist(image.ravel(), bins=256, range=(0, 256))
    plt.title(title)

plt.tight_layout()
plt.show()

hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
h = cv.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
h = cv.normalize(h, h).flatten()

def color_moments(image):
    feats = []
    for c in cv.split(image):
        c = c.astype(float).ravel()
        feats += [c.mean(), c.std(), skew(c)]
    return np.array(feats)


print(color_moments(hsv))

bright = cv.convertScaleAbs(img, alpha=1, beta=50)
h1 = cv.calcHist([img], [0], None, [64], [0, 256])
h2 = cv.calcHist([bright], [0], None, [64], [0, 256])
for name, m in [
    ("Correlation", cv.HISTCMP_CORREL),
    ("Chi-square", cv.HISTCMP_CHISQR),
    ("Intersection", cv.HISTCMP_INTERSECT),
    ("Bhattacharyya", cv.HISTCMP_BHATTACHARYYA),
]:
    print(name, cv.compareHist(h1, h2, m))

blur = cv.GaussianBlur(gray, (5, 5), 1.4)
gx = cv.Sobel(blur, cv.CV_64F, 1, 0, ksize=3)
gy = cv.Sobel(blur, cv.CV_64F, 0, 1, ksize=3)
mag = np.sqrt(gx**2 + gy**2)
ang = np.degrees(np.arctan2(gy, gx)) % 180

lap = cv.Laplacian(blur, cv.CV_64F)
canny = cv.Canny(blur, 100, 200)

orient_hist, _ = np.histogram(ang, bins=9, range=(0, 180), weights=mag)
print("Edge orientation histogram:", orient_hist / max(orient_hist.sum(), 1e-12))

images = {
    "Original": gray,
    "Sobel X": np.abs(gx),
    "Sobel Y": np.abs(gy),
    "Magnitude": mag,
    "Laplacian": np.abs(lap),
    "Canny": canny,
}
display_images(images, columns=3, figsize=(12, 8))

_, bw = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
contours, _ = cv.findContours(bw, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

for c in contours:
    area = cv.contourArea(c)
    if area < 100:
        continue
    perim = cv.arcLength(c, True)
    x, y, w, h = cv.boundingRect(c)
    hull_area = cv.contourArea(cv.convexHull(c))
    circularity = 4 * np.pi * area / (perim**2)
    extent = area / (w * h)
    solidity = area / hull_area
    hu = cv.HuMoments(cv.moments(c)).flatten()
    hu_log = -np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    print("Area, perimeter, aspect ratio, extent, circularity, solidity:")
    print(area, perim, w / h, extent, circularity, solidity)
    print("Hu moments (log):", hu_log)

contourImage = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)
cv.drawContours(contourImage, contours, -1, (0, 255, 0), 2)
display_images({"Binary": bw, "Contours": contourImage}, columns=2, figsize=(10, 4))

P, R = 8, 1
lbp = local_binary_pattern(gray, P, R, method="uniform")
lbp_hist, _ = np.histogram(lbp, bins=P + 2, range=(0, P + 2), density=True)


print("LBP histogram:", lbp_hist)

glcm = graycomatrix(
    gray,
    distances=[1, 3],
    angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
    levels=256,
    symmetric=True,
    normed=True,
)
for prop in ["contrast", "correlation", "energy", "homogeneity"]:
    print(prop, graycoprops(glcm, prop).mean())

display_images({"Original": gray, "LBP": lbp}, columns=2, figsize=(10, 4))

harris = cv.cornerHarris(np.float32(gray), blockSize=2, ksize=3, k=0.04)
harris_pts = np.argwhere(harris > 0.01 * harris.max())

shi = cv.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)

fast = cv.FastFeatureDetector_create(threshold=30)
fast_kp = fast.detect(gray, None)
print("Harris response pixels:", len(harris_pts))
print("Shi-Tomasi corners:", 0 if shi is None else len(shi))
print("FAST keypoints:", len(fast_kp))

harrisImage = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)
harrisImage[harris > 0.01 * harris.max()] = [255, 0, 0]

shiImage = cv.cvtColor(gray, cv.COLOR_GRAY2RGB)
if shi is not None:
    for point in shi:
        x, y = point.ravel().astype(int)
        cv.circle(shiImage, (x, y), 3, (0, 255, 0), -1)

fastImage = cv.drawKeypoints(gray, fast_kp, None, color=(0, 255, 0))
images = {"Harris": harrisImage, "Shi-Tomasi": shiImage, "FAST": fastImage}
display_images(images, columns=3, figsize=(12, 4))
