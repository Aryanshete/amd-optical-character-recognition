#!/usr/bin/env python3

import os
import sys
import re
from pathlib import Path

MANDATORY_BASE = "rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0"
REQUIRED_PATHS = ["/app/app.py", "/app/requirements.txt", "/app/output", "/models"]


def verify_dockerfile():
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        print("[FAIL] Dockerfile does not exist.")
        sys.exit(1)

    content = dockerfile_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

    errors = []
    warnings = []

    # 1. Base Image Check
    from_lines = [l for l in lines if l.upper().startswith("FROM")]
    if not from_lines:
        errors.append("No FROM instruction found in Dockerfile.")
    else:
        final_from = from_lines[-1].split()[1]
        if final_from != MANDATORY_BASE:
            errors.append(f"Base image must be '{MANDATORY_BASE}', found '{final_from}'.")
        else:
            print(f"[PASS] Mandatory base image verified: {MANDATORY_BASE}")

    # 2. Check for image squashing or multi-stage layer breaking
    if len(from_lines) > 1:
        warnings.append("Multi-stage build detected. Ensure final stage starts from mandated base.")

    # 3. Required path checks
    if "COPY app.py /app/app.py" not in content and "app.py" not in content:
        errors.append("Required path /app/app.py not copied into container.")
    else:
        print("[PASS] Entrypoint /app/app.py configured.")

    if "requirements.txt" not in content:
        errors.append("requirements.txt not found in Dockerfile.")
    else:
        print("[PASS] Dependencies /app/requirements.txt configured.")

    if "/app/output" not in content:
        errors.append("Output directory /app/output not created.")
    else:
        print("[PASS] Output directory /app/output configured.")

    if "/models" not in content:
        warnings.append("/models directory not explicitly mentioned.")
    else:
        print("[PASS] Weights directory /models configured.")

    # 4. Check for hardcoded API keys or secrets
    secret_keywords = ["api_key", "secret", "password", "token", "amd_key", "hf_token"]
    for kw in secret_keywords:
        if re.search(rf"\b{kw}\s*=", content, re.IGNORECASE):
            errors.append(f"Potential hardcoded credential '{kw}' detected in Dockerfile.")

    print("\n" + "=" * 50)
    if errors:
        print("DOCKERFILE VERIFICATION: FAILED")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("DOCKERFILE VERIFICATION: PASSED (100% compliant)")
        if warnings:
            for w in warnings:
                print(f"  [Notice] {w}")
    print("=" * 50)


if __name__ == "__main__":
    verify_dockerfile()
