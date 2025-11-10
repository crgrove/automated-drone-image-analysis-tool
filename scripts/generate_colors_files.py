import csv
import pickle
import cv2
import numpy as np
from pathlib import Path

COLORS = [
    ("Blaze Orange (Hunter Orange)", (255, 103, 0), "Hunting vests, safety jackets, tents, life vests"),
    ("Safety Orange (Traffic Cone Orange)", (255, 83, 0), "Road safety cones, rescue gear"),
    ("Neon Yellow‑Green (Hi‑Vis Lime)", (208, 255, 0), "Construction vests, running gear, EMS uniforms"),
    ("Bright Yellow", (255, 255, 0), "Backpacks, safety gear"),
    ("Bright Red", (220, 20, 60), "Jackets, tents, packs, vehicles"),
    ("Hot Pink (Blaze Pink)", (255, 20, 147), "Safety vests, markers, hunting apparel"),
    ("Magenta (Deep Pink)", (255, 0, 127), "Signal tape, rescue bags"),
    ("Bright Blue (Cyan‑Blue)", (0, 153, 255), "Tarps, jackets, tents"),
    ("Denim Blue (Light)", (93, 138, 168), "Jeans, jackets"),
    ("Dark Denim Blue", (36, 57, 73), "Jeans, workwear"),
    ("Royal Blue", (65, 105, 225), "Clothing, tarps"),
    ("Purple (Bright Violet)", (186, 85, 211), "Jackets, gear, signal flags"),
]

ROOT = Path(__file__).resolve().parents[1]  # → project root
APP_DIR = ROOT / "app"  # → app/
csv_path = APP_DIR / "colors.csv"
pkl_path = APP_DIR / "colors.pkl"


def rgb_to_hsv(r, g, b):
    """
    Convert RGB (0-255) to HSV.
    Returns (h, s, v) where:
    - h: 0-359 (degrees)
    - s: 0-100 (percentage)
    - v: 0-100 (percentage)
    """
    rgb_px = np.uint8([[[r, g, b]]])
    hsv_px = cv2.cvtColor(rgb_px, cv2.COLOR_RGB2HSV)[0][0]
    # OpenCV: H[0-179], S/V[0-255]
    h_deg = int(round(float(hsv_px[0]) * 2.0))  # Convert to 0-359
    s_pct = int(round(float(hsv_px[1]) * (100.0 / 255.0)))  # Convert to 0-100
    v_pct = int(round(float(hsv_px[2]) * (100.0 / 255.0)))  # Convert to 0-100
    return (h_deg, s_pct, v_pct)


def main():
    # CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "r", "g", "b", "h", "s", "v", "uses"])
        writer.writeheader()
        for name, (r, g, b), uses in COLORS:
            h, s, v = rgb_to_hsv(r, g, b)
            writer.writerow({
                "name": name,
                "r": r,
                "g": g,
                "b": b,
                "h": h,
                "s": s,
                "v": v,
                "uses": uses
            })

    # PKL (list of dicts)
    data = []
    for name, (r, g, b), uses in COLORS:
        h, s, v = rgb_to_hsv(r, g, b)
        data.append({
            "name": name,
            "rgb": (r, g, b),
            "hsv": (h, s, v),
            "uses": uses
        })
    with pkl_path.open("wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Wrote {csv_path} and {pkl_path}")


if __name__ == "__main__":
    main()
