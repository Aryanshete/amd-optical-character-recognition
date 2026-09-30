#!/usr/bin/env bash
set -e

IMAGE_NAME="aryan-amd-ocr"
TEST_IMG="${1:-sample_inputs/sample_01_california_plate.png}"
IMG_FILENAME=$(basename "$TEST_IMG")
IMG_STEM="${IMG_FILENAME%.*}"

docker build -t "$IMAGE_NAME" .

mkdir -p input output
cp "$TEST_IMG" "input/$IMG_FILENAME"

docker run --rm \
  --device=/dev/kfd --device=/dev/dri --security-opt seccomp=unconfined \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  "$IMAGE_NAME" \
  python3 /app/app.py --input-image "/app/input/$IMG_FILENAME"

OUTPUT_FILE="output/${IMG_STEM}_output.json"
if [ -f "$OUTPUT_FILE" ]; then
    cat "$OUTPUT_FILE"
else
    echo "Output $OUTPUT_FILE was not created"
    exit 1
fi
