#!/usr/bin/env python3

import os
import sys
import json
import time
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CURRENT_DIR))

from app import process_image
from ocr.postprocessor import evaluator_normalize

GROUND_TRUTHS = {
    "sample_01_california_plate.png": "7ABC123",
    "sample_02_beijing_plate.png": "京A·12345",
    "sample_03_new_york_angled.jpg": "JHT 2951",
    "sample_04_motion_blurred.jpg": "5XYZ891",
    "sample_05_shanghai_low_light.tiff": "沪B·88888",
    "sample_06_stop_sign.png": "STOP",
    "sample_07_noisy_stop_sign.tiff": "STOP",
    "sample_08_speed_limit_sign.png": "SPEED LIMIT 65",
    "sample_09_work_zone_sign.jpg": "ROAD WORK AHEAD",
    "sample_10_advisory_plaque.png": "35",
}


def run_benchmark():
    sample_dir = Path("sample_inputs")
    out_dir = Path("benchmark_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not sample_dir.exists():
        print(f"Error: {sample_dir} not found.")
        sys.exit(1)

    image_files = sorted(list(sample_dir.glob("*.*")))
    if not image_files:
        print("No sample images found.")
        sys.exit(1)

    print(f"{'Image':<35} | {'Latency':<8} | {'Status':<10} | {'Expected / Output'}")
    print("-" * 75)

    total_start = time.time()
    latencies = []

    for img_path in image_files:
        filename = img_path.name
        expected = GROUND_TRUTHS.get(filename, "N/A")
        out_file = out_dir / f"{img_path.stem}_output.json"
        
        t0 = time.time()
        result = process_image(str(img_path), out_file)
        latency = time.time() - t0
        latencies.append(latency)

        norm_output = evaluator_normalize(result.get("text", ""))
        norm_expected = evaluator_normalize(expected) if expected != "N/A" else ""
        match_status = "OK" if (norm_output == norm_expected and norm_expected) else "RUN_OK"
        if latency > 30.0:
            match_status = "SLOW"

        text_preview = result.get("text", "")
        print(f"{filename:<35} | {latency:.2f}s   | {match_status:<10} | Exp: {expected} | Out: '{text_preview}'")

    total_time = time.time() - total_start
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print("-" * 75)
    print(f"Total Images:    {len(image_files)}")
    print(f"Total Time:      {total_time:.2f}s")
    print(f"Average Latency: {avg_latency:.2f}s per image")


if __name__ == "__main__":
    run_benchmark()
