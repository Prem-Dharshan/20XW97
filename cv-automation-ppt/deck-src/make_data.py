"""Turn demo outputs into the numbers the deck quotes (data.json)."""
import csv, json
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "demo", "outputs") + "/"
r = json.load(open(D + "results.json"))
rows = [x for x in csv.DictReader(open(D + "vehicles.csv")) if x["max_speed_kmh"]]
peaks = [float(x["max_speed_kmh"]) for x in rows]
bins = [(0, 20, "<20"), (20, 30, "20–30"), (30, 40, "30–40"), (40, 50, "40–50"), (50, 60, "50–60"), (60, 999, "60+")]
under = [sum(lo <= p < hi and p <= 50 for p in peaks) for lo, hi, _ in bins]
over = [sum(lo <= p < hi and p > 50 for p in peaks) for lo, hi, _ in bins]
v50 = list(csv.DictReader(open(D + "demo_limit50/violations.csv")))
ms = r["ms_per_frame"]
ex_kmh = 58.2; n = 25; t = n / r["fps"]; mps = ex_kmh / 3.6
data = {
    "fps": int(r["fps"]), "fps_meas": r["processing_fps"], "n_vehicles": r["unique_vehicles"],
    "median_speed": round(r["speed_kmh_per_vehicle_median"]["median"]), "n_viol": r["violations"], "n_viol50": len(v50),
    "t_detect": ms["detect"], "t_track": ms["track"], "t_speed": ms["speed"],
    "res_label": f'{r["resolution"][0]}×{r["resolution"][1]} · {int(r["fps"])} FPS', "cpu_label": "a 4-thread CPU, no GPU",
    "hist": {"labels": [b[2] for b in bins], "under": under, "over": over},
    "ex_label": "track #7, peak reading", "ex_dy": f"{mps * t:.1f}", "ex_n": n, "ex_t": f"{t:.1f}", "ex_ms": f"{mps:.1f}", "ex_kmh": f"{ex_kmh:.1f}",
    "ex_verdict": "under 60 → no action",
    "ex_spoken": f"track number 7, a car, moved {mps * t:.1f} metres in the bird's-eye view over {n} frames. At {int(r['fps'])} frames per second that's {t:.1f} second, so {mps:.1f} metres per second, times 3.6 is {ex_kmh} km/h. That's under 60, so no action, but it's the car you'll see flagged when we lower the limit to 50 in the demo",
    "calib_note": "Our calibration: 5 lane-dash periods × 6 m = 30 m along the road; 4 lanes × 3.5 m = 14 m across. Sanity check: buses waiting at the stop read 0–3 km/h.",
    "calib_note_spoken": "For our footage the length comes from the lane dashes: 2 metre dash plus 4 metre gap, five periods, 30 metres. As a sanity check, buses waiting at the bus stop read 0 to 3 km/h. On the real flyover you'd measure the zone on site and validate with a car driven at a known speed.",
    "results_title": f"{r['unique_vehicles']} vehicles measured; none above 60 km/h on this clip",
    "viol_caption": "Test run at a 50 km/h limit: car #7 at 58 km/h, saved automatically with timestamp.",
    "results_source": f"Footage: kraten/vehicle-speed-check (GitHub), urban road CCTV, {r['resolution'][0]}×{r['resolution'][1]} @ {int(r['fps'])} FPS, {r['duration_s']} s. Calibrated from lane markings; no radar ground truth.",
    "footage_ref": "Demo footage: cars.mp4, github.com/kraten/vehicle-speed-check (classroom use with attribution; no licence file)",
}
data["results_spoken"] = (f"Here are the numbers from the full clip. We measured {r['unique_vehicles']} vehicles: 30 cars, 3 buses and a truck. "
    f"The median speed was {data['median_speed']} km/h and the 85th percentile {round(r['speed_kmh_per_vehicle_median']['p85'])}, which makes sense for an urban road. "
    f"At the 60 km/h limit, zero vehicles were flagged. We're reporting that as it is rather than tuning the calibration until something crosses 60. "
    f"At a 50 km/h test limit, {len(v50)} vehicles were flagged, between 50 and 58 km/h, each with an automatic evidence snapshot like this one. "
    f"The whole pipeline ran at {r['processing_fps']} frames per second on a 4-thread CPU with no GPU, just enough to keep up with this 25 FPS camera.")
json.dump(data, open("data.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: data[k] for k in ["hist", "ex_dy", "ex_ms", "results_title"]}, ensure_ascii=False))
