"""Renders the README figures in assets/ (hero, terminal output, demo GIF).

usage:
  python tools/render_figures.py                 # hero.png + terminal-train.png
  python tools/render_figures.py <frames_dir>    # also demo.gif from PNG frames of the live demo
Inputs: assets/app-screenshot.png (2x screenshot of the live demo). Requires Pillow.
Fonts (OFL) are in tools/fonts/: Space Grotesk and JetBrains Mono.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets")

# Warm palette taken from the demo page itself (Hugging Face yellow → orange on cream).
BG, CARD, LINE = "#FFF8EC", "#FFFFFF", "#EFE3CC"
INK, SUB, MUTED = "#1F1A14", "#5E554A", "#9A8F80"
YELLOW, ORANGE, ORANGE_DK, GREEN = "#FFD21E", "#FF9D00", "#D97A00", "#23935F"
TERM_BG, TERM_BAR, TERM_TXT = "#1E1B18", "#2A2622", "#EDE6DA"

def font(name, size, weight):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    f.set_variation_by_axes([weight])
    return f

DISPLAY = lambda s: font("SpaceGrotesk.ttf", s, 700)
MEDIUM = lambda s: font("SpaceGrotesk.ttf", s, 500)
BODY = lambda s: font("SpaceGrotesk.ttf", s, 400)
MONO = lambda s: font("JetBrainsMono.ttf", s, 400)
MONO_B = lambda s: font("JetBrainsMono.ttf", s, 700)

def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]

def glow(im, xy, radius, color, alpha):
    """Soft colour blob behind the content (the page's own gradient feel)."""
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    x, y = xy
    ImageDraw.Draw(layer).ellipse([x - radius, y - radius, x + radius, y + radius], fill=color + (alpha,))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius // 2)))

def shadow(im, box, r, offset=18, blur=28, alpha=55):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(layer).rounded_rectangle([x0, y0 + offset, x1, y1 + offset], r, fill=(60, 40, 10, alpha))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))

def chip(d, xy, text, f, fill=YELLOW, color=INK, pad=(16, 8)):
    x, y = xy
    w = d.textlength(text, font=f)
    h = f.size + 2 * pad[1]
    d.rounded_rectangle([x, y, x + w + 2 * pad[0], y + h], h // 2, fill=fill)
    d.text((x + pad[0], y + pad[1] - 2), text, font=f, fill=color)
    return x + w + 2 * pad[0]

def browser(im, box, url, shot):
    """Browser window with traffic-light dots, URL pill and the screenshot inside."""
    x0, y0, x1, y1 = box
    shadow(im, box, 22)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 22, fill=CARD, outline=LINE, width=2)
    bar = 58
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        cx = x0 + 30 + i * 26
        d.ellipse([cx - 7, y0 + bar // 2 - 7, cx + 7, y0 + bar // 2 + 7], fill=c)
    d.rounded_rectangle([x0 + 120, y0 + 13, x1 - 40, y0 + bar - 13], 16, fill="#F6EFE2")
    d.text((x0 + 140, y0 + 17), url, font=MONO(17), fill=SUB)
    d.line([(x0, y0 + bar), (x1, y0 + bar)], fill=LINE, width=2)
    inner = (x1 - x0 - 4, y1 - y0 - bar - 4)
    s = shot.copy(); s.thumbnail(inner, Image.LANCZOS)
    mask = Image.new("L", s.size, 0)  # round only the two bottom corners
    ImageDraw.Draw(mask).rounded_rectangle([0, -30, s.width, s.height], 20, fill=255)
    im.paste(s, (x0 + 2, y0 + bar + 2), mask)

URL = "huseyinbaranisik.github.io/huggingface-hello-web"
# Same reference input, same probability everywhere. Android is only reported in the project README.
RUNTIMES = ["scikit-learn", "ONNX Runtime", "browser", "Rails", "Android*"]

def hero():
    W, H = 1800, 860
    im = Image.new("RGBA", (W, H), BG)
    glow(im, (1500, 160), 420, (255, 210, 30), 120)
    glow(im, (1150, 820), 380, (255, 157, 0), 70)
    d = ImageDraw.Draw(im)

    x = 100
    nx = chip(d, (x, 130), "Hugging Face Hub", MONO_B(18))
    chip(d, (nx + 12, 130), "ONNX Runtime", MONO_B(18), fill="#FFE9C2")
    d.text((x - 4, 200), "huggingface", font=DISPLAY(104), fill=INK)
    d.text((x - 4, 310), "hello", font=DISPLAY(104), fill=ORANGE)
    d.text((x, 440), "One model, four runtimes.", font=MEDIUM(40), fill=INK)
    y = 510
    for line in wrap(d, "A small model trained locally, exported to ONNX and hosted for free on the "
                        "Hugging Face Hub, then run in the browser, on Android and on a Rails server.", BODY(25), 590):
        d.text((x, y), line, font=BODY(25), fill=SUB); y += 38
    tx = x
    for t in ["Python", "Browser", "Android", "Rails 8"]:
        tx = chip(d, (tx, 690), t, MEDIUM(20), fill=CARD, color=INK, pad=(18, 10)) + 10
    d.text((x, 770), "Pima diabetes  ·  logistic regression  ·  Hüseyin Baran Işık", font=MONO(17), fill=MUTED)

    shot = Image.open(os.path.join(OUT, "app-screenshot.png")).convert("RGB")
    browser(im, (830, 90, 1720, 90 + 58 + int(886 * shot.height / shot.width) + 4), URL, shot)

    # floating card: the cross-runtime check, overlapping the window's bottom-left corner
    cx0, cy0, cx1, cy1 = 790, 560, 1160, 812
    shadow(im, (cx0, cy0, cx1, cy1), 20, offset=12, blur=20, alpha=70)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx0, cy0, cx1, cy1], 20, fill=CARD, outline=LINE, width=2)
    d.text((cx0 + 28, cy0 + 24), "P(diabetes), reference input", font=MONO(16), fill=MUTED)
    d.text((cx0 + 26, cy0 + 50), "0.6771", font=DISPLAY(64), fill=ORANGE_DK)
    d.text((cx0 + 28, cy0 + 134), "same on all 5 runtimes", font=MEDIUM(19), fill=GREEN)
    d.text((cx0 + 28, cy0 + 166), " · ".join(RUNTIMES[:3]), font=MONO(14), fill=SUB)
    d.text((cx0 + 28, cy0 + 188), " · ".join(RUNTIMES[3:]), font=MONO(14), fill=SUB)
    d.text((cx0 + 28, cy0 + 216), "* as reported in the project README", font=MONO(12), fill=MUTED)
    return im.convert("RGB")

