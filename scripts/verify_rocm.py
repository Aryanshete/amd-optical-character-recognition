#!/usr/bin/env python3

import sys
import shutil
import subprocess


def check_rocm_gpu():
    print("Python:", sys.version.split()[0])

    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        hip_version = getattr(torch.version, "hip", None)
        print(f"CUDA/ROCm Available: {cuda_avail}")
        print(f"ROCm/HIP Version:    {hip_version}")

        if cuda_avail:
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i)
                vram = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)
                print(f"GPU [{i}]: {name} ({vram:.2f} GiB)")
        else:
            print("No ROCm/CUDA GPU detected. Running on CPU.")

    except ImportError:
        print("PyTorch is not installed.")

    amd_smi = shutil.which("amd-smi") or shutil.which("rocm-smi")
    if amd_smi:
        print(f"SMI tool: {amd_smi}")
        try:
            res = subprocess.run([amd_smi, "metric", "--mem"], capture_output=True, text=True, timeout=5)
            if res.stdout:
                print(res.stdout.strip())
        except Exception:
            pass

    for mount in ["/persistent", "/workspace", ".", "/app"]:
        try:
            usage = shutil.disk_usage(mount)
            total = usage.total / (1024 ** 3)
            free = usage.free / (1024 ** 3)
            print(f"Mount '{mount}': {free:.1f} GiB free / {total:.1f} GiB")
        except Exception:
            pass


if __name__ == "__main__":
    check_rocm_gpu()
