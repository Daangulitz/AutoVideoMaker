from PIL import Image, ImageDraw, ImageFont, ImageStat
import requests
from io import BytesIO
import textwrap

def is_bright(image):
    grayscale = image.convert("L")
    stat = ImageStat.Stat(grayscale)
    return stat.mean[0] > 170

def center_crop(img, size):
    width, height = img.size
    new_width, new_height = size, size

    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    return img.crop((left, top, right, bottom))

def make_image_card(image_url, title, output_path="output.png"):
    try:
        # Load and crop image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        # Crop to square (centered)
        min_dim = min(img.size)
        img = center_crop(img, min(min_dim, 1080))

        # Resize cropped square to 1080x1080 if smaller
        if img.size[0] < 1080:
            img = img.resize((1080, 1080))

        # Setup
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", size=44)

        text_color = "black" if is_bright(img) else "white"

        # Wrap text
        lines = textwrap.wrap(title, width=32)
        wrapped_text = "\n".join(lines)

        # Text box dimensions
        padding = 20
        text_width = max(draw.textlength(line, font=font) for line in lines)
        text_height = len(lines) * (font.size + 10)

        box_w = text_width + 2 * padding
        box_h = text_height + 2 * padding
        box_x = (img.width - box_w) // 2
        box_y = img.height - box_h - 60

        # Transparent box
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [(box_x, box_y), (box_x + box_w, box_y + box_h)],
            fill=(0, 0, 0, 0),
        )
        img = Image.alpha_composite(img, overlay)

        # Draw text
        draw = ImageDraw.Draw(img)
        draw.multiline_text(
            (box_x + padding, box_y + padding),
            wrapped_text,
            font=font,
            fill=text_color,
            spacing=10,
        )

        img.save(output_path, format="PNG")
        print(f"✅ Image saved: {output_path}")

    except Exception as e:
        print(f"❌ Error creating image card: {e}")
