#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from ocr.preprocessor import preprocess_image_file
from ocr.postprocessor import postprocess_transcription
from ocr.vlm_engine import get_vlm_engine


def determine_output_path(input_path: str, custom_output_dir: str = None) -> Path:
    input_p = Path(input_path)
    output_filename = f"{input_p.stem}_output.json"

    if custom_output_dir:
        out_dir = Path(custom_output_dir)
    elif str(input_p).startswith("/app/input") or os.path.exists("/app/output"):
        out_dir = Path("/app/output")
    else:
        out_dir = Path("output")

    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / output_filename


def process_image(input_image_path: str, output_path: Path) -> dict:
    start_time = time.time()
    print(f"[{time.strftime('%X')}] Processing image: {input_image_path}")

    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input image not found: {input_image_path}")

    preprocessed_img = preprocess_image_file(input_image_path)
    
    vlm = get_vlm_engine()
    raw_text, confidence = vlm.predict(preprocessed_img)
    final_text = postprocess_transcription(raw_text)

    result_data = {
        "text": final_text,
        "confidence": round(float(confidence), 2)
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"[{time.strftime('%X')}] Done in {elapsed:.2f}s -> {output_path}")
    print(f"[{time.strftime('%X')}] Transcription: '{final_text}' (Confidence: {confidence:.2f})")
    
    return result_data


def main():
    parser = argparse.ArgumentParser(description="OCR Inference Application")
    parser.add_argument("--input-image", required=True, type=str, help="Path to input image file")
    parser.add_argument("--output-dir", type=str, default=None, help="Optional output directory")

    raw_args = sys.argv[1:]
    while raw_args and (raw_args[0] in ("python", "python3") or raw_args[0].endswith("app.py")):
        raw_args = raw_args[1:]

    args = parser.parse_args(raw_args)

    try:
        output_file_path = determine_output_path(args.input_image, args.output_dir)
        process_image(args.input_image, output_file_path)
        sys.exit(0)
    except Exception as e:
        print(f"Error processing image: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
