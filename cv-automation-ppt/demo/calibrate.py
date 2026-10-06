#!/usr/bin/env python3
"""4-point calibration helper for speed_detection.py.

Interactive (needs a display):
    python calibrate.py --source flyover.mp4
    Click 4 road points in order TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT
    (corners of a ground rectangle you can measure, e.g. lane lines x dash ends).
    Keys: r = reset, q / Enter = finish. The points are printed for config.yaml.

Non-interactive check (works headless):
    python calibrate.py --check  ->  outputs/calibration_check.png
    (frame with the current polygon + the bird's-eye warp: lane lines should be
    vertical and parallel, dashes evenly spaced).

Tip: --background builds a median image of the video, i.e. the road without cars.
"""
import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml

CORNERS = ["top-left", "top-right", "bottom-right", "bottom-left"]


def get_frame(source, index, background):
    cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
    if background:  # median of ~40 frames spread over the clip removes moving vehicles
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        frames = []
        for i in np.linspace(0, n - 1, 40).astype(int):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, f = cap.read()
            if ok:
                frames.append(f)
        return np.median(np.stack(frames), axis=0).astype(np.uint8)
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    if not ok:
        raise SystemExit(f"Cannot read frame {index} from {source}")
    return frame


def birds_eye(frame, pts, width_m, length_m, px_per_m=20):
    dst = np.float32([[0, 0], [width_m, 0], [width_m, length_m], [0, length_m]]) * px_per_m
    m = cv2.getPerspectiveTransform(np.float32(pts), dst)
    return cv2.warpPerspective(frame, m, (int(width_m * px_per_m), int(length_m * px_per_m)))


def draw(frame, pts):
    img = frame.copy()
    if len(pts) > 1:
        cv2.polylines(img, [np.int32(pts)], len(pts) == 4, (0, 220, 255), 2)
    for i, (x, y) in enumerate(pts):
        cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
        tx = int(x) + 6 if x < img.shape[1] - 190 else int(x) - 190  # keep the text inside the image
        cv2.putText(img, f"{i + 1}:{CORNERS[i]} ({x},{y})", (tx, max(12, int(y) - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
    return img


def check(frame, pts, cfg, out_path):
    """Save frame-with-polygon next to the bird's-eye view (scaled to the same height)."""
    left = draw(frame, pts)
    bev = birds_eye(frame, pts, cfg["target_width_m"], cfg["target_length_m"])
    bev = cv2.resize(bev, (max(1, int(bev.shape[1] * left.shape[0] / bev.shape[0])), left.shape[0]))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), np.hstack([left, np.full((left.shape[0], 8, 3), 255, np.uint8), bev]))
    print(f"Saved {out_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="video (default: 'video' in config)")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--frame", type=int, default=0, help="frame index to use (default 0)")
    ap.add_argument("--background", action="store_true", help="use a median (car-free) image instead")
    ap.add_argument("--check", action="store_true", help="non-interactive: save image with current polygon")
    ap.add_argument("--out", default="outputs/calibration_check.png")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    frame = get_frame(args.source or cfg["video"], args.frame, args.background)

    if args.check:
        check(frame, cfg["source"], cfg, args.out)
        return

    pts = []

    k = min(1.0, 1280 / frame.shape[1])  # display scale: big videos are shown shrunk to <= 1280 px

    def on_click(event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN and len(pts) < 4:
            x, y = round(x / k), round(y / k)  # back to full-resolution pixel coordinates
            pts.append([x, y])
            print(f"{CORNERS[len(pts) - 1]}: [{x}, {y}]")

    no_gui = "No GUI available -- use --check (or run on a machine with a display and opencv-python)."
    if sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise SystemExit(no_gui)
    try:
        cv2.namedWindow("calibrate", cv2.WINDOW_AUTOSIZE)
    except cv2.error:
        raise SystemExit(no_gui)
    cv2.setMouseCallback("calibrate", on_click)
    print("Click: " + ", ".join(CORNERS) + "   (r = reset, q/Enter = done)")
    while True:
        cv2.imshow("calibrate", cv2.resize(draw(frame, pts), None, fx=k, fy=k))
        if len(pts) == 4:
            cv2.imshow("bird's-eye preview", birds_eye(frame, pts, cfg["target_width_m"], cfg["target_length_m"]))
        key = cv2.waitKey(30) & 0xFF
        if key == ord("r"):
            pts.clear()
            try:
                cv2.destroyWindow("bird's-eye preview")
            except cv2.error:
                pass
        elif key in (ord("q"), 13, 27):
            break
    cv2.destroyAllWindows()
    if len(pts) == 4:
        print("\nPaste into config.yaml (then set target_width_m / target_length_m):\nsource:")
        for p, name in zip(pts, CORNERS):
            print(f"  - [{p[0]}, {p[1]}]    # {name}")
        check(frame, pts, cfg, args.out)
    else:
        print("Fewer than 4 points clicked; nothing saved.")


if __name__ == "__main__":
    main()
