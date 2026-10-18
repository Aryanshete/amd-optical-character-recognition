# AMD AI Challenge — Mini-Challenge 2: Optical Character Recognition

High-performance, robust Optical Character Recognition solution built for the **AMD AI Challenge Mini-Challenge 2 (License Plates and Road Signs)** on the mandated **AMD ROCm PyTorch base image**.

---

## 1. Solution Architecture

```
                                  +-------------------------------------------------------------+
                                  |                 Docker Container (ROCm Base)                |
                                  |                                                             |
Grader: docker run -d <image> --->|  [app/server.py]                                            |
                                  |  - Starts at container launch (ENTRYPOINT)                  |
                                  |  - Loads Qwen2.5-VL-3B-Instruct in bfloat16 into GPU VRAM   |
                                  |  - Pre-warms GPU kernels (compilation paid at startup)       |
                                  |  - Serves http://127.0.0.1:8765 (/health and /ocr)          |
                                  |  - Stays resident throughout all test image evaluations     |
                                  +-------------------------------------------------------------+
                                                                ^
Grader: docker exec <image>                                     |  HTTP POST /ocr (1-2s latency)
  python3 /app/app.py                                           |
  --input-image /app/input/01.png ------------------------------+
                                                                |
                                                                v
                                              Writes /app/output/01_output.json
                                              {"text": "...", "confidence": 0.94}
                                              Exits 0 immediately
```

### Key Components

- **Resident Server (`app/server.py`)**: Runs as `ENTRYPOINT`, loads model weights once during the 10-minute startup budget, pre-warms kernels with a dummy generation, and listens on port 8765.
- **Grader Invocator (`app/app.py`)**: Called per image by `docker exec`. Sends image path to `127.0.0.1:8765/ocr`, writes `/app/output/<stem>_output.json`, and exits with code 0 in ~1-2 seconds (well within the 30-second budget). Includes fallback in-process execution with deadline guards.
- **OCR Engine (`app/ocr_engine.py`)**:
  - **Model**: `Qwen/Qwen2.5-VL-3B-Instruct` (~6.5 GB weights, ~7.5 GiB VRAM allocation, 1-2s inference per pass).
  - **Test-Time Augmentation (TTA)**: 3-pass majority voting with condition-aware preprocessing:
    - Automatically measures image noise (`_noise_level`); applies median filtering on noisy images (e.g., TIFF sensor noise).
    - Measures luminance; applies adaptive brightness on underexposed images with glare (e.g., Shanghai plate).
    - Applies autocontrast and sharpening.
  - **Domain-Specific Prompts & Post-Processing**:
    - Drops US state names, slogans, and DMV/government URLs printed around plate numbers.
    - Preserves Chinese province characters and letters (e.g., `京A`, `沪B`), while fixing OCR confusion of `I`/`O` into digits `1`/`0`.
    - Transcribes multi-line road signs top-to-bottom joined by single spaces (e.g., `ROAD WORK AHEAD`, `SPEED LIMIT 65`).
    - Outputs digits alone for advisory speed plaques without units (e.g., `35`).
- **Healthcheck (`app/healthcheck.py`)**: Docker healthcheck to signal when the resident model is loaded and ready.
- **Model Downloader (`app/download_model.py`)**: Bakes weights into `/models` at build time so the container requires zero network access at runtime.

---

## 2. Challenge Rules & Constraints Checklist

| Gate / Requirement | Specification | Our Implementation | Status |
| :--- | :--- | :--- | :--- |
| **Base Image** | Mandated `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0` | Exact base image used without squashing/flattening | **PASS** |
| **Container Size** | Uncompressed < 60 GiB | Total uncompressed size ~28 GiB | **PASS** |
| **VRAM Usage** | Peak between 1 GiB and 48 GiB | `Qwen2.5-VL-3B-Instruct` bf16 uses ~7.5 GiB VRAM | **PASS** |
| **Startup Budget** | < 10 minutes | Server loads and pre-warms in ~25-40 seconds | **PASS** |
| **Per-Image Budget** | < 30 seconds per image | Average inference time is ~1.5 - 3.0 seconds | **PASS** |
| **Image Formats** | PNG, JPEG, TIFF (including 16-bit) | Handled by `load_image()` | **PASS** |
| **Output Contract** | `/app/output/<stem>_output.json` with `text` & `confidence` | Strictly enforced | **PASS** |
| **No Secrets** | No `.env` or API keys | Offline weights, zero secrets | **PASS** |

---

## 3. Free Deployment via GitHub Actions & GHCR

The automated workflow in `.github/workflows/publish-docker.yml` builds and pushes the Docker container directly to **GitHub Container Registry (GHCR)** using free GitHub-hosted runners.

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "feat: complete AMD Mini-Challenge 2 OCR solution"
git push origin main
```

### Step 2: GitHub Actions Build
The workflow `.github/workflows/publish-docker.yml` triggers automatically on push to `main`. It:
1. Maximizes build disk space on the Ubuntu runner using `easimon/maximize-build-space`.
2. Builds the Docker image from `Dockerfile` (installing ROCm dependencies and baking `Qwen2.5-VL-3B-Instruct` into `/models`).
3. Pushes the image to GitHub Container Registry:
   - `ghcr.io/aryanshete/amd-optical-character-recognition:latest`
   - `ghcr.io/aryanshete/amd-optical-character-recognition:sha-<commit_sha>`

### Step 3: Make the Image Public (CRITICAL!)
Because the challenge evaluation harness pulls your container anonymously without credentials:
1. Go to your GitHub Profile: `https://github.com/Aryanshete?tab=packages`
2. Click on the package: `amd-optical-character-recognition`
3. Click **Package settings** (on the right sidebar).
4. Scroll down to **Danger Zone** -> **Change package visibility**.
5. Select **Public**, type the package name to confirm, and click **I understand the consequences, make this package public**.

---

## 4. Submission Link for Mini Challenge 2

In your LabLab submission dashboard under **Mini Challenge 2 Image**, enter:

```text
ghcr.io/aryanshete/amd-optical-character-recognition:latest
```
*(Or specify the exact tag: `ghcr.io/aryanshete/amd-optical-character-recognition:sha-<sha>`)*

> **Note**: Do NOT enter the GitHub repository URL (`https://github.com/...`). The grader requires a publicly pullable Docker container image reference.

---

## 5. Local Testing & Verification

Run the test suite:
```bash
python -m unittest discover tests
```

To run against the synthetic test set:
```bash
python scripts/make_test_images.py
python scripts/test_local.py --images test_images
```

To test against real PDF test samples:
```bash
python scripts/test_local.py --images test_images_real
```
