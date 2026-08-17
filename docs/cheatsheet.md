# Image Processing Cheatsheet

## OpenCV — I/O & Display

### `cv.imread()`
```python
cv.imread(path, flags)
```
*path: file path to read · flags: 0=grayscale, 1=color (default), unset=color*
```python
img = cv.imread("../images/lenna.png", 0)
```

### `cv.imshow()`
```python
cv.imshow(window_name, image)
```
*window_name: title shown on the window · image: array to display*
```python
cv.imshow("Original", img)
```

### `cv.waitKey()`
```python
cv.waitKey(delay)
```
*delay: ms to wait for a keypress, 0 = wait forever*
```python
cv.waitKey(0)
```

### `cv.destroyAllWindows()`
```python
cv.destroyAllWindows()
```
*closes every OpenCV window opened by imshow*
```python
cv.destroyAllWindows()
```

### `cv.imwrite()`
```python
cv.imwrite(path, img, params)
```
*path: output file (extension picks the codec) · img: array to save · params: e.g. `[cv.IMWRITE_JPEG_QUALITY, q]`*
```python
cv.imwrite(path, tif_img, [cv.IMWRITE_JPEG_QUALITY, q])
```

### `os.path.getsize()`
```python
os.path.getsize(path)
```
*path: file path · returns file size in bytes*
```python
print("PNG", os.path.getsize("../images/lenna.png"))
```

## OpenCV — Geometric Transforms

### `cv.resize()`
```python
cv.resize(src, dsize, fx, fy, interpolation)
```
*src: input image · dsize: `(w,h)` target size, `None`/`(0,0)` to use fx/fy instead · fx, fy: scale factors · interpolation: e.g. `cv.INTER_NEAREST`*
```python
img_50 = cv.resize(img, dsize=None, fx=0.5, fy=0.5)
```

### `cv.rotate()`
```python
cv.rotate(src, rotateCode)
```
*src: input image · rotateCode: `cv.ROTATE_90_CLOCKWISE` / `_COUNTERCLOCKWISE` / `ROTATE_180`*
```python
rot_90 = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
```

### `cv.getRotationMatrix2D()`
```python
cv.getRotationMatrix2D(center, angle, scale)
```
*center: pivot point `(x,y)` · angle: degrees, counter-clockwise · scale: isotropic scale factor*
```python
matrix_45 = cv.getRotationMatrix2D(center, 45, 1)
```

### `cv.warpAffine()`
```python
cv.warpAffine(src, M, dsize)
```
*src: input image · M: 2x3 affine matrix · dsize: output `(w,h)`*
```python
translated = cv.warpAffine(img, matrix, (width, height))
```

### `cv.flip()`
```python
cv.flip(src, flipCode)
```
*src: input image · flipCode: 0=vertical, 1=horizontal, -1=both*
```python
x_flip = cv.flip(img, 0)
```

### `imutils.translate()`
```python
imutils.translate(img, x, y)
```
*img: input image · x, y: pixel shift along each axis*
```python
translated = imutils.translate(img, 50, 30)
```

## OpenCV — Drawing

### `cv.rectangle()`
```python
cv.rectangle(img, pt1, pt2, color, thickness)
```
*pt1: top-left corner · pt2: bottom-right corner · color: BGR/gray value · thickness: border width, -1 = filled*
```python
cv.rectangle(img, (50, 50), (150, 150), 255, 2)
```

### `cv.circle()`
```python
cv.circle(img, center, radius, color, thickness)
```
*center: `(x,y)` · radius: pixels · color: BGR/gray value · thickness: border width, -1 = filled*
```python
cv.circle(img1, (120, 100), 80, 255, -1)
```

### `cv.putText()`
```python
cv.putText(img, text, org, fontFace, fontScale, color, thickness)
```
*org: bottom-left `(x,y)` of text · fontFace: font id (`0`=`cv.FONT_HERSHEY_SIMPLEX`) · fontScale: size multiplier · color: BGR/gray value · thickness: stroke width*
```python
cv.putText(gray_lvl_img, f"{bits}-bit", (10, 30), 0, 1, 0, 1)
```

### `cv.hconcat()`
```python
cv.hconcat(images)
```
*images: list of same-height arrays to join side by side*
```python
combined = cv.hconcat(bit_planes)
```

## OpenCV — Color & Thresholding

