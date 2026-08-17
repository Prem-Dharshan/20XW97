import cv2 as cv
import numpy as np

img = cv.imread("../images/shapes/horseshoe.jpg", 0)
_, img = cv.threshold(img, 128, 255, cv.THRESH_BINARY_INV)


pad = np.zeros((img.shape[0] + 1, img.shape[1] + 1), dtype=img.dtype)
pad[1:, 1:] = img

h, w = pad.shape
label = np.zeros((h, w), dtype=np.int32)
count = 1

for i in range(1, h):
    for j in range(1, w):

        A = pad[i, j]
        if A == 0:
            continue

        B = pad[i, j - 1]  # West
        C = pad[i - 1, j]  # North

        B_label = label[i, j - 1]
        C_label = label[i - 1, j]

        if A != B and A != C:
            A_label = count
            count += 1

        elif A == B and A != C:
            A_label = B_label

        elif A != B and A == C:
            A_label = C_label

        else:
            if B_label == C_label:
                A_label = B_label
            else:
                label[label == C_label] = B_label
                A_label = B_label

        label[i, j] = A_label

label = label[1:, 1:]

ids = np.unique(label)
ids = ids[ids != 0]

print("Labels created:", count - 1)
print("Number of components:", len(ids))

vis = (label.astype(np.float32) / max(label.max(), 1) * 255).astype(np.uint8)
cv.imshow("Binary Image", img)
cv.imshow("Labels", vis)

cv.waitKey(0)
cv.destroyAllWindows()
