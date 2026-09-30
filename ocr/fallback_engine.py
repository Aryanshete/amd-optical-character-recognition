from typing import Tuple, Optional
from PIL import Image
import torch

_easyocr_reader: Optional[object] = None


def get_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        use_gpu = torch.cuda.is_available()
        _easyocr_reader = easyocr.Reader(['en', 'ch_sim'], gpu=use_gpu)
    return _easyocr_reader


def run_fallback_ocr(image: Image.Image) -> Tuple[str, float]:
    try:
        reader = get_reader()
        import numpy as np
        img_np = np.array(image)
        results = reader.readtext(img_np)
        if results:
            results.sort(key=lambda x: x[0][0][1])
            text_lines = [r[1] for r in results]
            confidences = [r[2] for r in results]
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.8
            return "\n".join(text_lines), round(float(avg_conf), 2)
    except Exception:
        pass

    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        if text.strip():
            return text.strip(), 0.85
    except Exception:
        pass

    return "", 0.0
