# Vehicle speed detection demo

Live demo for the *Computer Vision & Automation* talk. The running example is speed
enforcement on the GD Naidu flyover in Coimbatore, with a 60 km/h limit.

```
frame ─► YOLOv8n (detect) ─► ByteTrack (IDs) ─► perspective transform (px → m) ─► speed ─► rule: speed > limit?
                                                                                         └─► red box + snapshot + CSV row
```

The design follows Roboflow's published speed-estimation example
(`supervision/examples/speed_estimation`):

- **Detect.** Ultralytics YOLOv8n, pretrained on COCO. It keeps only car (2), motorcycle (3),
  bus (5) and truck (7), and uses class-agnostic NMS so each vehicle gets one box.
- **Track.** Only detections whose bottom-centre point lies inside the calibrated zone are
  passed to `sv.ByteTrack`, which gives each vehicle a persistent ID.
- **Pixels to metres.** `cv2.getPerspectiveTransform` maps the 4-point road trapezoid
  (`source` in `config.yaml`) onto a rectangle of `target_width_m × target_length_m` metres.
  This gives a bird's-eye view.
- **Speed.** Each track keeps a deque of `(frame_index, y_metres)` covering about 1 s of
  frames. The speed is `|y_last − y_first| / (elapsed_frames / fps) × 3.6` km/h. It is reported
  only after at least `fps/2` frames have elapsed. Elapsed time comes from the frame indices,
  so a missed detection does not distort the speed.
- **Automation rule.** When a vehicle's speed exceeds the limit, its box turns red and stays
  red. The first time this happens for a track, the script saves one evidence JPG (box, ID,
  speed, video time, log time) to `outputs/violations/` and appends a row to
  `outputs/violations.csv`. There is no number-plate reading (ANPR).

## Files

| File | Purpose |
|---|---|
| `speed_detection.py` | The demo: detect, track, measure speed, apply the rule. Writes the outputs listed below. |
| `config.yaml` | **Edit this on the day.** Video, model, confidence, speed limit, calibration points and metres. |
| `calibrate.py` | Click 4 road points (interactive), or `--check` to save the current polygon and bird's-eye view. |
| `make_slide_assets.py` | Builds the PNGs and GIFs for the slides. Not needed live. |
| `requirements.txt` | Pinned, tested versions. |
| `data/traffic.mp4` | Footage (gitignored; download it, see below). |
| `yolov8n.pt` | Model weights (gitignored; auto-downloads, or use curl below). |

## Setup (once, before the day)

```bash
cd cv-automation-ppt/demo
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Footage (about 1.4 MB) and weights (about 6.5 MB):
mkdir -p data
curl -L -o data/traffic.mp4 https://raw.githubusercontent.com/kraten/vehicle-speed-check/master/cars.mp4
curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
```

- **Linux laptop without a GPU.** The PyPI `torch` wheel bundles CUDA libraries (several GB).
  To avoid that, first run
  `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` and then
  install the requirements. Windows and macOS wheels are CPU-only already.
- **OpenCV build.** Install only `opencv-python`, which has the GUI. If `opencv-python-headless`
  is also installed, `--show` stops working; uninstall both and reinstall `opencv-python`.
- **`supervision` version.** It is pinned to `0.30.7` because `sv.ByteTrack` was removed in 0.31.

## Run

```bash
# Live demo window (q / Esc quits, space pauses)
python speed_detection.py --source data/traffic.mp4 --show

# Headless: save the annotated video plus CSV/JSON results to outputs/
python speed_detection.py --source data/traffic.mp4 --save outputs/annotated.mp4

# Change the speed limit without editing the config
python speed_detection.py --source data/traffic.mp4 --show --limit 50

# Version shown on the slides (lower limit so the rule fires on this footage), kept in its own folder
python speed_detection.py --limit 50 --out outputs/demo_limit50 --save outputs/demo_limit50/annotated.mp4

# Slide images and GIFs (run the two commands above first)
python make_slide_assets.py

# Calibration
python calibrate.py --source data/traffic.mp4               # click 4 points (needs a display)
python calibrate.py --check                                 # outputs/calibration_check.png
python calibrate.py --check --background --out outputs/calibration_check_background.png  # median, car-free frame
```

### Outputs (`outputs/`)

