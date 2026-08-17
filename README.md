# 20XW97 — Computer Vision Lab

Coursework, from-scratch algorithm implementations, and reference notes for the Computer Vision Lab (20XW97) course. Most techniques here are implemented manually with NumPy pixel loops rather than single OpenCV calls, to work through the underlying math.

## Structure

| Path | Contents |
| --- | --- |
| [`getting-started/`](getting-started) | Guided intro notebook covering OpenCV/NumPy basics — I/O, resizing, cropping, color spaces, drawing, arithmetic |
| [`concepts/`](concepts) | Standalone scripts, one per technique (thresholding, quantization, edge detection, histogram equalization/matching, connected-component labelling, etc.) |
| [`PS01/`](PS01) – [`PS05/`](PS05) | Problem-set answer notebooks |
| [`images/`](images) | Sample/test images used across scripts and notebooks |
| [`docs/cheatsheet.md`](docs/cheatsheet.md) | Quick-reference for every OpenCV/NumPy/Matplotlib function and manual concept used in this repo |

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Running

Scripts in `concepts/` are standalone — each opens image windows via `cv.imshow`, so run them from inside that directory:

```bash
cd concepts
uv run python thresholding.py
```

Notebooks (`getting-started/`, `PS01`–`PS05`) run with any Jupyter-compatible kernel pointed at the project's virtual environment.

## License

[MIT](LICENSE)
