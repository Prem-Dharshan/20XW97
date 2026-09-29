import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import math

# Learning order (each section builds on the ones before it):
#   0. Setup                     -> image, shared helpers
#   1. Spatial Filtering         -> kernels, smoothing (LPF), sharpening (HPF = img - LPF)
#   2. Frequency Domain Filters  -> same LPF / HPF ideas, but as masks on the FFT
#   3. Noise Models              -> what corrupts an image
#   4. Denoising                 -> spatial (1) + frequency (2) filters used to remove noise (3)
#   5. Degradation (Blur) Models -> PSF / H that blurs an image (G = F * H)
#   6. Restoration               -> undo H: inverse -> pseudo-inverse -> Wiener

# ============================================================
# 0. SETUP
# ============================================================

def show_images(images, titles):
    n = len(images)

    cols = min(4, n)
    rows = math.ceil(n / cols)

    plt.figure(figsize=(4 * cols, 4 * rows))

    for i, image in enumerate(images):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(image, cmap="gray")
        plt.title(titles[i])
        plt.axis("off")

    plt.tight_layout()
    plt.show()

img_path = "images/lenna.png"
img = cv.imread(img_path, 0)
height, width = img.shape
# show_images([img], ["Original Image"])

MIN_INTENSITY, MAX_INTENSITY = 0, 255
ddepth = -1  # output keeps the input's depth (uint8 in -> uint8 out)

# Clip - keeps pixel values inside the valid [0, 255] range
clip = lambda x: np.clip(x, MIN_INTENSITY, MAX_INTENSITY)

# ============================================================
# 1. SPATIAL FILTERING
# ============================================================

# --- 1.1 Smoothing (Low Pass) ---

kernel_size = 5  # larger kernel -> averages over a wider area, stronger blur
sigma = 1        # larger sigma -> Gaussian weights spread out, stronger blur

# Box Filter - replaces each pixel with the plain average of its k x k neighbourhood
# Formula: K = (1 / k^2) * ones(k, k)
box_kernel = lambda k: np.ones((k, k)) / (k * k)
box_smooth = cv.filter2D(img, ddepth, box_kernel(kernel_size))
# show_images([img, box_smooth], ["Original Image", "Box LPF"])

# Gaussian Filter - weighted average, closer neighbours count more
# Formula: G(x, y) = exp(-(x^2 + y^2) / (2 * sigma^2)), normalised to sum 1
gaussian_kernel = cv.getGaussianKernel(kernel_size, sigma) @ cv.getGaussianKernel(kernel_size, sigma).T
gaussian_smooth = cv.filter2D(img, ddepth, gaussian_kernel)
# show_images([img, gaussian_smooth], ["Original Image", "Gaussian LPF"])

# --- 1.2 Sharpening (High Pass = Original - Low Pass) ---

# High Pass Filter - keeps only edges / fine detail that smoothing removed
# Formula: hpf = img - lpf
hpf = cv.subtract(img, gaussian_smooth)
# show_images([img, hpf], ["Original Image", "HPF"])

# Sharpen - adds the scaled detail back onto the image
# Formula: g = img + k * (img - lpf)
sharpen = lambda k: clip(img + k * hpf.astype(float))

# Unsharp Masking - sharpen with k = 1
unsharped = sharpen(1)  # k = 1 -> detail added back once
# show_images([img, unsharped], ["Original Image", "Unsharp Masking"])

# High Boost Filter - sharpen with k > 1
hbf = sharpen(2)        # larger k -> edges exaggerated more strongly
# show_images([img, hbf], ["Original Image", "High Boosted Filter"])

# ============================================================
# 2. FREQUENCY DOMAIN FILTERING
# ============================================================

# --- 2.0 FFT setup (used by every frequency-domain section below) ---

# To Frequency - centred spectrum of an image
# Formula: F(u, v) = fftshift(FFT2(f))
to_freq = lambda image: np.fft.fftshift(np.fft.fft2(image))

# To Spatial - back from a centred spectrum to an image
# Formula: f = |IFFT2(ifftshift(F))|
to_spatial = lambda spectrum: np.abs(np.fft.ifft2(np.fft.ifftshift(spectrum)))

F = to_freq(img)

