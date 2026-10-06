#!/usr/bin/env python3
"""Generate the slide images/GIFs from the demo footage. Run AFTER speed_detection.py
(it reuses outputs/annotated.mp4 and the violation snapshots). Not needed for the live demo.

    python make_slide_assets.py [--config config.yaml] [--out outputs] [--demo-run outputs/demo_limit50]
"""
import argparse, csv, warnings
from collections import Counter, defaultdict, deque
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
import yaml
from PIL import Image
from ultralytics import YOLO

from speed_detection import CLASS_NAMES, GREEN, RED, YELLOW, WHITE, BLACK, ViewTransformer, put_label

warnings.filterwarnings("ignore", category=FutureWarning)
UP = 2           # slide stills: 640x360 footage upscaled 2x -> 1280x720
GIF_S = 6.0      # GIF length in seconds
BLUE = (230, 140, 30)


def up(img):
    return cv2.resize(img, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)


def save_gif(frames, path, fps):
    """BGR frames -> looping GIF with one shared palette (small + no flicker)."""
    rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
    sample = Image.fromarray(np.vstack(rgb[:: max(1, len(rgb) // 8)]))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    ims = [Image.fromarray(f).quantize(palette=pal, dither=Image.Dither.NONE) for f in rgb]
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0, optimize=True)
    print(f"{path}: {len(ims)} frames, {Path(path).stat().st_size / 1e6:.1f} MB")


def read_frames(path, start, count, step=1):
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    for i in range(count):
        ok, f = cap.read()
        if not ok:
            break
        if i % step == 0:
            frames.append(f)
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default="outputs")
    ap.add_argument("--demo-run", default="outputs/demo_limit50", help="run folder with violations (lower limit)")
    args = ap.parse_args()
    cfg, out = yaml.safe_load(open(args.config)), Path(args.out)
    cap = cv2.VideoCapture(cfg["video"])
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    poly = np.array(cfg["source"], np.int32)
    W, L = cfg["target_width_m"], cfg["target_length_m"]
    vt = ViewTransformer(poly, W, L)
    model = YOLO(cfg["model"])
    yolo = dict(conf=cfg["confidence"], iou=cfg["iou"], classes=cfg["classes"], agnostic_nms=True, verbose=False)

    # Pass 1: same detect -> track -> speed pipeline as speed_detection.py, recording per-frame state.
    tracker, zone = sv.ByteTrack(frame_rate=fps, track_activation_threshold=cfg["confidence"]), sv.PolygonZone(poly)
    hist, votes = defaultdict(lambda: deque(maxlen=int(fps))), defaultdict(Counter)
    states = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        i = len(states)
        det = sv.Detections.from_ultralytics(model(frame, **yolo)[0])
        det = tracker.update_with_detections(det[zone.trigger(det)])
        pts = vt.transform(det.get_anchors_coordinates(sv.Position.BOTTOM_CENTER))
        rec = []
        for tid, cid, box, (xm, ym) in zip(det.tracker_id, det.class_id, det.xyxy, pts):
            h = hist[tid]
            h.append((i, ym))
            votes[int(tid)][CLASS_NAMES.get(int(cid), "?")] += 1
            el = h[-1][0] - h[0][0]
            kmh = abs(h[-1][1] - h[0][1]) / (el / fps) * 3.6 if el >= fps / 2 else None
            rec.append((int(tid), CLASS_NAMES.get(int(cid), "?"), box.astype(int), kmh, float(xm), float(ym)))
        states.append(rec)
    n = len(states)
    states = [[(t, votes[t].most_common(1)[0][0], *r[1:]) for t, *r in s] for s in states]  # majority class
    labelled = np.array([sum(r[3] is not None for r in s) for s in states])
    key = int(np.argmax(labelled))                       # still frame: most vehicles with a speed
    win = int(GIF_S * fps)
    sums = np.convolve(labelled, np.ones(win), "valid")
    g0 = int(np.argmax(sums))                            # GIF window: busiest 6 s
    print(f"key frame {key} ({labelled[key]} vehicles with speed); GIF window {g0 / fps:.1f}-{(g0 + win) / fps:.1f} s")

    raw = read_frames(cfg["video"], key, 1)[0]
    cv2.imwrite(str(out / "frame_raw.png"), up(raw))

    # Detections only (no tracking, no zone): class + confidence
    img = up(raw)
    res = model(raw, **yolo)[0]
    for (x1, y1, x2, y2), c, s in zip(res.boxes.xyxy.cpu().numpy().astype(int) * UP, res.boxes.cls.cpu().numpy(), res.boxes.conf.cpu().numpy()):
        cv2.rectangle(img, (x1, y1), (x2, y2), BLUE, 2)
        put_label(img, f"{CLASS_NAMES.get(int(c), '?')} {s:.2f}", x1, y1 - 2, BLUE, 0.7)
    cv2.imwrite(str(out / "frame_detections.png"), img)

    # Tracked: zone + IDs + speeds
    img = up(raw)
    cv2.polylines(img, [poly * UP], True, YELLOW, 2)
    for tid, cls, box, kmh, _, _ in states[key]:
        x1, y1, x2, y2 = box * UP
        lab = f"#{tid} {cls}" + (f" {kmh:.0f} km/h" if kmh is not None else "")
        col = RED if kmh is not None and kmh > cfg["speed_limit_kmh"] else GREEN
        cv2.rectangle(img, (x1, y1), (x2, y2), col, 2)
        put_label(img, lab, x1, y1 - 2, col, 0.7)
    cv2.imwrite(str(out / "frame_tracked.png"), img)

    # Homography before: source polygon with corner coordinates and real-world size
    img = up(raw)
    cv2.polylines(img, [poly * UP], True, YELLOW, 3)
    for k, (x, y) in enumerate(poly):
        cv2.circle(img, (x * UP, y * UP), 8, RED, -1)
        put_label(img, f"P{k + 1} ({x},{y})", min(x * UP + 10, 1100), y * UP - 10, BLACK, 0.7)
    (bx, by), (tx, ty) = (poly[2] + poly[3]) // 2 * UP, (poly[0] + poly[1]) // 2 * UP
    put_label(img, f"{W:g} m (4 lanes x 3.5 m)", bx - 140, by + 34, YELLOW, 0.75)
    put_label(img, f"{L:g} m along road (5 x 6 m dash periods)", (poly[3][0] + poly[0][0]) // 2 * UP + 20, 420, YELLOW, 0.75)
    cv2.imwrite(str(out / "homography_before.png"), img)

    # Homography after: bird's-eye view of the zone at 24 px/m with a metre ruler
    ppm = 24
    m = cv2.getPerspectiveTransform(np.float32(poly), np.float32([[0, 0], [W * ppm, 0], [W * ppm, L * ppm], [0, L * ppm]]))
    bev = cv2.warpPerspective(raw, m, (int(W * ppm), int(L * ppm)))
    canvas = np.full((int(L * ppm) + 60, int(W * ppm) + 90, 3), 255, np.uint8)
    canvas[30:30 + bev.shape[0], 70:70 + bev.shape[1]] = bev
    for d in range(0, int(L) + 1, 5):
        y = 30 + int((L - d) * ppm)
        cv2.line(canvas, (58, y), (68, y), BLACK, 2)
        cv2.putText(canvas, f"{d} m", (6, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLACK, 1, cv2.LINE_AA)
    cv2.putText(canvas, f"{W:g} m", (70 + int(W * ppm) // 2 - 22, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 1, cv2.LINE_AA)
    cv2.imwrite(str(out / "homography_after.png"), canvas)

    # Background subtraction (classical CV baseline): frame vs MOG2 mask after warm-up
    k2 = min(max(key, 150), n - 1)  # >= 6 s of warm-up so the background model has converged
    mog = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
    for f2 in read_frames(cfg["video"], 0, k2 + 1):
        mask = mog.apply(f2)
    side = np.hstack([f2, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
    side = cv2.resize(side, None, fx=1.25, fy=1.25, interpolation=cv2.INTER_CUBIC)
    put_label(side, "Input frame", 8, 30, BLACK, 0.7)
    put_label(side, f"MOG2 foreground mask (frame {k2}; grey = shadow)", side.shape[1] // 2 + 8, 30, BLACK, 0.7)
    cv2.imwrite(str(out / "background_subtraction.png"), side)

    # GIFs (12.5 fps, native 640 px width)
    save_gif(read_frames(out / "annotated.mp4", g0, win, 2), out / "annotated_preview.gif", fps / 2)
    vio_rows = list(csv.DictReader(open(out / "violations.csv"))) or list(csv.DictReader(open(Path(args.demo_run) / "violations.csv")))
    if vio_rows:
        best = max(vio_rows, key=lambda r: float(r["speed_kmh"]))
        cv2.imwrite(str(out / "violation_example.png"), up(cv2.imread(best["snapshot_path"])))
        demo_vid = Path(best["snapshot_path"]).parent.parent / "annotated.mp4"
        start = max(0, min(int(best["frame"]) - int(2 * fps), n - win))
        save_gif(read_frames(demo_vid, start, win, 2), out / f"annotated_preview_{demo_vid.parent.name}.gif", fps / 2)

    # Tracking preview: camera view with IDs + trails | bird's-eye view with the same IDs
    ppm, frames, trails = 12, [], defaultdict(list)
    m = cv2.getPerspectiveTransform(np.float32(poly), np.float32([[0, 0], [W * ppm, 0], [W * ppm, L * ppm], [0, L * ppm]]))
    for j, f in enumerate(read_frames(cfg["video"], g0, win)):
        rec, left = states[g0 + j], f.copy()
        right = cv2.warpPerspective(f, m, (int(W * ppm), int(L * ppm)))
        cv2.polylines(left, [poly], True, YELLOW, 1)
        for tid, cls, (x1, y1, x2, y2), kmh, xm, ym in rec:
            trails[tid].append(((x1 + x2) // 2, y2))
            col = tuple(int(c) for c in sv.ColorPalette.DEFAULT.by_idx(tid).as_bgr())
            cv2.polylines(left, [np.array(trails[tid][-40:], np.int32)], False, col, 2)
            cv2.rectangle(left, (x1, y1), (x2, y2), col, 2)
            put_label(left, f"#{tid}", x1, y1 - 2, col, 0.45)
            cv2.circle(right, (int(xm * ppm), int(ym * ppm)), 5, col, -1)
            cv2.putText(right, f"#{tid}", (int(xm * ppm) + 6, int(ym * ppm) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1, cv2.LINE_AA)
        if j % 2 == 0:
            frames.append(np.hstack([left, np.full((360, 6, 3), 255, np.uint8), cv2.resize(right, (int(W * ppm), 360))]))
    save_gif(frames, out / "tracking_preview.gif", fps / 2)


if __name__ == "__main__":
    main()
