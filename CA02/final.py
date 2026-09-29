import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import math

def show_images(images, titles):
    n = len(images)

    cols = min(4, n)
    rows = math.ceil(n / cols)

    plt.figure(figsize=(4 * cols, 4 * rows))

    for i, img in enumerate(images):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(img, cmap="gray")
        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()

img_path = "images/lenna.png"
img = cv.imread(img_path, 0)
height, width = img.shape
# show_images([img], ["Original Image"])

# ---

blur_depth = -1
kernel_height, kernel_width = (5, 5)

# Box Filter
box_kernel = np.ones((kernel_height, kernel_width)) / (kernel_height * kernel_width)
box_lpf = cv.filter2D(img, blur_depth, box_kernel)
# show_images([img, box_lpf], ["Original Image", "Box LPF"])

# Guassian Filter
guassian_kernel = cv.getGaussianKernel(kernel_height, 1) @ cv.getGaussianKernel(kernel_width, 1).T
guassian_lpf = cv.filter2D(img, blur_depth, guassian_kernel)
# show_images([img, guassian_lpf], ["Original Image", "Guassian LPF"])

# High Pass Filter
lpf = guassian_lpf
hpf = cv.subtract(img, lpf)
# show_images([img, hpf], ["Original Image", "HPF"])

# Unsharp Masking
boost_factor = 1
unsharped = cv.add(img, boost_factor * hpf)
# show_images([img, unsharped], ["Original Image", "Unsharp Masking"])

# High Boosted Filter
boost_factor = 2
hbf = cv.add(img, boost_factor * hpf)
hbf = np.clip(hbf, 0, 255)
# show_images([img, hbf], ["Original Image", "High Boosted Filter"])

# Low Pass Filters

F = np.fft.fftshift(np.fft.fft2(img))
u, v = np.meshgrid(np.arange(width) - width // 2, np.arange(height) - height // 2)
D = np.sqrt(u ** 2 + v ** 2)

D0 = 30
n = 2

# Ideal Mask
ideal_mask = (D <= D0)

# Butterworth Mask
butterworth_mask = 1 / (1 + (D / D0) ** (2 * n))

# Gaussian Mask
gaussian_mask = np.exp(-(D**2) / (2 * D0**2))

# Apply frequency mask
apply_mask = lambda mask: np.clip(
                            np.abs(
                                np.fft.ifft2(
                                    np.fft.ifftshift(F * mask))), 0, 255
                        )

ideal_lpf = apply_mask(ideal_mask)
butterworth_lpf = apply_mask(butterworth_mask)
gaussian_lpf = apply_mask(gaussian_mask)

# show_images(
#     [
#         ideal_mask * 255, butterworth_mask * 255, gaussian_mask * 255,
#         img, ideal_lpf, butterworth_lpf, gaussian_lpf
#     ],
#     [
#         "Ideal Mask", "Butterworth Mask", "Gaussian Mask",
#         "Original", "Ideal LPF", "Butterworth LPF", "Gaussian LPF"
#     ]
# )

# High Pass Filters
ideal_hpf = apply_mask(1 - ideal_mask)
butterworth_hpf = apply_mask(1 - butterworth_mask)
gaussian_hpf = apply_mask(1 - gaussian_mask)

# show_images(
#     [
#         (1 - ideal_mask) * 255,
#         (1 - butterworth_mask) * 255,
#         (1 - gaussian_mask) * 255,
#         img, ideal_hpf, butterworth_hpf, gaussian_hpf
#     ],
#     [
#         "Ideal HPF Mask", "Butterworth HPF Mask", "Gaussian HPF Mask",
#         "Original", "Ideal HPF", "Butterworth HPF", "Gaussian HPF"
#     ]
# )

# High Frequency Emphasis Filter
a, b = 0.5, 2

emphasis_mask = a + b * (1 - gaussian_mask)
emphasis_hpf = apply_mask(emphasis_mask)

# show_images(
#     [gaussian_mask * 255, emphasis_mask * 255, img, gaussian_hpf, emphasis_hpf],
#     ["Gaussian HPF Mask", "Emphasis Mask", "Original", "Gaussian HPF", "High Frequency Emphasis"]
# )

# Band Filters
d0_band, w = 40, 20

brf_mask = np.ones((height, width), dtype=np.float32)
brf_mask[(D >= d0_band - w / 2) & (D <= d0_band + w / 2)] = 0
brf = apply_mask(brf_mask)

bpf_mask = 1 - brf_mask
bpf = apply_mask(bpf_mask)

# show_images(
#     [brf_mask * 255, bpf_mask * 255, img, brf, bpf],
#     ["BRF Mask", "BPF Mask", "Original", "BRF", "BPF"]
# )

# Homomorphic Filter
gamma_l, gamma_h, c, d0 = 0.5, 2.0, 1, 30

img_log = np.log1p(img.astype(np.float32))
F_log = np.fft.fftshift(np.fft.fft2(img_log))

H = (gamma_h - gamma_l) * (1 - np.exp(-c * D**2 / d0**2)) + gamma_l

img_filtered = np.real(np.fft.ifft2(np.fft.ifftshift(F_log * H)))

homomorphic = np.expm1(img_filtered)
homomorphic = cv.normalize(homomorphic, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)

# show_images(
#     [H, img, homomorphic],
#     ["Homomorphic Mask", "Original", "Homomorphic Filter"]
# )

MAX_INTENSITY = 255
MIN_INTENSITY = 0