# Distance of every frequency from the centre
# Formula: D(u, v) = sqrt(u^2 + v^2)
u, v = np.meshgrid(np.arange(width) - width // 2, np.arange(height) - height // 2)
D = np.sqrt(u ** 2 + v ** 2)

# Apply Mask - filters a spectrum with mask H and returns the image
# Formula: g = IFFT(F * H)
apply_mask = lambda mask, spectrum=F: clip(to_spatial(spectrum * mask))

# --- 2.1 Low Pass Filters ---

D0 = 30  # larger cutoff -> more frequencies pass, less blur
n = 2    # larger order -> sharper Butterworth cutoff (closer to Ideal, more ringing)

# Ideal LPF - passes everything inside radius D0, cuts the rest (causes ringing)
# Formula: H = 1 if D <= D0 else 0
ideal_mask = (D <= D0)

# Butterworth LPF - smooth roll-off controlled by order n
# Formula: H = 1 / (1 + (D / D0)^(2n))
butterworth_mask = 1 / (1 + (D / D0) ** (2 * n))

# Gaussian LPF - smoothest roll-off, no ringing
# Formula: H = exp(-D^2 / (2 * D0^2))
gaussian_H = lambda cutoff: np.exp(-(D ** 2) / (2 * cutoff ** 2))
gaussian_mask = gaussian_H(D0)

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

# --- 2.2 High Pass Filters ---

# HPF - the complement of each LPF, keeps edges and removes flat regions
# Formula: H_hp = 1 - H_lp
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

# --- 2.3 High Frequency Emphasis Filter ---

a = 0.5  # offset -> how much of the original (low frequencies) is kept
b = 2    # multiplier -> how strongly edges / high frequencies are boosted

# High Frequency Emphasis - sharpens edges while keeping the background
# Formula: H = a + b * H_hp
emphasis_mask = a + b * (1 - gaussian_mask)
emphasis_hpf = apply_mask(emphasis_mask)

# show_images(
#     [gaussian_mask * 255, emphasis_mask * 255, img, gaussian_hpf, emphasis_hpf],
#     ["Gaussian Mask", "Emphasis Mask", "Original", "Gaussian HPF", "High Frequency Emphasis"]
# )

# --- 2.4 Band Filters ---

d0_band = 40     # centre radius of the band -> which frequency ring is targeted
band_width = 20  # wider band -> more frequencies removed / kept

# Band Reject - removes a ring of frequencies (e.g. periodic noise)
# Formula: H = 0 if D0 - W/2 <= D <= D0 + W/2 else 1
brf_mask = np.ones((height, width), dtype=np.float32)
brf_mask[(D >= d0_band - band_width / 2) & (D <= d0_band + band_width / 2)] = 0
brf = apply_mask(brf_mask)

# Band Pass - keeps only that ring of frequencies
# Formula: H_bp = 1 - H_br
bpf_mask = 1 - brf_mask
bpf = apply_mask(bpf_mask)

# show_images(
#     [brf_mask * 255, bpf_mask * 255, img, brf, bpf],
#     ["BRF Mask", "BPF Mask", "Original", "BRF", "BPF"]
# )

# --- 2.5 Homomorphic Filter ---

gamma_l = 0.5  # < 1 -> suppresses illumination (low frequencies), evens out lighting
gamma_h = 2.0  # > 1 -> boosts reflectance (high frequencies), enhances contrast / detail
c = 1          # sharpness of the transition between gamma_l and gamma_h
d0 = 30        # cutoff separating illumination from reflectance

# Homomorphic - separates illumination and reflectance via log, then fixes lighting
# Formula: H = (gamma_h - gamma_l) * (1 - exp(-c * D^2 / D0^2)) + gamma_l
#          g = exp(IFFT(H * FFT(ln(1 + f)))) - 1
F_log = to_freq(np.log1p(img.astype(np.float32)))

H_homomorphic = (gamma_h - gamma_l) * (1 - np.exp(-c * D**2 / d0**2)) + gamma_l

img_filtered = np.real(np.fft.ifft2(np.fft.ifftshift(F_log * H_homomorphic)))

homomorphic = np.expm1(img_filtered)
homomorphic = cv.normalize(homomorphic, None, 0, 255, cv.NORM_MINMAX).astype(np.uint8)

# show_images(
#     [H_homomorphic, img, homomorphic],
#     ["Homomorphic Mask", "Original", "Homomorphic Filter"]
# )

# ============================================================
# 3. NOISE MODELS
# ============================================================

# Add Noise - adds a noise pattern to the image and clips to [0, 255]
# Formula: g = f + noise
add_noise = lambda noise: clip(img + noise)

# Gaussian noise - random grain drawn from a normal distribution
# Formula: g = f + N(mean, std)
gaussian_mean, gaussian_std = 0, 20  # higher std -> noisier, grainier image
gaussian_noise = np.random.normal(gaussian_mean, gaussian_std, img.shape)
gaussian_img = add_noise(gaussian_noise)

# Uniform noise - every value in [min, max] equally likely
# Formula: g = f + U(min, max)
uniform_min, uniform_max = -40, 40  # wider [min, max] range -> stronger, more visible noise
uniform_noise = np.random.uniform(uniform_min, uniform_max, img.shape)
uniform_img = add_noise(uniform_noise)

# Impulse (salt & pepper) noise - random pixels forced to pure black or white
# Formula: g = 0 with prob p/2, 255 with prob p/2, else f
impulse_probability = 0.05  # higher probability -> more salt/pepper pixels flipped to 0 or 255
random_values = np.random.rand(height, width)
impulse_img = img.copy()
impulse_img[random_values < impulse_probability / 2] = MIN_INTENSITY
impulse_img[random_values > 1 - impulse_probability / 2] = MAX_INTENSITY

# Speckle noise - multiplicative, so brighter regions get noisier
# Formula: g = f + f * N(mean, std)
speckle_mean, speckle_std = 0, 0.2  # higher std -> stronger multiplicative noise, more grainy in bright regions
speckle_noise = np.random.normal(speckle_mean, speckle_std, img.shape)
speckle_img = add_noise(img * speckle_noise)

# Poisson noise - photon-counting noise, variance equals the pixel intensity
# Formula: g ~ Poisson(f)
poisson_img = clip(np.random.poisson(img))

# Rayleigh noise - skewed, always-positive noise (range imaging)
# Formula: g = f + Rayleigh(scale)
rayleigh_scale = 20  # larger scale -> stronger, more spread-out noise
rayleigh_noise = np.random.rayleigh(rayleigh_scale, img.shape)
rayleigh_img = add_noise(rayleigh_noise)

# Periodic noise - sinusoidal stripes (shows up as bright spikes in the spectrum)
# Formula: g = f + A * sin(2 * pi * x / T)
period, periodic_amplitude = 10, 20  # shorter period -> tighter stripes; larger amplitude -> more visible banding
x = np.arange(width)
periodic_noise = np.tile(periodic_amplitude * np.sin(2 * np.pi * x / period), (height, 1))
periodic_img = add_noise(periodic_noise)

# show_images(
#     [gaussian_noise, gaussian_img, uniform_noise, uniform_img, impulse_img, speckle_noise, speckle_img, periodic_noise, periodic_img],
#     ["Gaussian Noise", "Gaussian Image", "Uniform Noise", "Uniform Image", "Impulse Image", "Speckle Noise", "Speckle Image", "Periodic Noise", "Periodic Image"]
# )

# ============================================================
# 4. DENOISING
# ============================================================

noisy = gaussian_img
window_size = 3  # larger window -> more noise removed, but more detail blurred

# --- 4.1 Mean Filters (linear, spatial) ---

# Arithmetic Mean - plain average of the window (same as the box filter)
# Formula: f_hat = (1 / mn) * sum(g)
mean3 = cv.filter2D(noisy, ddepth, box_kernel(window_size))

# Weighted Average - centre pixel counts more than neighbours
# Formula: f_hat = sum(w * g) / sum(w)
weighted_kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], np.float32) / 16  # divided by sum of weights
weighted3 = cv.filter2D(noisy, ddepth, weighted_kernel)