### `cv.cvtColor()`
```python
cv.cvtColor(src, code)
```
*src: input image · code: conversion constant, e.g. `cv.COLOR_BGR2GRAY`*
```python
gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
```

### `cv.threshold()`
```python
cv.threshold(src, thresh, maxval, type)
```
*src: input (grayscale) · thresh: cutoff value · maxval: value assigned to foreground · type: e.g. `cv.THRESH_BINARY`, `cv.THRESH_BINARY_INV`*
```python
_, img = cv.threshold(img, 128, 255, cv.THRESH_BINARY_INV)
```

### `cv.adaptiveThreshold()`
```python
cv.adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C)
```
*adaptiveMethod: how the local threshold is computed (mean/gaussian) · blockSize: neighborhood size (odd) · C: constant subtracted from the local mean*
```python
ref_adaptive = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, block, C)
```

### `cv.equalizeHist()`
```python
cv.equalizeHist(src)
```
*src: single-channel (grayscale) image · applies histogram equalization automatically*
```python
equalized_img = cv.equalizeHist(gray_img)
```

### `cv.calcHist()`
```python
cv.calcHist(images, channels, mask, histSize, ranges)
```
*images: list of source images · channels: which channel to histogram · mask: `None` for full image · histSize: bin count · ranges: value range*
```python
hist = cv.calcHist([gray_img], [0], None, [256], [0, 256])
```

## OpenCV — Filtering & Edges

### `cv.blur()`
```python
cv.blur(src, ksize)
```
*src: input image · ksize: `(w,h)` averaging kernel size*
```python
mean3 = cv.blur(noisy, (3, 3))
```

### `cv.medianBlur()`
```python
cv.medianBlur(src, ksize)
```
*src: input image · ksize: odd kernel side length (single int)*
```python
median3 = cv.medianBlur(noisy, 3)
```

### `cv.filter2D()`
```python
cv.filter2D(src, ddepth, kernel)
```
*ddepth: output depth, `-1` keeps source depth · kernel: convolution mask*
```python
gx = cv.filter2D(img, cv.CV_64F, prewitt_x)
```

### `cv.Sobel()`
```python
cv.Sobel(src, ddepth, dx, dy, ksize)
```
*ddepth: output depth · dx, dy: derivative order in each direction · ksize: Sobel kernel size*
```python
gx = cv.Sobel(img, cv.CV_64F, 1, 0, 3)
```

### `cv.Laplacian()`
```python
cv.Laplacian(src, ddepth, ksize)
```
*ddepth: output depth · ksize: aperture size*
```python
lap = cv.Laplacian(img, cv.CV_64F, 3)
```

### `cv.magnitude()`
```python
cv.magnitude(x, y)
```
*x, y: gradient components in each direction, same shape*
```python
magnitude = cv.magnitude(gx, gy)
```

### `cv.convertScaleAbs()`
```python
cv.convertScaleAbs(src)
```
*takes `|src|` and scales/clips it back to 8-bit*
```python
sobel = cv.convertScaleAbs(cv.magnitude(sobel_x, sobel_y))
```

### `cv.normalize()`
```python
cv.normalize(src, dst, alpha, beta, norm_type)
```
*dst: output array, `None` = auto-create · alpha, beta: target value range · norm_type: e.g. `cv.NORM_MINMAX`*
```python
magnitude = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)
```

### `cv.connectedComponents()`
```python
cv.connectedComponents(image, connectivity)
```
*image: binary (0/255) input · connectivity: 4 or 8 · returns `(num_labels, label_map)`, background counts as label 0*
```python
n, _ = cv.connectedComponents(img, connectivity=8)
```

## NumPy — Array Creation

### `np.array()`
```python
np.array(values, dtype)
```
*values: nested list/tuple of numbers · dtype: element type*
```python
kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
```

### `np.zeros()`
```python
np.zeros(shape, dtype)
```
*shape: output dimensions · dtype: element type*
```python
result = np.zeros((height, width), dtype=np.float32)
```

### `np.ones()`
```python
np.ones(shape, dtype)
```
*shape: output dimensions · dtype: element type*
```python
img1 = np.ones((200, 200), dtype=np.uint8) * 0
```

### `np.zeros_like()` / `np.ones_like()`
```python
np.zeros_like(array, dtype)
```
*array: source to copy shape from · dtype: override element type (optional)*
```python
label = np.zeros((h, w), dtype=np.int32)
```

