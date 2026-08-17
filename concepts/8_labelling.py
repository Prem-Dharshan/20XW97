import cv2 as cv
import numpy as np

img = cv.imread("../images/shapes/horseshoe.jpg", 0)
_, img = cv.threshold(img, 128, 255, cv.THRESH_BINARY_INV)


pad = np.zeros((img.shape[0] + 1, img.shape[1] + 2), dtype=img.dtype)
pad[1:, 1:-1] = img

h, w = pad.shape
label = np.zeros((h, w), dtype=np.int32)
count = 1

for i in range(1, h):
    for j in range(1, w - 1):

        A = pad[i, j]
        if A == 0:
            continue

        NW = pad[i - 1, j - 1]
        N = pad[i - 1, j]
        NE = pad[i - 1, j + 1]
        W = pad[i, j - 1]

        NW_label = label[i - 1, j - 1]
        N_label = label[i - 1, j]
        NE_label = label[i - 1, j + 1]
        W_label = label[i, j - 1]

        neighbours = set()

        if A == NW:
            neighbours.add(NW_label)
        if A == N:
            neighbours.add(N_label)
        if A == NE:
            neighbours.add(NE_label)
        if A == W:
            neighbours.add(W_label)

        if not neighbours:
            A_label = count
            count += 1
        else:
            A_label = min(neighbours)
            for lbl in neighbours:
                if lbl != A_label:
                    label[label == lbl] = A_label

        label[i, j] = A_label

label = label[1:, 1:-1]

ids = np.unique(label)
ids = ids[ids != 0]

print("Labels created:", count - 1)
print("Number of components:", len(ids))

vis = (label.astype(np.float32) / max(label.max(), 1) * 255).astype(np.uint8)
cv.imshow("Binary Image", img)
cv.imshow("Labels", vis)

cv.waitKey(0)
cv.destroyAllWindows()