# show_images(
#     [noisy, mean3, weighted3],
#     ["Noisy", "Mean Filter", "Weighted Average"]
# )

# --- 4.2 Order-Statistic Filters (non-linear, spatial) ---

trim = 2  # d -> number of extreme values dropped per window (d/2 lowest + d/2 highest)

# Sliding windows - every pixel's neighbourhood flattened into one row
padded = np.pad(noisy, window_size // 2, mode="edge")
windows = np.lib.stride_tricks.sliding_window_view(padded, (window_size, window_size)).reshape(height, width, -1)

# Median - middle value of the window, best for salt & pepper
# Formula: f_hat = median(g)
median = np.median(windows, axis=-1)

# Minimum - darkest value of the window, removes salt (white) noise
# Formula: f_hat = min(g)
minimum = np.min(windows, axis=-1)

# Maximum - brightest value of the window, removes pepper (black) noise
# Formula: f_hat = max(g)
maximum = np.max(windows, axis=-1)

# Alpha-trimmed mean - drops extremes then averages, good for mixed noise
# Formula: f_hat = (1 / (mn - d)) * sum(g after dropping d/2 lowest and d/2 highest)
sorted_windows = np.sort(windows, axis=-1)
alpha_trimmed = np.mean(sorted_windows[..., trim // 2 : -trim // 2], axis=-1)

# show_images(
#     [noisy, median, minimum, maximum, alpha_trimmed],
#     ["Noisy", "Median", "Minimum", "Maximum", "Alpha Trimmed"]
# )

# --- 4.3 Anisotropic Diffusion Filter (edge-preserving) ---

iterations = 20  # more iterations -> more smoothing
K = 10           # larger K -> more smoothing across edges
lamb = 0.2       # step size -> how strongly each iteration updates the image

# Anisotropic Diffusion - smooths flat regions but stops diffusing across strong edges
# Formula: I = I + lambda * sum over N,S,E,W of (grad * exp(-(grad / K)^2))
diffused = gaussian_img.astype(float)

for _ in range(iterations):
    gradients = [np.roll(diffused, shift, axis) - diffused for shift, axis in [(-1, 0), (1, 0), (-1, 1), (1, 1)]]
    diffused += lamb * sum(grad * np.exp(-(grad / K) ** 2) for grad in gradients)

anisotropic = clip(diffused)

# show_images(
#     [gaussian_img, anisotropic],
#     ["Gaussian Noisy", "Anisotropic Diffusion"]
# )

# --- 4.4 Frequency Domain Denoising (periodic noise) ---

cutoff_frequency = 40  # larger cutoff -> more high frequencies retained, less blur

# FFT Denoising - Gaussian LPF removes the high-frequency stripe spikes
# Formula: g = IFFT(FFT(noisy) * exp(-D^2 / (2 * D0^2)))
periodic_mask = gaussian_H(cutoff_frequency)
denoised_image = apply_mask(periodic_mask, to_freq(periodic_img))

# show_images(
#     [periodic_img, periodic_mask * 255, denoised_image],
#     ["Periodic Noisy", "Gaussian LPF Mask", "FFT Denoised"]
# )

# ============================================================
# 5. DEGRADATION (BLUR) MODELS  ->  G = F * H
# ============================================================

# Blur - degrades the image with frequency response H
# Formula: g = IFFT(F * H)  (same as spatial convolution g = h * f)
blur = lambda H: to_spatial(F * H)

# Out-of-focus (oof) - lens defocus spreads each point into a uniform disk
# Formula: h = 1 / (pi * R^2) inside a disk of radius R, else 0;  H = FFT(h)
def out_of_focus_H(radius):
    psf = np.zeros((height, width), dtype=np.float32)
    cv.circle(psf, (width // 2, height // 2), radius, 1, -1)
    psf /= psf.sum()
    return to_freq(np.fft.ifftshift(psf))

out_of_focus_radius = 10  # larger radius -> stronger blur
H_oof = out_of_focus_H(out_of_focus_radius)
out_of_focus_blur = blur(H_oof)

# Motion blur - camera moving in a straight line smears each point along it
# Formula: h = 1 / L along a horizontal line of length L
motion_length = 15  # longer length -> stronger directional blur
motion_psf = np.zeros((motion_length, motion_length), np.float32)
motion_psf[motion_length // 2, :] = 1
motion_psf /= motion_psf.sum()

motion_blur = cv.filter2D(img, ddepth, motion_psf)

# Atmospheric turbulence - air turbulence smoothly blurs the whole image
# Formula: H = exp(-k * D^(5/3))
turbulence_strength = 0.001  # larger k -> stronger turbulence blur
turbulence_blur = blur(np.exp(-turbulence_strength * D ** (5 / 3)))

# show_images(
#     [img, out_of_focus_blur, motion_blur, turbulence_blur],
#     ["Original", "Out-of-Focus", "Motion Blur", "Atmospheric Turbulence"]
# )

# Varying the oof radius - bigger disk = more blur and more zero rings in H
# Formula: H_R = FFT(disk of radius R)
radii = [3, 5, 7, 10, 15]  # larger radius -> more blur and a more ill-conditioned (harder to invert) OTF
radius_H = [out_of_focus_H(r) for r in radii]
radius_blurs = [blur(H_r) for H_r in radius_H]

# show_images(
#     radius_blurs + [np.abs(H_r) for H_r in radius_H],
#     [f"Blurred R={r}" for r in radii] + [f"OTF R={r}" for r in radii]
# )

# ============================================================
# 6. RESTORATION  ->  undo H
# ============================================================

# Inverse Filter - divides the blur back out of the spectrum
# Formula: F_hat = G / H
inverse_filter = lambda G, H: to_spatial(np.nan_to_num(G / H))

# Pseudo-Inverse Filter - inverse filter, but skips frequencies where H is ~0
# Formula: F_hat = G / H if |H| > threshold else 0
pseudo_inverse_filter = lambda G, H, threshold: to_spatial(np.where(np.abs(H) > threshold, G / H, 0))

# Wiener Filter - inverse filter damped by the noise-to-signal ratio K
# Formula: F_hat = (conj(H) / (|H|^2 + K)) * G
wiener_filter = lambda G, H, K: to_spatial((np.conj(H) / (np.abs(H) ** 2 + K)) * G)

# Blur + Noise - blurs the image with H, adds Gaussian noise, returns the noisy spectrum
# Formula: G = F * H + N
blur_and_noise = lambda H, std: to_freq(blur(H) + np.random.normal(0, std, img.shape))

# --- 6.1 Inverse Filter - Gaussian blur, no noise ---

# Gaussian blur + inverse - with no noise, G / H recovers the image exactly
# Formula: G = F * exp(-D^2 / (2 * D0^2)),  F_hat = G / H
D0_blur = 10  # larger D0 -> weaker blur (H stays close to 1 over more frequencies)
H_gauss = gaussian_H(D0_blur)
G_gauss = F * H_gauss

gauss_blurred = to_spatial(G_gauss)
gauss_inverse = inverse_filter(G_gauss, H_gauss)

# show_images(
#     [img, H_gauss, gauss_blurred, gauss_inverse],
#     ["Original", "Gaussian H", "Blurred", "Inverse Restored"]
# )

# --- 6.2 Inverse Filter - wrong parameter ---

# Wrong parameter - restoring with the wrong H leaves residual blur
# Formula: F_hat = (F * H_true) / H_wrong
D0_wrong = 5  # smaller than D0_blur -> under-corrects the true blur, image stays blurry
wrong_restored = inverse_filter(G_gauss, gaussian_H(D0_wrong))

# show_images(
#     [img, gauss_blurred, wrong_restored],
#     ["Original", "Blurred (D0=10)", "Restored (assumed D0=5)"]
# )

# --- 6.3 Inverse Filter - Gaussian blur + Gaussian noise ---

# Noisy inverse - noise gets amplified wherever H is small
# Formula: G / H = F + N / H
noise_std = 5  # larger std -> more noise, which the inverse filter blows up even more
G_noisy = blur_and_noise(H_gauss, noise_std)

blurred_noisy = to_spatial(G_noisy)
noisy_inverse = inverse_filter(G_noisy, H_gauss)

# show_images(
#     [img, gauss_blurred, blurred_noisy, noisy_inverse],
#     ["Original", "Blurred", "Blurred + Noisy", "Inverse Filter Restored"]
# )

# --- 6.4 Inverse vs Pseudo-Inverse vs Wiener - out-of-focus blur ---

threshold = 0.01    # larger threshold -> more stable, less detail recovered
noise_ratio = 0.01  # larger K -> less noise amplification, more residual blur

# Compare restorations - same oof blur (from section 5), three ways to undo it
# Formula: G = F * H_oof
G_oof = F * H_oof

inverse_img = inverse_filter(G_oof, H_oof)
pseudo_inverse_img = pseudo_inverse_filter(G_oof, H_oof, threshold)
wiener_img = wiener_filter(G_oof, H_oof, noise_ratio)

# show_images(
#     [img, out_of_focus_blur, inverse_img, pseudo_inverse_img, wiener_img],
#     ["Original", "Blurred", "Inverse", "Pseudo-Inverse", "Wiener"]
# )

# --- 6.5 Wiener Filter - out-of-focus blur + Gaussian noise ---

oof_radius = 7      # larger radius -> stronger blur to restore from
oof_noise_var = 10  # larger variance -> noisier image, needs a larger K
wiener_K = 0.03     # larger K suppresses noise amplification more, at the cost of leaving more residual blur

# Wiener on noisy oof - balances undoing the blur against amplifying noise
# Formula: F_hat = (conj(H) / (|H|^2 + K)) * (F * H + N)
H_oof7 = out_of_focus_H(oof_radius)
G_oof_noisy = blur_and_noise(H_oof7, np.sqrt(oof_noise_var))

oof_noisy = to_spatial(G_oof_noisy)
oof_wiener = wiener_filter(G_oof_noisy, H_oof7, wiener_K)

# show_images(
#     [img, blur(H_oof7), oof_noisy, oof_wiener],
#     ["Original", "Blurred", "Blurred + Noisy", "Wiener Restored"]
# )
