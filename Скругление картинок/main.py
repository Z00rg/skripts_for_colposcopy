from PIL import Image, ImageDraw
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "img")
OUTPUT_DIR = os.path.join(BASE_DIR, "img_rounded")

RADIUS = 12  # rounded-xl

os.makedirs(OUTPUT_DIR, exist_ok=True)


def round_corners(image, radius):
    # Гарантируем RGBA
    image = image.convert("RGBA")
    w, h = image.size

    # Маска с прозрачными углами
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, w, h),
        radius=radius,
        fill=255
    )

    # Применяем маску
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)

    return result


for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
        continue

    src_path = os.path.join(INPUT_DIR, filename)
    img = Image.open(src_path)

    rounded = round_corners(img, RADIUS)

    name, _ = os.path.splitext(filename)
    out_path = os.path.join(OUTPUT_DIR, f"{name}.png")  # <-- ВСЕГДА PNG

    rounded.save(out_path, format="PNG")
    print(f"✔ {filename} → {name}.png")

print("Готово. Углы прозрачные ✅")
