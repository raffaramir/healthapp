"""Generate HEALTHAPP PWA PNG icons (any + maskable, 192 + 512).

Run once with the project venv:
    python scripts/gen_pwa_icons.py
Output: static/img/pwa/icon-{192,512}.png + icon-maskable-{192,512}.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / 'static' / 'img' / 'pwa'
OUT.mkdir(parents=True, exist_ok=True)

GRAD_TOP = (16, 185, 129)     # #10B981
GRAD_MID = (22, 163, 74)      # #16A34A
GRAD_BOT = (11, 95, 45)       # #0B5F2D
WHITE = (255, 255, 255)


def gradient_bg(size: int) -> Image.Image:
    """Diagonal three-stop gradient."""
    img = Image.new('RGBA', (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)  # 0..1 diagonal
            if t < 0.6:
                k = t / 0.6
                r = int(GRAD_TOP[0] + (GRAD_MID[0] - GRAD_TOP[0]) * k)
                g = int(GRAD_TOP[1] + (GRAD_MID[1] - GRAD_TOP[1]) * k)
                b = int(GRAD_TOP[2] + (GRAD_MID[2] - GRAD_TOP[2]) * k)
            else:
                k = (t - 0.6) / 0.4
                r = int(GRAD_MID[0] + (GRAD_BOT[0] - GRAD_MID[0]) * k)
                g = int(GRAD_MID[1] + (GRAD_BOT[1] - GRAD_MID[1]) * k)
                b = int(GRAD_MID[2] + (GRAD_BOT[2] - GRAD_MID[2]) * k)
            px[x, y] = (r, g, b, 255)
    return img


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    return mask


def draw_cross(canvas: Image.Image, bar_w: int, bar_h: int, corner: int) -> None:
    """Centered medical cross."""
    size = canvas.size[0]
    cx = cy = size // 2
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # vertical bar
    d.rounded_rectangle(
        (cx - bar_w // 2, cy - bar_h // 2, cx + bar_w // 2, cy + bar_h // 2),
        radius=corner, fill=WHITE,
    )
    # horizontal bar
    d.rounded_rectangle(
        (cx - bar_h // 2, cy - bar_w // 2, cx + bar_h // 2, cy + bar_w // 2),
        radius=corner, fill=WHITE,
    )
    # subtle glow
    glow = overlay.filter(ImageFilter.GaussianBlur(radius=size // 64))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(overlay)


def make_any(size: int) -> Image.Image:
    """Rounded-corner icon (purpose=any)."""
    bg = gradient_bg(size)
    rounded = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rounded.paste(bg, (0, 0), rounded_mask(size, radius=int(size * 0.19)))
    bar_w = int(size * 0.16)
    bar_h = int(size * 0.55)
    draw_cross(rounded, bar_w=bar_w, bar_h=bar_h, corner=int(size * 0.04))
    return rounded


def make_maskable(size: int) -> Image.Image:
    """Full-bleed icon for adaptive masks (purpose=maskable). Content inside 80% safe zone."""
    bg = gradient_bg(size)
    bar_w = int(size * 0.14)
    bar_h = int(size * 0.55)  # within 80% safe radius
    draw_cross(bg, bar_w=bar_w, bar_h=bar_h, corner=int(size * 0.035))
    return bg


def main() -> None:
    for s in (192, 512):
        any_img = make_any(s)
        any_img.save(OUT / f'icon-{s}.png', optimize=True)
        mask_img = make_maskable(s)
        mask_img.save(OUT / f'icon-maskable-{s}.png', optimize=True)
        print(f'wrote icon-{s}.png + icon-maskable-{s}.png')

    # Apple touch icon — iOS prefers a square non-transparent PNG, ~180px.
    apple = make_maskable(180)
    apple.save(OUT / 'apple-touch-icon.png', optimize=True)
    print('wrote apple-touch-icon.png')


if __name__ == '__main__':
    main()
