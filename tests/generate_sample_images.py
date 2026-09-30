import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("sample_inputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_font(size: int = 40, font_family: str = "arial.ttf"):
    candidates = [
        font_family,
        f"C:\\Windows\\Fonts\\{font_family}",
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_chinese_font(size: int = 40):
    candidates = [
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
        "C:\\Windows\\Fonts\\simsun.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return get_font(size)


def add_gaussian_noise(image: Image.Image, intensity: int = 40) -> Image.Image:
    img = image.copy()
    w, h = img.size
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            if random.random() < 0.25:
                noise = random.randint(-intensity, intensity)
                r, g, b = pixels[x, y][:3]
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )
    return img


def generate_all_samples():
    print(f"Generating test images in {OUTPUT_DIR.resolve()}...")

    # California Plate
    img1 = Image.new("RGB", (500, 250), color=(240, 240, 240))
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([(10, 10), (490, 240)], outline=(30, 30, 100), width=4)
    font_small = get_font(22)
    d1.text((180, 25), "CALIFORNIA", fill=(180, 20, 20), font=font_small)
    font_large = get_font(56)
    d1.text((130, 90), "7ABC123", fill=(20, 30, 120), font=font_large)
    d1.text((150, 195), "dmv.ca.gov", fill=(100, 100, 100), font=font_small)
    img1.save(OUTPUT_DIR / "sample_01_california_plate.png")

    # Beijing Plate
    img2 = Image.new("RGB", (500, 250), color=(20, 50, 140))
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([(10, 10), (490, 240)], outline=(255, 255, 255), width=3)
    c_font = get_chinese_font(52)
    d2.text((100, 90), "京A·12345", fill=(255, 255, 255), font=c_font)
    img2.save(OUTPUT_DIR / "sample_02_beijing_plate.png")

    # New York Plate
    img3 = Image.new("RGB", (500, 250), color=(245, 210, 50))
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([(10, 10), (490, 240)], outline=(10, 10, 50), width=4)
    d3.text((180, 25), "NEW YORK", fill=(10, 10, 50), font=font_small)
    d3.text((120, 90), "JHT 2951", fill=(10, 10, 50), font=font_large)
    d3.text((160, 195), "EMPIRE STATE", fill=(10, 10, 50), font=font_small)
    img3 = img3.rotate(12, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(200, 200, 200))
    img3.save(OUTPUT_DIR / "sample_03_new_york_angled.jpg", "JPEG", quality=92)

    # Motion-Blurred Plate
    img4 = Image.new("RGB", (500, 250), color=(240, 240, 240))
    d4 = ImageDraw.Draw(img4)
    d4.rectangle([(10, 10), (490, 240)], outline=(40, 40, 40), width=3)
    d4.text((130, 90), "5XYZ891", fill=(20, 20, 20), font=font_large)
    img4 = img4.filter(ImageFilter.GaussianBlur(radius=2.5))
    img4.save(OUTPUT_DIR / "sample_04_motion_blurred.jpg", "JPEG", quality=85)

    # Shanghai Plate
    img5 = Image.new("RGB", (500, 250), color=(10, 20, 40))
    d5 = ImageDraw.Draw(img5)
    d5.rectangle([(10, 10), (490, 240)], outline=(80, 80, 80), width=2)
    d5.text((100, 90), "沪B·88888", fill=(140, 140, 140), font=c_font)
    img5 = ImageEnhance.Brightness(img5).enhance(0.4)
    img5.save(OUTPUT_DIR / "sample_05_shanghai_low_light.tiff", "TIFF")

    # Stop Sign
    img6 = Image.new("RGB", (350, 350), color=(255, 255, 255))
    d6 = ImageDraw.Draw(img6)
    points = [(100, 20), (250, 20), (330, 100), (330, 250), (250, 330), (100, 330), (20, 250), (20, 100)]
    d6.polygon(points, fill=(210, 20, 20), outline=(255, 255, 255))
    stop_font = get_font(60)
    d6.text((85, 140), "STOP", fill=(255, 255, 255), font=stop_font)
    img6.save(OUTPUT_DIR / "sample_06_stop_sign.png")

    # Noisy Stop Sign
    img7 = add_gaussian_noise(img6, intensity=50)
    img7.save(OUTPUT_DIR / "sample_07_noisy_stop_sign.tiff", "TIFF")

    # Speed Limit Sign
    img8 = Image.new("RGB", (350, 450), color=(255, 255, 255))
    d8 = ImageDraw.Draw(img8)
    d8.rectangle([(15, 15), (335, 435)], outline=(0, 0, 0), width=6)
    sign_font = get_font(36)
    speed_num_font = get_font(72)
    d8.text((105, 50), "SPEED", fill=(0, 0, 0), font=sign_font)
    d8.text((115, 120), "LIMIT", fill=(0, 0, 0), font=sign_font)
    d8.text((120, 220), "65", fill=(0, 0, 0), font=speed_num_font)
    img8.save(OUTPUT_DIR / "sample_08_speed_limit_sign.png")

    # Work Zone Sign
    img9 = Image.new("RGB", (400, 400), color=(255, 255, 255))
    d9 = ImageDraw.Draw(img9)
    diamond = [(200, 20), (380, 200), (200, 380), (20, 200)]
    d9.polygon(diamond, fill=(245, 120, 20), outline=(0, 0, 0))
    work_font = get_font(32)
    d9.text((150, 110), "ROAD", fill=(0, 0, 0), font=work_font)
    d9.text((150, 175), "WORK", fill=(0, 0, 0), font=work_font)
    d9.text((140, 240), "AHEAD", fill=(0, 0, 0), font=work_font)
    img9.save(OUTPUT_DIR / "sample_09_work_zone_sign.jpg", "JPEG", quality=90)

    # Advisory Plaque
    img10 = Image.new("RGB", (300, 300), color=(250, 210, 30))
    d10 = ImageDraw.Draw(img10)
    d10.rectangle([(10, 10), (290, 290)], outline=(0, 0, 0), width=5)
    adv_font = get_font(76)
    d10.text((95, 100), "35", fill=(0, 0, 0), font=adv_font)
    img10.save(OUTPUT_DIR / "sample_10_advisory_plaque.png")

    print(f"Generated samples in {OUTPUT_DIR.resolve()}.")


if __name__ == "__main__":
    generate_all_samples()