### `np.pad()`
```python
np.pad(array, pad_width, mode)
```
*pad_width: border size (int or per-axis) · mode: fill strategy, e.g. `"edge"`, `"reflect"`, `"constant"`*
```python
padded = np.pad(img, half, mode="reflect")
```

## NumPy — Reshaping & Stats

### `.ravel()` / `.flatten()`
```python
array.ravel()
```
*ravel returns a view when possible, flatten always copies — both give a 1D array*
```python
hist, _ = np.histogram(img.ravel(), bins=256, range=[0, 256])
```

### `np.min()` / `np.max()`
```python
np.min(array)
```
*array: input · returns the smallest (or largest) element*
```python
Imin = np.min(img)
```

### `np.mean()` / `np.median()`
```python
np.mean(array)
```
*array: input · returns the average (or middle) value of all elements*
```python
result[i, j] = np.mean(mask)
```

### `np.sqrt()` / `np.abs()`
```python
np.sqrt(array)
```
*array: input, applied element-wise*
```python
magnitude = np.sqrt(gx**2 + gy**2)
```

### `np.sum()`
```python
np.sum(array)
```
*array: input · adds every element together*
```python
value = np.sum(mask * kernel)
```

### `np.sort()`
```python
np.sort(array)
```
*array: input · returns elements in ascending order*
```python
x = np.sort(img.flatten())
```

### `np.arange()`
```python
np.arange(start, stop, step)
```
*start: first value (default 0) · stop: exclusive upper bound · step: increment (default 1)*
```python
x = np.arange(256)
```

### `np.unique()`
```python
np.unique(array, return_counts)
```
*array: input · return_counts=True also returns how often each value occurs*
```python
values, counts = np.unique(img, return_counts=True)
```

### `np.clip()`
```python
np.clip(array, minimum, maximum)
```
*array: input · minimum, maximum: bounds to clamp values into*
```python
clipped = np.clip(img, 50, 200)
```

### `np.histogram()`
```python
np.histogram(array, bins, range)
```
*array: input values (flattened) · bins: number of bins · range: `[low, high]` value span*
```python
hist, bins = np.histogram(img.flatten(), bins=256, range=[0, 256])
```

### `.cumsum()`
```python
array.cumsum()
```
*returns the running (cumulative) sum along the array*
```python
cdf = hist.cumsum()
```

### `.argmin()`
```python
array.argmin()
```
*returns the index of the smallest element*
```python
mapping[src_val] = np.abs(ref_cdf - src_cdf[src_val]).argmin()
```

### `np.random.normal()`
```python
np.random.normal(mean, std, size)
```
*mean: distribution center · std: spread · size: output shape*
```python
gauss = np.random.normal(0, np.sqrt(1000), img.shape)
```

### `.astype()`
```python
array.astype(dtype)
```
*dtype: target type, e.g. `np.uint8` for display, `np.float32` for math*
```python
equalized = ((cdf - cdf_min) / (N - cdf_min) * 255).astype(np.uint8)
```

## Matplotlib

### `plt.hist()`
```python
plt.hist(array, bins, range)
```
*array: values to bin · bins: bin count · range: `[low, high]`*
```python
plt.hist(img.ravel(), bins=256, range=[0, 256])
```

### `plt.plot()`
```python
plt.plot(x, y, label)
```
*x, y: coordinate arrays · label: legend entry (optional)*
```python
plt.plot(x, 255 * np.log(1 + x) / np.log(256), label="Log")
```

### `plt.scatter()`
```python
plt.scatter(x, y, s)
```
*x, y: point coordinates · s: marker size*
```python
plt.scatter(img.flatten(), log_img.flatten(), s=1)
```

### `plt.figure()`
```python
plt.figure(figsize)
```
*figsize: `(width, height)` in inches*
```python
plt.figure(figsize=(8, 6))
```

### `plt.xlabel()` / `plt.ylabel()` / `plt.title()`
```python
plt.xlabel(text)
```
*text: label string shown on the axis/plot*
```python
plt.xlabel("Input intensity")
```

### `plt.legend()` / `plt.grid()` / `plt.show()`
```python
plt.legend()
```
*legend draws labels set via `label=`, grid overlays gridlines, show renders the figure*
```python
plt.legend()
```

## From-Scratch Concepts

### Image dimensions
```python
height, width = img.shape[:2]
```
*`[:2]` guards against 3-channel color images where `.shape` also has a channel count*
```python
height, width = img.shape
```

