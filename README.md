# AMD AI Challenge — Mini-Challenge 2: Optical Character Recognition

Optical Character Recognition application built for AMD ROCm GPU environments, supporting license plates and road signs under challenging visual conditions.

## Project Structure

```text
amd-ocr-challenge/
├── app.py                     # CLI entrypoint
├── Dockerfile                 # ROCm base image setup
├── requirements.txt           # Python dependencies
├── README.md
├── ocr/
│   ├── preprocessor.py        # Image loading and enhancement
│   ├── postprocessor.py       # Transcription cleaning rules
│   ├── vlm_engine.py          # Vision-language model runner
│   └── fallback_engine.py     # Lightweight fallback
├── tests/
│   ├── test_png.py
│   ├── test_jpeg.py
│   ├── test_tiff.py
│   ├── test_rules.py
│   └── generate_sample_images.py
├── sample_inputs/
├── sample_outputs/
└── scripts/
    ├── verify_rocm.py         # Hardware & environment verification
    ├── download_weights.py    # Model weights downloader
    ├── run_benchmark.py       # Latency benchmark
    ├── run_container.sh       # Docker container test (Linux)
    └── run_container.ps1      # Docker container test (Windows)
```

## Setup & Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Sample Images
```bash
python tests/generate_sample_images.py
```

### 3. Run Test Suite
```bash
python -m unittest discover tests
```

### 4. Run Inference
```bash
python app.py --input-image sample_inputs/sample_01_california_plate.png
```

Output is generated at `output/<stem>_output.json`:
```json
{
  "text": "7ABC123",
  "confidence": 0.95
}
```

### 5. Benchmark Latency
```bash
python scripts/run_benchmark.py
```

## Docker Container

### Build
```bash
docker build -t aryan-amd-ocr .
```

### Run
```bash
docker run --rm \
  --device=/dev/kfd --device=/dev/dri --security-opt seccomp=unconfined \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  aryan-amd-ocr \
  python3 /app/app.py --input-image /app/input/test1.png
```

Or run the test script:
```bash
./scripts/run_container.sh sample_inputs/sample_01_california_plate.png
```

