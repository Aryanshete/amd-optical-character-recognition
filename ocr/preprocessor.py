from typing import Tuple
from PIL import Image, ImageEnhance, ImageFilter, ImageStat


def load_image(image_path: str) -> Image.Image:
    img = Image.open(image_path)
    if hasattr(img, "n_frames") and img.n_frames > 1:
        img.seek(0)
    
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        return background
    elif img.mode != "RGB":
        return img.convert("RGB")
    
    return img


def analyze_image_stats(img: Image.Image) -> Tuple[float, float]:
    grayscale = img.convert("L")
    stat = ImageStat.Stat(grayscale)
    return stat.mean[0], stat.stddev[0]


def enhance_image(
    img: Image.Image,
    min_dimension: int = 512,
    max_dimension: int = 2048,
    enable_contrast_boost: bool = True,
    enable_sharpening: bool = True
) -> Image.Image:
    w, h = img.size
    min_side = min(w, h)
    
    if min_side < min_dimension:
        scale_factor = min_dimension / float(min_side)
        img = img.resize((int(w * scale_factor), int(h * scale_factor)), resample=Image.Resampling.BICUBIC)
    elif max(w, h) > max_dimension:
        scale_factor = max_dimension / float(max(w, h))
        img = img.resize((int(w * scale_factor), int(h * scale_factor)), resample=Image.Resampling.LANCZOS)
    
    if enable_contrast_boost:
        mean_lum, std_lum = analyze_image_stats(img)
        if mean_lum < 75.0:
            img = ImageEnhance.Brightness(img).enhance(1.35)
            img = ImageEnhance.Contrast(img).enhance(1.25)
        elif mean_lum > 210.0:
            img = ImageEnhance.Brightness(img).enhance(0.85)
            img = ImageEnhance.Contrast(img).enhance(1.30)
        elif std_lum < 35.0:
            img = ImageEnhance.Contrast(img).enhance(1.40)
    
    if enable_sharpening:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))
        
    return img


def preprocess_image_file(image_path: str) -> Image.Image:
    return enhance_image(load_image(image_path))
