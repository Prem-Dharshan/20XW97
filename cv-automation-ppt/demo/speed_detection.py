#!/usr/bin/env python3
"""Vehicle speed detection: YOLOv8n (detect) -> ByteTrack (track) -> perspective
transform (pixels -> metres) -> speed -> automation rule (flag > speed limit).

Design follows Roboflow's supervision `examples/speed_estimation`.
Usage:  python speed_detection.py --source data/traffic.mp4 [--show] [--save outputs/annotated.mp4] [--limit 60]
"""
import argparse, csv, json, os, platform, sys, time, warnings
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
import yaml
from ultralytics import YOLO

warnings.filterwarnings("ignore", category=FutureWarning)  # sv.ByteTrack deprecation notice
CLASS_NAMES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
GREEN, RED, YELLOW, WHITE, BLACK = (60, 200, 60), (0, 0, 255), (0, 220, 255), (255, 255, 255), (0, 0, 0)


class ViewTransformer:
    """Maps image points to a bird's-eye road frame measured in metres."""
    def __init__(self, source, width_m, length_m):
        target = np.float32([[0, 0], [width_m, 0], [width_m, length_m], [0, length_m]])
        self.m = cv2.getPerspectiveTransform(np.float32(source), target)

    def transform(self, points):
        if len(points) == 0:
            return points
        return cv2.perspectiveTransform(points.reshape(-1, 1, 2).astype(np.float32), self.m).reshape(-1, 2)


def gui_available():
    """cv2.imshow aborts the process on Linux without a display, so check first."""
    return sys.platform in ("win32", "darwin") or bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def put_label(img, text, x, y, color, scale):
    """Text on a filled box whose bottom-left corner is (x, y)."""
    (tw, th), base = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)
    y = max(y, th + base + 2)
    cv2.rectangle(img, (x, y - th - base - 2), (x + tw + 4, y), color, -1)
    cv2.putText(img, text, (x + 2, y - base), cv2.FONT_HERSHEY_SIMPLEX, scale, WHITE if color != YELLOW else BLACK, 1, cv2.LINE_AA)