| Output | Content |
|---|---|
| `annotated.mp4` | Annotated video (gitignored). |
| `vehicles.csv` | One row per track: id, class (majority vote), max and median speed, frames seen, violation flag. |
| `violations.csv`, `violations/*.jpg` | Evidence log and snapshots. |
| `results.json` | Video info, vehicles by class, speed statistics, violations and violation fraction, processing FPS, CPU, and ms/frame for detect, track, speed and annotate/IO. |
| Slide images | `frame_raw.png`, `frame_detections.png` (YOLO boxes and confidence only), `frame_tracked.png` (IDs and speeds), `homography_before.png` and `homography_after.png` (bird's-eye view, 24 px/m, metre ruler), `violation_example.png`, `background_subtraction.png` (MOG2 baseline), `calibration_check*.png`. |
| GIFs | `annotated_preview.gif` and `annotated_preview_demo_limit50.gif` (6 s, 640 px, 2–4 MB), `tracking_preview.gif` (camera view with trails next to the bird's-eye view). |
| `demo_limit50/` | The same outputs for the 50 km/h run. |

## Results on the sample footage (CPU only)

The 60 km/h run (`outputs/results.json`) found 34 vehicles in 47.6 s: 30 cars, 3 buses and
1 truck. All 34 have a speed estimate.

| Statistic | Value |
|---|---|
| Speed per vehicle (median of its estimates) | mean 35.6, median 37.0, p85 47.0, max 55.6 km/h |
| Violations at 60 km/h | **0 (0 %)** |
| Violations at 50 km/h (demo run) | **5 of 34 (14.7 %)**: 50.1–58.2 km/h |
| Processing speed | about 24 FPS end-to-end on an Intel Xeon @ 2.1 GHz (4 threads). Detection is about 36 ms/frame, tracking about 1.5 ms, speed calculation 0.1 ms. |

**Why the speeds are believable:**

- **Frame rate.** The burned-in clock runs from 12:21:25 to 12:22:12 over 1,190 frames, which
  confirms the clip is real-time at 25 fps.
- **Dash pattern.** Fitting the dash ends gives a dash-to-period ratio of 0.35. That matches the
  2 m line + 4 m gap pattern (0.33) better than the 6 m + 9 m highway pattern (0.40). With the
  6 + 9 pattern, every speed would be 2.5× higher (median about 93 km/h), which is implausible
  for an urban road with a bus stop.
- **Lane width.** The 3.5 m lanes and 6 m dash period together imply a camera with about a 59°
  horizontal field of view (f ≈ 565 px). That is a normal CCTV lens, so the two assumptions agree.
- **Independent check.** A separate 1-D fit of the dash rows reproduces the pipeline's speeds to
  within about 2 km/h for four checked cars.
- **Stopped buses.** Buses waiting at the stop read 0–3 km/h, which is correct.

**Note for the talk:** this footage is an urban arterial with typical speeds of 30–55 km/h, so
nothing exceeds 60. For the live demo, either say so ("everyone is under 60 here") or run with
`--limit 50` to show the rule firing, and name the threshold you are using.

## Calibration used for the sample footage

`config.yaml` sets `source = [[203,84],[389,84],[583,321],[48,321]]` on the 640×360 frame. The
zone is **14 m wide × 30 m long**.

- **Along the road (30 m).** This is the only dimension speed depends on. The lane lines are
  dashed with a 2 m dash and a 4 m gap, which is the Chinese GB 5768 pattern for urban roads
  below 60 km/h; the dash/period fit above supports it. The top and bottom rows of the zone are
  at dash ends exactly 5 periods apart: 5 × 6 m = 30 m.
- **Across the road (14 m).** 4 lanes × 3.5 m is an assumption (the usual urban lane width,
  3.5–3.75 m). The homography was solved from the two inner dashed lane lines (7 m apart) and
  extended to 4 lanes. Errors in width only affect the x-axis of the bird's-eye view, not the
  speed.

## Recalibrating for the GD Naidu flyover (4-point method)

Every camera view needs its own calibration. The numbers above apply only to the sample clip.

1. **Get footage.** Use a fixed, elevated camera looking along the carriageway, for example
   from a footbridge or a pole. A slight downward angle with lane markings visible over
   30–60 m works best. Lock the zoom and focus.
2. **Choose a ground rectangle.** Two lane lines (or kerb lines) form the long sides. Two rows
   across the road at dash ends form the short sides.
3. **Measure it in metres:**
   - **Length:** count dash periods and multiply by the period length. Check the period on
     site with a measuring wheel or tape, or against the IRC:35 road-marking code. Do not
     assume the Chinese 2 + 4 m pattern.
   - **Width:** measure lane width on site or from satellite imagery. Indian urban lanes are
     about 3.5 m; the flyover may differ.
4. **Record the pixel corners.** Run `python calibrate.py --source flyover.mp4 --background` and
   click top-left, top-right, bottom-right, bottom-left. Paste the printed points into `source:`
   and set `target_width_m` and `target_length_m`.
5. **Check the result.** Run `python calibrate.py --check`. In the bird's-eye half, the lane
   lines must be vertical and parallel and the dashes evenly spaced.
6. **Validate with a known speed.** Drive a car through at a steady 40 km/h on cruise control
   or with GPS, and confirm the reading is within a few km/h. Also check that typical traffic
   gives plausible values.

## Live-demo checklist

- [ ] `pip install -r requirements.txt` is done on the presentation laptop, and
      `data/traffic.mp4` and `yolov8n.pt` are present, so no internet is needed on stage.
- [ ] Test run with `python speed_detection.py --show`: the window opens and FPS is above 10.
      If the laptop is slow, it still works, just more slowly.
- [ ] Decide the limit you will state: 60 (story; 0 violations on this clip) or `--limit 50`
      (5 violations).
- [ ] `outputs/` is cleared or contains the expected snapshots, so you can open
      `outputs/violations/` and `violations.csv` live after the run.
- [ ] Backup: `outputs/annotated.mp4`, `outputs/demo_limit50/annotated.mp4` and the GIFs, in
      case the live run fails.
- [ ] Explain that boxes appear only inside the yellow zone. That is the measurement area, and
      vehicles below or above it are deliberately ignored.
- [ ] Keys: **space** pauses (good for pointing at a label), **q** quits.

## Footage source and licence

- **Clip:** `cars.mp4` from <https://github.com/kraten/vehicle-speed-check>, downloaded from
  <https://raw.githubusercontent.com/kraten/vehicle-speed-check/master/cars.mp4> (commit
  `d830b17`, 2022). It is 640×360, 25 fps, 47.6 s, and was not trimmed. The overlay reads
  "Camera-1, 2016/03/18": a fixed elevated traffic camera over a multi-lane urban road (Chinese
  road markings) with a bus stop, and traffic moving away from the camera.
- **Licence:** the repository has no licence file, so no reuse rights are granted. Default
  copyright applies, and the original rights holder of the CCTV footage is unknown. It is used
  here only for a non-commercial classroom demonstration with attribution. The clip is
  gitignored and downloaded by URL, not redistributed. Replace it with your own flyover footage
  before any public or commercial use, including the GIFs and PNGs derived from it.
- **Alternatives checked:** Intel IoT DevKit sample videos (CC-BY 4.0, but no usable highway
  view), Ultralytics assets, Roboflow `vehicles.mp4` (hosted on media.roboflow.com and not
  reachable from the build machine), and several GitHub repos. None was a better licensed,
  fixed highway view.
- **Code and models:** Ultralytics YOLOv8 is AGPL-3.0, `supervision` is MIT, and OpenCV is
  Apache-2.0.

## Assumptions and limitations

- **Flat road.** The ground is assumed to be a plane, so the homography is valid only inside
  and near the zone. Flyover slope or curvature needs a zone short enough to be roughly flat.
- **Ground contact point.** The bottom-centre of the box is taken as where the vehicle touches
  the road. For tall vehicles seen at an angle, or vehicles changing lanes, this shifts. The
  1 s window smooths jitter to about ±2 km/h. Speed uses only the along-road component.
- **Calibration error.** Speed error equals the error in `target_length_m`: a 5 % length error
  gives a 5 % speed error. Rounding the pixel corners costs about 0.5 %.
- **Detector limits.** YOLOv8n is small: distant vehicles (above the zone), heavy occlusion,
  night and rain reduce detection. Buses and minibuses are sometimes labelled "truck", and a
  majority vote over each track fixes most of these. The far-lane opposite carriageway is
  excluded by the zone.
- **Not enforcement-grade.** There is no ANPR, no certified timing, no sensor fusion and no
  lens-distortion correction (a slight barrel distortion is visible). Real enforcement uses
  certified radar or lidar, or section-average cameras.
- **Violation trigger.** A violation fires on the first 1 s estimate above the limit. A single
  noisy estimate just above the threshold can trigger it. A production system would require a
  margin or several consecutive readings.