### Bit-plane extraction
```python
(img[i, j] >> bit) & 1
```
*`>> bit` shifts the target bit down to position 0 · `& 1` masks off everything else*
```python
bit_plane[i, j] = (img[i, j] >> bit) & 1
```

### Bit-depth quantization
```python
(img >> (8 - bits)) << (8 - bits)
```
*right-shift drops the low-order bits, left-shift restores their original position (zeroed)*
```python
gray_quantized = (gray >> (8 - bits)) << (8 - bits)
```

### Spatial subsampling
```python
img[::factor, ::factor]
```
*strided slicing on rows and columns to shrink resolution without interpolation*
```python
spatial_power = img[::factor, ::factor]
```

### Pixel-wise convolution (manual)
```python
np.sum(padded[i:i+k, j:j+k] * kernel)
```
*slide a `k×k` window over the padded image, multiply by the kernel, and sum for each output pixel*
```python
gx = np.sum(mask * kernel_x)
```

### Contrast stretching (piecewise linear)
```python
((s2 - s1) / (r2 - r1)) * (img[i, j] - r1) + s1
```
*maps intensities below `r1` to `s1`, above `r2` to `s2`, and linearly interpolates in between*
```python
contrast[i, j] = ((s2 - s1) / (r2 - r1)) * (img[i, j] - r1) + s1
```

### Histogram equalization (manual)
```python
mapping = ((cdf - cdf_min) / (N - cdf_min) * 255).astype(np.uint8)
```
*builds a lookup table from the cumulative histogram, then applies it via fancy indexing*
```python
result = equalized[img]
```

### Histogram matching / specification
```python
mapping[i] = np.argmin(np.abs(ref_cdf - src_cdf[i]))
```
*for each source gray level, pick the reference gray level whose CDF value is closest*
```python
matched = mapping[img]
```

### Global / band / adaptive thresholding (manual)
```python
dst[i, j] = 255 if condition else 0
```
*global compares against one constant, band checks a `[low, high]` range, adaptive compares against the local window mean*
```python
if img[i, j] > local_mean - C: adaptive_thresh[i, j] = 255
```

### Mean / median filter (manual)
```python
result[i, j] = np.mean(padded[i:i+size, j:j+size])
```
*slide a window over the padded image and replace each pixel with the window's average (or median for edge-preserving denoising)*
```python
result[i, j] = np.median(mask)
```

### Connected-component labelling (4/8-connectivity)
```python
if A == D: A_label = D_label  # else compare against left(B)/top(C) neighbors
```
*single-pass raster scan; 8-connectivity also checks the diagonal (top-left) neighbor `D`, 4-connectivity only checks left/top*
```python
label[label == C_label] = B_label  # merge equivalent labels
```

### Arithmetic / logical image operations
```python
add[i, j] = min(int(a) + int(b), 255)
```
*cast to `int` first to avoid `uint8` overflow/wraparound, then clamp back into `[0, 255]`*
```python
AND[i, j] = 255 if (a and b) else 0
```

### Gamma / log intensity transforms
```python
255 * (img / 255) ** gamma
```
*normalize to `[0,1]`, apply the power-law (or `np.log`) curve, then rescale back to `[0,255]`*
```python
gamma_corrected = 255 * (img / 255) ** 0.5
```

## ⭐ Priority list (cram these first)

```python
cv.imread(path, 0)
cv.imshow("Name", img)
cv.waitKey(0)
cv.destroyAllWindows()
cv.threshold(img, 128, 255, cv.THRESH_BINARY)
cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.equalizeHist(img)
cv.calcHist([img], [0], None, [256], [0, 256])
cv.normalize(x, None, 0, 255, cv.NORM_MINMAX)
cv.filter2D(img, cv.CV_64F, kernel)
cv.Sobel(img, cv.CV_64F, 1, 0, 3)
cv.Laplacian(img, cv.CV_64F, 3)
cv.connectedComponents(img, connectivity=8)
cv.hconcat(images)
np.histogram(img.ravel(), 256, [0, 256])
hist.cumsum()
np.clip(img, 0, 255)
np.sqrt(gx**2 + gy**2)
np.unique(img, return_counts=True)
np.random.normal(mean, sigma, img.shape)
plt.hist(img.ravel(), bins=256, range=[0, 256])
plt.plot(x, y)
plt.show()
```