# Fig. 3: real output of `hf_cli.py train` and `hf_cli.py predict` (captured 30 Oct 2026).
TERMINAL = """$ python hf_cli.py train
✓ model.onnx üretildi (sklearn ile maks fark 1.2e-07)
✓ model eğitildi → _out/model
  test metrikleri: {'accuracy': 0.7792, 'auc': 0.8428}

$ python hf_cli.py predict
{
  "input": { "pregnancies": 1.0, "glucose": 193.0, "blood_pressure": 50.0,
             "skin_thickness": 16.0, "insulin": 375.0, "bmi": 25.9,
             "pedigree": 0.655, "age": 24.0 },
  "proba": { "diabetes yok": 0.3229, "diabetes var": 0.6771 }
}"""

def caption(d, x, y, fig, title):
    nx = chip(d, (x, y), f"Fig. {fig}", MONO_B(17))
    d.text((nx + 16, y + 2), title, font=MEDIUM(26), fill=INK)

def terminal():
    W, H = 1400, 650
    im = Image.new("RGBA", (W, H), BG)
    glow(im, (W - 120, 60), 260, (255, 210, 30), 90)
    caption(ImageDraw.Draw(im), 70, 48, 3, "Real output: train, then predict")
    box = (70, 120, W - 70, H - 60)
    shadow(im, box, 18)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 18, fill=TERM_BG)
    d.rounded_rectangle([box[0], box[1], box[2], box[1] + 52], 18, fill=TERM_BAR)
    d.rectangle([box[0], box[1] + 30, box[2], box[1] + 52], fill=TERM_BAR)
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        d.ellipse([box[0] + 24 + i * 24 - 7, box[1] + 19, box[0] + 24 + i * 24 + 7, box[1] + 33], fill=c)
    d.text((box[0] + 110, box[1] + 15), "~/huggingface-hello-web", font=MONO(17), fill="#A39C90")
    y = box[1] + 80
    for line in TERMINAL.split("\n"):
        x = box[0] + 34
        if line.startswith("✓"):  # JetBrains Mono has no ✓ glyph: draw the tick as two strokes
            d.line([(x + 1, y + 13), (x + 6, y + 19), (x + 14, y + 6)], fill="#5FD39A", width=3, joint="curve")
            d.text((x + d.textlength("✓", font=MONO(20)), y), line[1:], font=MONO(20), fill="#5FD39A")
        else:
            color = ORANGE if line.startswith("$") else TERM_TXT
            d.text((x, y), line, font=MONO_B(20) if line.startswith("$") else MONO(20), fill=color)
        y += 32
    return im.convert("RGB")

def demo(frames_dir):
    files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    crop = (0, 0, 1070, 690)  # the page's two content columns, with the result card's right edge
    W = 1080
    fw = W - 140 - 4
    fh = int(fw * (crop[3] - crop[1]) / (crop[2] - crop[0]))
    H = 120 + 58 + fh + 4 + 70
    base = Image.new("RGBA", (W, H), BG)  # no glow here: soft gradients band badly in a GIF palette
    caption(ImageDraw.Draw(base), 70, 40, 2, "Live demo: inference in the browser")
    blank = Image.new("RGB", (crop[2], crop[3]), CARD)
    browser(base, (70, 110, W - 70, 110 + 58 + fh + 4), URL, blank)
    base = base.convert("RGB")
    frames = []
    for f in files:
        fr = Image.open(os.path.join(frames_dir, f)).convert("RGB").crop(crop).resize((fw, fh), Image.LANCZOS)
        p = base.copy()
        mask = Image.new("L", fr.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, -30, fw, fh], 20, fill=255)
        p.paste(fr, (72, 110 + 58 + 2), mask)
        frames.append(p.quantize(colors=160, method=Image.Quantize.FASTOCTREE))
    hold = [frames[-1]] * 12  # rest on the final result before looping
    frames[0].save(os.path.join(OUT, "demo.gif"), save_all=True, append_images=frames[1:] + hold,
                   duration=100, loop=0, optimize=True)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hero().save(os.path.join(OUT, "hero.png"), optimize=True)
    terminal().save(os.path.join(OUT, "terminal-train.png"), optimize=True)
    if len(sys.argv) > 1:
        demo(sys.argv[1])
    print("figures ->", OUT)
