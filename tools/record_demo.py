# Records the live huggingface-hello-web demo as PNG frames (onnxruntime-web served from a local npm copy).
# usage: python rec_hf.py <out_dir>
import os, sys, time
from playwright.sync_api import sync_playwright

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
URL = "https://huseyinbaranisik.github.io/huggingface-hello-web/"
CHROME = os.path.expanduser("~/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe")
ORT = os.environ.get("ORT_DIST", "ortweb/package/dist")  # local copy of onnxruntime-web@1.22.0 dist (npm pack)
FPS = 10
n = 0

def grab(page, seconds):
    global n
    end = time.time() + seconds
    while time.time() < end:
        t = time.time()
        page.screenshot(path=os.path.join(OUT, f"{n:04d}.png"))
        n += 1
        time.sleep(max(0, 1 / FPS - (time.time() - t)))

def serve_ort(route):
    path = os.path.join(ORT, route.request.url.split("/dist/")[-1].split("?")[0])
    ctype = "application/wasm" if path.endswith(".wasm") else "text/javascript"
    route.fulfill(path=path, content_type=ctype) if os.path.exists(path) else route.abort()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    page = b.new_page(viewport={"width": 1120, "height": 700}, device_scale_factor=1)
    page.route("**/cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/**", serve_ort)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_selector("#tahmin:not([disabled])", timeout=60000)
    grab(page, 1.5)
    page.click("#tahmin"); grab(page, 2.2)
    for name, value in [("glucose", "110"), ("bmi", "22.4"), ("age", "31")]:
        box = page.locator(f'input[name="{name}"]')
        box.fill(""); grab(page, 0.2)
        for ch in value:
            box.type(ch); grab(page, 0.12)
    grab(page, 0.4)
    page.click("#tahmin"); grab(page, 2.6)
    print(page.inner_text("#sonuc").replace("\n", " | "))
    b.close()
print(n, "frames ->", OUT)
