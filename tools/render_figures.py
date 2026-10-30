"""Renders the README figures in assets/ (hero, terminal output, demo GIF plate).

usage:
  python tools/render_figures.py                 # hero.png + terminal-train.png
  python tools/render_figures.py <frames_dir>    # also demo.gif from PNG frames of the live demo
Requires Pillow. Fonts (OFL) are in tools/fonts/.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
OUT = os.path.join(ROOT, "assets")

BG, PANEL, LINE = "#0E1424", "#141C30", "#27314B"
GOLD, CREAM, MUTED, GREEN = "#C9A35B", "#F2EAD8", "#8A93A6", "#7FB77E"

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

SERIF_B = lambda s: font("PlayfairDisplay-Bold.ttf", s)
SERIF_I = lambda s: font("PlayfairDisplay-Italic.ttf", s)
SANS = lambda s: font("IBMPlexSans-Regular.ttf", s)
SANS_B = lambda s: font("IBMPlexSans-SemiBold.ttf", s)
MONO = lambda s: font("IBMPlexMono-Regular.ttf", s)
MONO_B = lambda s: font("IBMPlexMono-SemiBold.ttf", s)

def spaced(d, xy, text, f, fill, gap):
    """Letter-spaced small caps label, the 'kicker' style used on every figure."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + gap
    return x

def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]

def plate_header(d, x, y, w, fig, title):
    spaced(d, (x, y), f"HUGGINGFACE HELLO  ·  FIG. {fig}", MONO_B(17), GOLD, 3)
    f = SERIF_I(26)
    d.text((x + w - d.textlength(title, font=f), y - 8), title, font=f, fill=MUTED)

# Fig. 1: one reference input, the same probability on every runtime.
# "checked by" says where each number comes from; Android is only reported in the project README.
RUNTIMES = [
    ("Python · scikit-learn", "hf_cli.py train"),
    ("Python · ONNX Runtime", "hf_cli.py hub-predict"),
    ("Browser · onnxruntime-web", "live demo"),
    ("Rails 8 · onnxruntime gem", "rails test"),
    ("Android · onnxruntime-react-native", "project README"),
]

def hero():
    W, H = 1800, 820
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    x = 110
    spaced(d, (x, 120), "HUGGING FACE HUB  ·  ONNX RUNTIME", MONO_B(19), GOLD, 4)
    d.line([(x, 162), (x + 70, 162)], fill=GOLD, width=3)
    d.text((x - 6, 190), "huggingface", font=SERIF_B(112), fill=CREAM)
    d.text((x - 6, 312), "hello", font=SERIF_B(112), fill=CREAM)
    d.text((x, 450), "One Model, Four Runtimes", font=SERIF_I(46), fill=GOLD)
    y = 535
    for line in wrap(d, "A small model trained locally, exported to ONNX and hosted for free on the "
                        "Hugging Face Hub — then run in the browser, on Android and on a Rails server.", SANS(25), 720):
        d.text((x, y), line, font=SANS(25), fill="#B9BFCC"); y += 38
    d.line([(x, 720), (x + 760, 720)], fill=LINE, width=1)
    spaced(d, (x, 740), "Pima diabetes  ·  logistic regression  ·  Hüseyin Baran Işık", MONO(17), MUTED, 1)

    # right: Fig. 1 card
    cx, cy, cw, ch = 1000, 110, 690, 580
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=PANEL, outline=GOLD, width=2)
    d.text((cx + 40, cy + 34), "Reference input", font=SANS_B(22), fill=CREAM)
    d.text((cx + 40, cy + 70), "glucose 193 · bmi 25.9 · age 24 · insulin 375 · …", font=MONO(17), fill=MUTED)
    d.text((cx + 40, cy + 112), "P(diabetes)", font=SANS(22), fill=MUTED)
    d.text((cx + 40, cy + 140), "0.6771", font=SERIF_B(84), fill=GOLD)
    y = cy + 272
    d.line([(cx + 40, y - 18), (cx + cw - 40, y - 18)], fill=LINE, width=1)
    for name, src in RUNTIMES:
        # name with its source underneath, the value right-aligned so long names never collide
        d.text((cx + 40, y), name, font=SANS(21), fill=CREAM)
        d.text((cx + 40, y + 29), src, font=MONO(15), fill=MUTED)
        v = "0.6771"
        d.text((cx + cw - 40 - d.textlength(v, font=MONO_B(22)), y + 10), v, font=MONO_B(22), fill=GREEN)
        y += 60
    d.text((cx, cy + ch + 26), "Fig. 1", font=MONO_B(17), fill=GOLD)
    d.text((cx + 70, cy + ch + 20), "Same input, same probability — on every runtime", font=SERIF_I(23), fill=MUTED)
    return im

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

def terminal():
    W, H = 1400, 700
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    plate_header(d, 80, 60, W - 160, 3, "Real output — train, then predict")
    tx, ty, tw = 80, 120, W - 160
    d.rectangle([tx, ty, tx + tw, H - 70], fill=PANEL, outline=LINE, width=1)
    d.rectangle([tx, ty, tx + tw, ty + 54], fill="#18213A", outline=LINE, width=1)
    d.text((tx + 28, ty + 15), "~/huggingface-hello-web — python", font=MONO(18), fill=MUTED)
    y = ty + 86
    for line in TERMINAL.split("\n"):
        color = GOLD if line.startswith("$") else GREEN if line.startswith("✓") else CREAM
        d.text((tx + 34, y), line, font=MONO_B(21) if line.startswith("$") else MONO(21), fill=color)
        y += 33
    return im

def demo(frames_dir):
    files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    crop = (0, 0, 1040, 690)  # the page's two content columns
    fw, fh = 860, int(860 * (crop[3] - crop[1]) / (crop[2] - crop[0]))
    W, H = fw + 140, fh + 230
    base = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(base)
    plate_header(d, 70, 52, W - 140, 2, "Live demo — inference in the browser")
    d.rectangle([69, 109, 70 + fw, 110 + fh], outline=GOLD, width=2)
    d.text((70, 140 + fh), "›", font=MONO_B(24), fill=GOLD)
    d.text((98, 141 + fh), "huseyinbaranisik.github.io/huggingface-hello-web", font=MONO_B(22), fill=CREAM)
    frames = []
    for f in files:
        fr = Image.open(os.path.join(frames_dir, f)).convert("RGB").crop(crop).resize((fw, fh), Image.LANCZOS)
        p = base.copy(); p.paste(fr, (70, 110)); frames.append(p.quantize(colors=160, method=Image.Quantize.FASTOCTREE))
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