def draw_hud(img, lines, scale):
    """Semi-transparent status panel in the top-left corner."""
    h, wd = int(17 * scale / 0.45), int(150 * scale / 0.45)
    panel = img[: h * len(lines) + 6, :wd]
    panel[:] = (panel * 0.35).astype(np.uint8)
    for i, text in enumerate(lines):
        cv2.putText(img, text, (6, h * (i + 1)), cv2.FONT_HERSHEY_SIMPLEX, scale, WHITE, 1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", help="video file (default: 'video' in config) or webcam index, e.g. 0")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--show", action="store_true", help="live window (q/Esc quits, space pauses)")
    ap.add_argument("--save", help="write annotated video, e.g. outputs/annotated.mp4")
    ap.add_argument("--limit", type=float, help="speed limit in km/h (overrides config)")
    ap.add_argument("--out", help="output folder (overrides output_dir in config)")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    source = args.source or cfg["video"]
    limit = args.limit if args.limit is not None else cfg["speed_limit_kmh"]
    out_dir = Path(args.out or cfg.get("output_dir", "outputs"))
    (out_dir / "violations").mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video source: {source}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale = max(0.45, w / 1400)

    model = YOLO(cfg["model"])
    tracker = sv.ByteTrack(frame_rate=fps, track_activation_threshold=cfg["confidence"])
    polygon = np.array(cfg["source"], dtype=np.int32)
    zone = sv.PolygonZone(polygon=polygon)  # keeps detections whose bottom-centre is inside
    transformer = ViewTransformer(polygon, cfg["target_width_m"], cfg["target_length_m"])

    # Per-track state: last ~1 s of (frame_index, y_metres), speed estimates, class votes, frames seen.
    history = defaultdict(lambda: deque(maxlen=int(fps * cfg.get("speed_window_s", 1.0))))
    speeds, votes, seen, violators = defaultdict(list), defaultdict(Counter), defaultdict(int), set()
    cls_of = lambda t: votes[t].most_common(1)[0][0]  # majority class over the track's life
    min_frames = fps / 2  # a track counts as a vehicle once seen for >= 0.5 s (filters flicker)
    vio_file = open(out_dir / "violations.csv", "w", newline="")
    vio_csv = csv.writer(vio_file)
    vio_csv.writerow(["track_id", "class", "speed_kmh", "frame", "video_time_s", "snapshot_path"])

    writer = cv2.VideoWriter(args.save, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)) if args.save else None
    show = args.show and gui_available()
    if args.show and not show:
        print("No display found -- running without --show")
    if show:  # resizable window, initially ~1280 px wide (readable on a projector)
        cv2.namedWindow("Speed detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Speed detection", 1280, int(1280 * h / w))
    t_stage = {"detect": 0.0, "track": 0.0, "speed": 0.0, "annotate_io": 0.0}
    frame_idx, live_fps, t_start = 0, 0.0, time.perf_counter()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t0 = time.perf_counter()
        # 1) DETECT: YOLOv8n on vehicle classes only
        result = model(frame, conf=cfg["confidence"], iou=cfg["iou"], classes=cfg["classes"],
                       agnostic_nms=True, verbose=False)[0]  # one box per vehicle (no car+truck duplicates)
        det = sv.Detections.from_ultralytics(result)
        t1 = time.perf_counter()
        # 2) TRACK: keep detections inside the calibrated zone, then ByteTrack assigns IDs
        det = det[zone.trigger(det)]
        det = tracker.update_with_detections(det)
        t2 = time.perf_counter()
        # 3) SPEED: bottom-centre -> metres; displacement over ~1 s of frames
        pts = transformer.transform(det.get_anchors_coordinates(sv.Position.BOTTOM_CENTER))
        labels, colors = [], []
        for tid, cid, (_, y_m) in zip(det.tracker_id, det.class_id, pts):
            hist = history[tid]
            hist.append((frame_idx, y_m))
            votes[tid][CLASS_NAMES.get(int(cid), str(cid))] += 1
            seen[tid] += 1
            elapsed = hist[-1][0] - hist[0][0]  # frames (robust to missed detections)
            if elapsed < fps / 2:
                labels.append(f"#{tid} {cls_of(tid)}")
                colors.append(GREEN)
                continue
            kmh = abs(hist[-1][1] - hist[0][1]) / (elapsed / fps) * 3.6
            speeds[tid].append(kmh)
            labels.append(f"#{tid} {cls_of(tid)} {kmh:.0f} km/h")
            colors.append(RED if kmh > limit or tid in violators else GREEN)  # violators stay red
        t3 = time.perf_counter()

        # 4) AUTOMATE + ANNOTATE
        out = frame.copy()
        cv2.polylines(out, [polygon], True, YELLOW, 2)
        for (x1, y1, x2, y2), tid, label, color in zip(det.xyxy.astype(int), det.tracker_id, labels, colors):
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
            put_label(out, label, x1, y1 - 2, color, scale)
            if color == RED and tid not in violators:  # first time over the limit: evidence + log
                violators.add(tid)
                snap = frame.copy()
                cv2.rectangle(snap, (x1, y1), (x2, y2), RED, 3)
                put_label(snap, label, x1, y1 - 2, RED, scale)
                stamp = f"VIOLATION {label} > {limit:.0f} | video t={frame_idx / fps:.2f}s | logged {datetime.now():%Y-%m-%d %H:%M:%S}"
                put_label(snap, stamp, 0, h - 1, RED, scale)
                path = out_dir / "violations" / f"track{tid:04d}_frame{frame_idx:05d}.jpg"
                cv2.imwrite(str(path), snap)
                vio_csv.writerow([tid, cls_of(tid), f"{speeds[tid][-1]:.1f}", frame_idx, f"{frame_idx / fps:.2f}", path.as_posix()])
                vio_file.flush()
        inst = 1 / max(time.perf_counter() - t0, 1e-6)
        live_fps = inst if frame_idx < 2 else 0.9 * live_fps + 0.1 * inst
        counted = sum(n >= min_frames for n in seen.values())
        draw_hud(out, [f"FPS: {live_fps:.1f}", f"Vehicles: {counted}", f"Violations: {len(violators)}",
                       f"Limit: {limit:.0f} km/h"], scale)
        if writer:
            writer.write(out)
        if show:
            try:
                cv2.imshow("Speed detection", out)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                if key == ord(" "):
                    cv2.waitKey(0)
            except cv2.error:
                print("No GUI available (headless OpenCV?) -- continuing without --show")
                show = False
        t4 = time.perf_counter()
        for k, dt in zip(t_stage, (t1 - t0, t2 - t1, t3 - t2, t4 - t3)):
            t_stage[k] += dt
        frame_idx += 1

    total = time.perf_counter() - t_start
    cap.release(); vio_file.close()
    if writer:
        writer.release()
    if show:
        cv2.destroyAllWindows()

    # Per-vehicle table and run summary
    with open(out_dir / "vehicles.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["track_id", "class", "max_speed_kmh", "median_speed_kmh", "frames_seen", "violation"])
        for tid in sorted(seen):
            s = speeds[tid]
            wr.writerow([tid, cls_of(tid), f"{max(s):.1f}" if s else "", f"{np.median(s):.1f}" if s else "",
                         seen[tid], int(tid in violators)])
    med = np.array([np.median(s) for s in speeds.values() if s])
    vehicles = [t for t, n in seen.items() if n >= min_frames]
    by_class = Counter(cls_of(t) for t in vehicles)
    cpu = platform.processor() or platform.machine()
    try:
        cpu = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
    except (OSError, StopIteration):
        pass
    summary = {
        "video": Path(str(source)).name, "resolution": [w, h], "fps": round(fps, 2),
        "duration_s": round(frame_idx / fps, 2), "total_frames": frame_idx,
        "track_ids_total": len(seen), "unique_vehicles": len(vehicles),
        "unique_vehicles_note": "tracks seen for >= 0.5 s inside the zone (shorter tracks = detector flicker)",
        "unique_vehicles_by_class": dict(sorted(by_class.items())),
        "vehicles_with_speed_estimate": int(len(med)),
        "speed_kmh_per_vehicle_median": {
            "mean": round(float(med.mean()), 1) if len(med) else None,
            "median": round(float(np.median(med)), 1) if len(med) else None,
            "p85": round(float(np.percentile(med, 85)), 1) if len(med) else None,
            "min": round(float(med.min()), 1) if len(med) else None,
            "max": round(float(med.max()), 1) if len(med) else None},
        "speed_limit_kmh": limit, "violations": len(violators),
        "fraction_of_estimated_vehicles_violating": round(len(violators) / len(med), 3) if len(med) else None,
        "processing_fps": round(frame_idx / total, 1), "cpu": f"{cpu} ({os.cpu_count()} threads)",
        "ms_per_frame": {k: round(1000 * v / max(frame_idx, 1), 1) for k, v in t_stage.items()},
        "calibration": {"source_px": cfg["source"], "target_width_m": cfg["target_width_m"],
                        "target_length_m": cfg["target_length_m"]},
    }
    (out_dir / "results.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
