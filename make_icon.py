# -*- coding: utf-8 -*-
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path("niqaa.ico")


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_icon(size: int) -> Image.Image:
    scale = size / 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def xy(values: tuple[float, ...]) -> tuple[int, ...]:
        return tuple(int(value * scale) for value in values)

    # Royal indigo glass tile.
    draw.rounded_rectangle(xy((12, 12, 244, 244)), radius=int(34 * scale), fill=(18, 24, 45, 255))
    draw.rounded_rectangle(xy((20, 20, 236, 236)), radius=int(28 * scale), outline=(129, 140, 248, 185), width=max(1, int(4 * scale)))
    draw.ellipse(xy((32, 26, 218, 188)), fill=(79, 70, 229, 58))

    # Shield body.
    shield = [xy((128, 42))[0:2], xy((194, 68))[0:2], xy((184, 152))[0:2], xy((128, 210))[0:2], xy((72, 152))[0:2], xy((62, 68))[0:2]]
    draw.polygon(shield, fill=(49, 46, 129, 255), outline=(199, 210, 254, 255))
    draw.line(xy((128, 50, 128, 204)), fill=(129, 140, 248, 180), width=max(1, int(3 * scale)))

    # Clean sweep mark.
    draw.line(xy((91, 146, 160, 87)), fill=(255, 255, 255, 255), width=max(2, int(12 * scale)))
    draw.line(xy((154, 84, 180, 110)), fill=(34, 197, 94, 255), width=max(2, int(10 * scale)))
    draw.arc(xy((84, 128, 164, 192)), 205, 335, fill=(34, 197, 94, 255), width=max(2, int(10 * scale)))

    # Small deletion spark/lines.
    draw.line(xy((80, 92, 102, 114)), fill=(248, 113, 113, 255), width=max(1, int(6 * scale)))
    draw.line(xy((102, 92, 80, 114)), fill=(248, 113, 113, 255), width=max(1, int(6 * scale)))

    # Brand initials.
    font = load_font(max(10, int(30 * scale)))
    text = "ن"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text((int((size - text_w) / 2), int(214 * scale)), text, font=font, fill=(255, 255, 255, 245))
    return image


def main() -> None:
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [make_icon(size) for size in sizes]
    images[-1].save(OUT, sizes=[(size, size) for size in sizes], append_images=images[:-1])
    print(OUT.resolve())


if __name__ == "__main__":
    main()
