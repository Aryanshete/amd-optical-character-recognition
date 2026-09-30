#!/usr/bin/env python3

import argparse
import os
import sys


def download_model(model_name: str, target_dir: str):
    print(f"Downloading {model_name} to {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        from huggingface_hub import snapshot_download
        downloaded_path = snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
        )
        print(f"Downloaded to: {downloaded_path}")
    except ImportError:
        print("huggingface_hub is required. Install via: pip install huggingface_hub", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to download model: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download model weights")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-VL-7B-Instruct")
    parser.add_argument("--output-dir", type=str, default="./models")
    args = parser.parse_args()
    download_model(args.model, args.output_dir)


if __name__ == "__main__":
    main()
