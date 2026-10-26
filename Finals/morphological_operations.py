import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

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

binary = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
], dtype=np.uint8)

kernelName = "cross"
kernelSizes = [(3, 3), (5, 5), (7, 7)]
iterations = range(1, 4)
selectedKernelsBySize = {}

for kernelSize in kernelSizes:
    width, height = kernelSize

    kernels = {
        "rect": cv.getStructuringElement(cv.MORPH_RECT, kernelSize),
        "cross": cv.getStructuringElement(cv.MORPH_CROSS, kernelSize),
        "ellipse": cv.getStructuringElement(cv.MORPH_ELLIPSE, kernelSize),
        "diagonal": np.eye(height, width, dtype=np.uint8),
        "antiDiagonal": np.fliplr(np.eye(height, width, dtype=np.uint8)).copy(),
        "hitmiss": np.array([[-1, -1, -1], [0, 1, 0], [1, 1, 1]], dtype=np.int8)
    }

    selectedKernelsBySize[kernelSize] = kernels[kernelName]

kernel = selectedKernelsBySize[kernelSizes[0]]

images = {"Original": binary}

for iteration in iterations:
    eroded = cv.erode(binary, kernel, iterations=iteration)
    images[f"Erosion: {iteration}"] = eroded

display_images(images, columns=4, figsize=(16, 4))

images = {"Original": binary}

for iteration in iterations:
    dilated = cv.dilate(binary, kernel, iterations=iteration)
    images[f"Dilation: {iteration}"] = dilated

display_images(images, columns=4, figsize=(16, 4))

images = {"Original": binary}

for kernelSize, sizeKernel in selectedKernelsBySize.items():
    opening = cv.morphologyEx(binary, cv.MORPH_OPEN, sizeKernel)
    images[f"Opening: {kernelSize}"] = opening

display_images(images, columns=4, figsize=(16, 4))

images = {"Original": binary}

for kernelSize, sizeKernel in selectedKernelsBySize.items():
    closing = cv.morphologyEx(binary, cv.MORPH_CLOSE, sizeKernel)
    images[f"Closing: {kernelSize}"] = closing

display_images(images, columns=4, figsize=(16, 4))

hitmissKernel = kernels["hitmiss"]
hitmiss = cv.morphologyEx(binary, cv.MORPH_HITMISS, hitmissKernel)

display_images({"Original": binary, "Hit-or-miss": hitmiss}, columns=2, figsize=(8, 4))

eroded = cv.erode(binary, kernel)
dilated = cv.dilate(binary, kernel)

innerBoundary = cv.subtract(binary, eroded)
outerBoundary = cv.subtract(dilated, binary)

display_images({"Original": binary, "Inner boundary": innerBoundary, "Outer boundary": outerBoundary}, columns=3, figsize=(12, 4))

contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
filled = np.zeros_like(binary)

cv.drawContours(filled, contours, -1, 1, cv.FILLED)

display_images({"Original": binary, "Region filled": filled}, columns=2, figsize=(8, 4))

convexHullImage = np.zeros_like(binary)

for contour in contours:
    hull = cv.convexHull(contour)
    cv.drawContours(convexHullImage, [hull], -1, 1, cv.FILLED)

display_images({"Original": binary, "Convex hull": convexHullImage}, columns=2, figsize=(8, 4))

if hasattr(cv, "ximgproc") and hasattr(cv.ximgproc, "thinning"):
    thinning = cv.ximgproc.thinning(binary * 255)
    display_images({"Original": binary, "Thinning": thinning}, columns=2, figsize=(8, 4))
else:
    print("Thinning requires opencv-contrib-python.")

thickening = cv.dilate(binary, kernel)

display_images({"Original": binary, "Thickening (dilation)": thickening}, columns=2, figsize=(8, 4))

watershedBinary = binary * 255
watershedOpening = cv.morphologyEx(watershedBinary, cv.MORPH_OPEN, kernel)
sureBackground = cv.dilate(watershedOpening, kernel, iterations=3)

distance = cv.distanceTransform(watershedOpening, cv.DIST_L2, 5)
sureForeground = np.uint8(distance > 0.5 * distance.max()) * 255
unknown = cv.subtract(sureBackground, sureForeground)

_, markers = cv.connectedComponents(sureForeground)
markers += 1
markers[unknown == 255] = 0

watershedImage = cv.cvtColor(watershedBinary, cv.COLOR_GRAY2RGB)
markers = cv.watershed(watershedImage, markers)
watershedImage[markers == -1] = [255, 0, 0]

display_images({"Original": binary, "Watershed": watershedImage}, columns=2, figsize=(8, 4))
