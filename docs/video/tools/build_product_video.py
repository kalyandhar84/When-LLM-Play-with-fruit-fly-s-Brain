#!/usr/bin/env python3
"""Record the live Neural Path Finder exhibit + GitHub architecture docs,
then assemble a captioned ~5:08 product mp4 (no TTS, no claimed Kalyan VO).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
VIDEO = ROOT / "docs" / "video"
STILLS = VIDEO / "stills"
DIAGRAMS = VIDEO / "diagrams"
RAW = VIDEO / "raw"
BUILD = VIDEO / "build"
MASTER = VIDEO / "neural_path_finder_product.mp4"
CAPTIONS = VIDEO / "captions.srt"
CAPTIONS_ASS = VIDEO / "captions.ass"

LIVE = "https://fruitfly-poc.azurewebsites.net/"
ARCH = "https://github.com/kalyandhar84/fruitfly/blob/main/docs/ARCHITECTURE.md"
README = "https://github.com/kalyandhar84/fruitfly/blob/main/README.md"
GEN_PY = "https://github.com/kalyandhar84/fruitfly/blob/main/scripts/generate_connectome.py"

W, H, FPS = 1920, 1080, 30
BG = (246, 234, 212)
PANEL = (255, 248, 238)
INK = (58, 36, 24)
MUTED = (111, 87, 72)
ACCENT = (217, 137, 18)
PINK = (226, 90, 154)
WHITE = (255, 253, 248)

FONT_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
FONT_MED = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"
FONT_SEM = "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

SCENES = [
    "Taste Food",
    "Watch TV",
    "Zapped By Human",
    "Hot Sensation",
    "Cold Sensation",
    "Smell Something Yummy",
    "Hear a Buzz",
    "Smell Something Bad",
]

# Exact chapter lengths — captions.srt is authored against this timeline.
CHAPTERS = {
    "title": 8.0,
    "what": 44.0,  # 0:08–0:52
    "data_card_a": 7.0,
    "data_card_b": 10.0,
    "data_gen": 13.0,
    "data_stats": 13.0,  # 0:52–1:35 = 43
    "cando": 45.0,  # 1:35–2:20
    "demo": 100.0,  # 2:20–4:00
    "arch_card": 6.0,
    "arch_github": 16.0,
    "arch_readme": 10.0,
    "arch_seq": 8.0,
    "arch_stages": 6.0,
    "arch_modules": 6.0,  # 4:00–4:52 = 52
    "outro": 16.0,  # 4:52–5:08
}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rounded(draw: ImageDraw.ImageDraw, xy, r, fill):
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def save_card(name: str, paint) -> Path:
    STILLS.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # warm wash
    overlay = Image.new("RGB", (W, H), (255, 232, 196))
    img = Image.blend(img, overlay, 0.18)
    draw = ImageDraw.Draw(img)
    draw.ellipse((1200, -220, 2100, 520), fill=(255, 214, 170))
    draw.ellipse((-280, 720, 620, 1300), fill=(255, 214, 224))
    paint(img, draw)
    path = STILLS / name
    img.save(path, "PNG", optimize=True)
    return path


def make_title_cards() -> dict[str, Path]:
    out: dict[str, Path] = {}

    def title(img, draw):
        f_k = font(FONT_SEM, 22)
        f_h = font(FONT_BOLD, 86)
        f_s = font(FONT_MED, 34)
        f_u = font(FONT_REG, 22)
        draw.ellipse((140, 150, 214, 224), fill=ACCENT)
        draw.ellipse((156, 166, 198, 208), fill=PINK)
        draw.text((240, 168), "A TINY FLY’S NERVOUS SYSTEM  ·  PLAY MODE", fill=ACCENT, font=f_k)
        draw.text((140, 250), "Neural Path Finder", fill=INK, font=f_h)
        sub = "Play a fruit fly’s day on a connectome map"
        draw.text((140, 370), sub, fill=MUTED, font=f_s)
        rounded(draw, (140, 470, 1180, 560), 28, PANEL)
        draw.text((170, 498), "fruitfly-poc.azurewebsites.net", fill=INK, font=font(FONT_SEM, 28))
        note = "Voiceover by Kalyan Dhar — mux Recording (4).m4a when the Windows PC is back"
        for i, line in enumerate(wrap(draw, note, f_u, 1500)):
            draw.text((140, 900 + i * 32), line, fill=MUTED, font=f_u)

    def data_a(img, draw):
        draw.text((140, 160), "2  ·  DATA SOURCE", fill=ACCENT, font=font(FONT_SEM, 22))
        draw.text((140, 220), "Not a live lab feed.", fill=INK, font=font(FONT_BOLD, 72))
        body = (
            "The browser never talks to Janelia at runtime. "
            "scripts/generate_connectome.py writes a hand-authored connectome.json. "
            "The API loads that file once into a NetworkX directed graph."
        )
        y = 370
        for line in wrap(draw, body, font(FONT_MED, 32), 1600):
            draw.text((140, y), line, fill=MUTED, font=font(FONT_MED, 32))
            y += 48

    def data_b(img, draw):
        draw.text((140, 120), "MALE CNS  vs  THIS APP", fill=ACCENT, font=font(FONT_SEM, 22))
        boxes = [
            (140, 220, 900, 860, "Published MaleCNS v1.0", "166,000", "neurons", "125 million synapses"),
            (1020, 220, 1780, 860, "Teaching graph in the app", "75", "neurons", "149 connections"),
        ]
        for x0, y0, x1, y1, cap, big, unit, sub in boxes:
            rounded(draw, (x0, y0, x1, y1), 36, PANEL)
            draw.text((x0 + 40, y0 + 40), cap, fill=MUTED, font=font(FONT_SEM, 24))
            draw.text((x0 + 40, y0 + 140), big, fill=INK, font=font(FONT_BOLD, 92))
            draw.text((x0 + 40, y0 + 260), unit, fill=ACCENT, font=font(FONT_SEM, 36))
            draw.text((x0 + 40, y0 + 500), sub, fill=MUTED, font=font(FONT_MED, 28))

    def arch(img, draw):
        draw.text((140, 180), "5  ·  ARCHITECTURE", fill=ACCENT, font=font(FONT_SEM, 22))
        draw.text((140, 250), "How the program is built", fill=INK, font=font(FONT_BOLD, 64))
        body = (
            "Walk docs/ARCHITECTURE.md and the README mermaid diagrams: "
            "Vite SPA → FastAPI /api → graph.py → pathfinder.py → connectome.json. "
            "No graph database. No Janelia client at runtime."
        )
        y = 390
        for line in wrap(draw, body, font(FONT_MED, 32), 1600):
            draw.text((140, y), line, fill=MUTED, font=font(FONT_MED, 32))
            y += 48
        draw.text((140, 700), "github.com/kalyandhar84/fruitfly", fill=INK, font=font(FONT_SEM, 28))

    def outro(img, draw):
        draw.text((140, 180), "Neural Path Finder", fill=INK, font=font(FONT_BOLD, 72))
        draw.text((140, 280), "A wiring map you can play.", fill=MUTED, font=font(FONT_MED, 36))
        rounded(draw, (140, 400, 1780, 620), 32, PANEL)
        draw.text((180, 440), "Live exhibit", fill=MUTED, font=font(FONT_SEM, 22))
        draw.text((180, 480), "https://fruitfly-poc.azurewebsites.net/", fill=INK, font=font(FONT_SEM, 32))
        draw.text((180, 540), "https://github.com/kalyandhar84/fruitfly", fill=INK, font=font(FONT_MED, 28))
        note = (
            "Kalyan Dhar voiceover is not in this file. Mux Recording (4).m4a "
            "with the chain in docs/video/VOICEOVER.md — do not substitute TTS."
        )
        y = 700
        for line in wrap(draw, note, font(FONT_REG, 24), 1600):
            draw.text((140, y), line, fill=MUTED, font=font(FONT_REG, 24))
            y += 36

    out["title"] = save_card("card-title.png", title)
    out["data_a"] = save_card("card-data-feed.png", data_a)
    out["data_b"] = save_card("card-data-stats.png", data_b)
    out["arch"] = save_card("card-architecture.png", arch)
    out["outro"] = save_card("card-outro.png", outro)
    return out


MERMAID_HTML = """<!doctype html>
<html><head>
<meta charset="utf-8"/>
<title>NPF diagrams</title>
<style>
  html, body { margin:0; background:#f6ead4; color:#3a2418; font-family: Inter, Nunito, sans-serif; }
  .slide { width:1920px; height:1080px; padding:64px 72px; box-sizing:border-box; }
  h1 { font-size:40px; margin:0 0 12px; }
  p.k { color:#d98912; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:16px; margin:0 0 8px; }
  .box { background:#fff8ee; border-radius:28px; padding:28px 36px; height:860px; overflow:hidden;
         box-shadow:0 16px 36px rgba(92,48,18,.12); }
</style>
</head><body>
<div class="slide" id="runtime">
  <p class="k">README · runtime</p>
  <h1>Browser SPA → FastAPI → connectome.json</h1>
  <div class="box"><pre class="mermaid">
flowchart LR
  subgraph Browser
    SPA["Vite SPA  frontend/dist"]
  end
  subgraph "FastAPI :8000"
    Index["GET /  → dist/index.html"]
    API["/api/*"]
    G["graph.py"]
    P["pathfinder.py"]
    X["explain.py"]
    JSON[("connectome.json  75 neurons / 149 edges")]
  end
  SPA -->|same origin| Index
  SPA -->|fetch JSON| API
  API --> G
  API --> P
  P --> X
  G --> JSON
  </pre></div>
</div>
<div class="slide" id="sequence">
  <p class="k">ARCHITECTURE.md · request flow</p>
  <h1>Tap Watch TV · GET /api/scenarios/watch-tv/run</h1>
  <div class="box"><pre class="mermaid">
sequenceDiagram
  participant B as Browser SPA
  participant F as FastAPI
  participant C as connectome.json
  participant PF as pathfinder
  B->>F: GET /api/health
  F-->>B: status ok
  B->>F: GET /api/scenarios
  F-->>B: eight scene cards
  B->>F: GET /api/scenarios/watch-tv/run
  F->>PF: PathFindRequest R1 to DNg13
  PF->>C: NetworkX DiGraph
  PF-->>F: ranked paths + hubs
  F-->>B: result + playful_story
  B->>F: POST /api/branch
  F-->>B: upstream / downstream
  </pre></div>
</div>
<div class="slide" id="stages">
  <p class="k">ARCHITECTURE.md · official motif</p>
  <h1>R1 photoreceptors toward DNg13</h1>
  <div class="box"><pre class="mermaid">
flowchart LR
  R["R1–R6  retina"] --> L["L1 / L2 / L3  lamina"]
  L --> M["Mi1 / Tm3  medulla"]
  M --> P["LC10 / AOTU  lobula"]
  P --> CB["AVLP / LAL / Vest"]
  CB --> DN["DNg13  neck"]
  DN --> V["LegMN  VNC"]
  </pre></div>
</div>
<div class="slide" id="modules">
  <p class="k">ARCHITECTURE.md · backend modules</p>
  <h1>Ranking: hops, bottleneck synapses, Jaccard alts</h1>
  <div class="box"><pre class="mermaid">
flowchart TB
  GEN[generate_connectome.py] --> JSON[(connectome.json)]
  JSON --> GRAPH[graph.py load resolve hubs]
  GRAPH --> PF[pathfinder.py shortest strength diversity]
  PF --> EX[explain.py why-this-path playful_story]
  MAIN[main.py FastAPI plus SPA] --> GRAPH
  MAIN --> PF
  UI[Vite UI scenes and scientist] --> MAIN
  </pre></div>
</div>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({
    startOnLoad: true,
    theme: "base",
    themeVariables: {
      primaryColor: "#fff1d6",
      primaryTextColor: "#3a2418",
      primaryBorderColor: "#d98912",
      lineColor: "#8c5824",
      secondaryColor: "#f6ead4",
      tertiaryColor: "#fff8ee",
      fontFamily: "Inter, Nunito, sans-serif",
      fontSize: "18px"
    }
  });
</script>
</body></html>
"""


def run_ffmpeg(args: list[str]) -> None:
    print("+", " ".join(args[:12]), "..." if len(args) > 12 else "")
    subprocess.run(args, check=True)


def still_mp4(png: Path, seconds: float, dest: Path, kenburns: bool = False) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fade_out = max(0.05, seconds - 0.35)
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0xf6ead4,fps={FPS},"
        f"fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out:.2f}:d=0.25,format=yuv420p"
    )
    inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{seconds:.3f}", "-i", str(png)]
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            *inp,
            "-f",
            "lavfi",
            "-t",
            f"{seconds:.3f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf",
            vf,
            "-t",
            f"{seconds:.3f}",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            str(dest),
        ]
    )
    return dest


def fit_webm(webm: Path, seconds: float, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=yuv420p,"
        f"tpad=stop_mode=clone:stop_duration=12"
    )
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(webm),
            "-f",
            "lavfi",
            "-t",
            f"{seconds:.3f}",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf",
            vf,
            "-t",
            f"{seconds:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            str(dest),
        ]
    )
    return dest


def inject_cursor(page) -> None:
    page.evaluate(
        """() => {
      if (document.getElementById('npf-cursor')) return;
      const s = document.createElement('style');
      s.textContent = `
        #npf-cursor { position:fixed; left:0; top:0; width:28px; height:28px;
          pointer-events:none; z-index:2147483647; transform:translate(-50%,-50%); }
        #npf-cursor .dot { width:10px; height:10px; background:#d98912; border-radius:50%;
          position:absolute; left:9px; top:9px; box-shadow:0 0 0 2px #fff8ee; }
        #npf-cursor .ring { width:28px; height:28px; border:2px solid #d98912; border-radius:50%; opacity:.75; }
        #npf-cursor.click .ring { animation: npfping .35s ease-out; }
        @keyframes npfping { from { transform:scale(1); opacity:.7;} to { transform:scale(1.9); opacity:0;} }
      `;
      const c = document.createElement('div');
      c.id = 'npf-cursor';
      c.innerHTML = '<div class="ring"></div><div class="dot"></div>';
      document.documentElement.appendChild(s);
      document.documentElement.appendChild(c);
      document.addEventListener('mousemove', e => {
        c.style.left = e.clientX + 'px';
        c.style.top = e.clientY + 'px';
      }, true);
      document.addEventListener('mousedown', () => {
        c.classList.add('click');
        setTimeout(() => c.classList.remove('click'), 360);
      }, true);
    }"""
    )


def inject_chip(page, label: str, bottom: bool = False) -> None:
    page.evaluate(
        """([label, bottom]) => {
      let chip = document.getElementById('npf-urlchip');
      if (!chip) {
        chip = document.createElement('div');
        chip.id = 'npf-urlchip';
        document.documentElement.appendChild(chip);
      }
      chip.textContent = label;
      Object.assign(chip.style, {
        position: 'fixed', left: '24px', zIndex: 2147483646,
        top: bottom ? 'auto' : '16px', bottom: bottom ? '18px' : 'auto',
        background: 'rgba(255,248,238,0.94)', color: '#3a2418',
        font: '600 16px Inter, Segoe UI, sans-serif',
        padding: '8px 16px', borderRadius: '999px',
        boxShadow: '0 8px 24px rgba(92,48,18,0.16)',
        pointerEvents: 'none', border: '1px solid rgba(140,88,36,0.18)'
      });
    }""",
        [label, bottom],
    )


def pad_to(page, start: float, seconds: float) -> None:
    left = seconds - (time.monotonic() - start)
    if left > 0.04:
        page.wait_for_timeout(int(left * 1000))
    elif left < -1.5:
        print(f"  ! chapter overran by {-left:.1f}s")


def move_click(page, locator, timeout: int = 15000) -> None:
    locator.first.wait_for(state="visible", timeout=timeout)
    locator.first.scroll_into_view_if_needed()
    box = locator.first.bounding_box()
    if box:
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=12)
        page.wait_for_timeout(180)
    locator.first.click()


def new_recording_page(p, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--hide-scrollbars"],
    )
    context = browser.new_context(
        viewport={"width": W, "height": H},
        device_scale_factor=1,
        user_agent=UA,
        record_video_dir=str(folder),
        record_video_size={"width": W, "height": H},
        color_scheme="light",
    )
    page = context.new_page()
    return browser, context, page


def dismiss_github(page) -> None:
    for name in ("Accept", "Accept all", "Got it", "Reject additional"):
        try:
            page.get_by_role("button", name=re.compile(name, re.I)).click(timeout=1200)
            page.wait_for_timeout(400)
        except Exception:
            pass
    page.evaluate(
        """() => {
      const hideSels = [
        '.Layout-sidebar',
        '[data-testid="repos-file-tree-container"]',
        'nav[aria-label="Files"]',
        '.footer',
        '.js-notification-shelf-offset-top',
      ];
      hideSels.forEach(sel => document.querySelectorAll(sel).forEach(el => el.style.display = 'none'));
      const md = document.querySelector('.markdown-body');
      if (md) md.style.maxWidth = '1100px';
    }"""
    )


def slow_scroll(page, pixels: int, duration_ms: int) -> None:
    steps = max(8, duration_ms // 80)
    dy = pixels / steps
    dt = duration_ms / steps
    for _ in range(steps):
        page.mouse.wheel(0, dy)
        page.wait_for_timeout(dt)


def record_live_home(p) -> Path:
    folder = RAW / "home"
    if folder.exists():
        shutil.rmtree(folder)
    browser, context, page = new_recording_page(p, folder)
    page.goto(LIVE, wait_until="networkidle", timeout=60000)
    page.get_by_role("heading", name="Neural Path Finder").wait_for()
    page.get_by_role("button", name=re.compile("Watch TV")).wait_for()
    inject_cursor(page)
    inject_chip(page, "Live  ·  fruitfly-poc.azurewebsites.net")
    start = time.monotonic()
    page.wait_for_timeout(16000)
    page.evaluate("() => document.querySelector('.board-wrap')?.scrollIntoView({block:'center'})")
    page.wait_for_timeout(2000)
    page.get_by_role("button", name=re.compile("Watch TV")).hover()
    pad_to(page, start, CHAPTERS["what"])
    video = Path(page.video.path())
    context.close()
    browser.close()
    dest = RAW / "home.webm"
    shutil.move(str(video), dest)
    return dest


def record_live_cando_demo(p) -> tuple[Path, Path]:
    folder = RAW / "play"
    if folder.exists():
        shutil.rmtree(folder)
    browser, context, page = new_recording_page(p, folder)
    dest = RAW / "play.webm"
    try:
        _record_live_cando_demo_inner(page)
    finally:
        video = Path(page.video.path()) if page.video else None
        context.close()
        browser.close()
        if video and video.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(video), dest)
    return dest, dest


def _record_live_cando_demo_inner(page) -> None:
    page.goto(LIVE, wait_until="networkidle", timeout=60000)
    page.get_by_role("button", name=re.compile("Watch TV")).wait_for()
    inject_cursor(page)
    inject_chip(page, "Live  ·  fruitfly-poc.azurewebsites.net")

    # --- what you can do ---
    t0 = time.monotonic()
    page.evaluate("() => document.querySelector('.board-wrap')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(800)
    per = 3.2
    for title in SCENES:
        loc = page.get_by_role("button", name=re.compile(re.escape(title)))
        try:
            loc.first.hover()
        except Exception:
            pass
        page.wait_for_timeout(int(per * 1000))
    try:
        page.get_by_role("button", name=re.compile("do they meet")).hover()
    except Exception:
        pass
    page.wait_for_timeout(3500)
    page.get_by_role("button", name="Scientist mode").hover()
    pad_to(page, t0, CHAPTERS["cando"])
    cando_end = page.evaluate("() => performance.now()")  # just a beat
    _ = cando_end
    # Playwright records one webm per page; split later by duration.
    # We keep a single play.webm covering cando+demo, then split in ffmpeg.

    # --- live demo, clocks match SCRIPT.md 2:20–4:00 ---
    t1 = time.monotonic()
    page.evaluate("() => window.scrollTo({top:0, behavior:'instant'})")
    page.wait_for_timeout(600)
    move_click(page, page.get_by_role("button", name=re.compile("Watch TV")))
    try:
        page.get_by_text(re.compile("Following the wires")).first.wait_for(timeout=15000)
    except Exception:
        pass
    try:
        page.get_by_text(re.compile("flickering screen")).first.wait_for(timeout=20000)
    except Exception:
        try:
            page.get_by_role("button", name=re.compile("Most direct")).first.wait_for(timeout=20000)
        except Exception:
            page.wait_for_timeout(1500)
    page.evaluate("() => document.getElementById('results')?.scrollIntoView({block:'start'})")
    pad_to(page, t1, 46)  # 3:06 tap R1
    try:
        hop = page.get_by_role("button", name=re.compile("R1 photoreceptor"))
        hop.first.scroll_into_view_if_needed()
        move_click(page, hop)
    except Exception as exc:
        print("  hop click skipped:", exc)
    pad_to(page, t1, 54)  # 3:14 strongest
    try:
        move_click(page, page.get_by_role("button", name=re.compile("Strongest connectivity")))
    except Exception as exc:
        print("  strongest skipped:", exc)
    pad_to(page, t1, 62)  # 3:22 zap
    page.evaluate("() => document.querySelector('.board-wrap')?.scrollIntoView({block:'center'})")
    page.wait_for_timeout(400)
    move_click(page, page.get_by_role("button", name=re.compile("Zapped By Human")))
    try:
        page.get_by_text(re.compile("Following the wires")).first.wait_for(timeout=12000)
        page.get_by_role("button", name=re.compile("Most direct")).first.wait_for(timeout=20000)
    except Exception:
        page.wait_for_timeout(2000)
    page.evaluate("() => document.getElementById('results')?.scrollIntoView({block:'start'})")
    pad_to(page, t1, 80)  # 3:40 compare
    page.evaluate("() => document.querySelector('.quick-compare')?.scrollIntoView({block:'center'})")
    page.wait_for_timeout(400)
    move_click(page, page.get_by_role("button", name=re.compile("do they meet")))
    try:
        page.get_by_text(re.compile("Taste food vs watch TV", re.I)).first.wait_for(timeout=20000)
    except Exception:
        page.wait_for_timeout(2000)
    page.evaluate("() => document.getElementById('results')?.scrollIntoView({block:'start'})")
    pad_to(page, t1, 92)  # 3:52 open scientist so the panel is visible at 3:56
    move_click(page, page.get_by_role("button", name="Scientist mode"))
    page.wait_for_timeout(800)
    try:
        page.locator("#scientist-panel").scroll_into_view_if_needed()
    except Exception:
        pass
    pad_to(page, t1, 96)
    try:
        move_click(page, page.get_by_role("button", name=re.compile("Classic demo")))
        page.get_by_role("button", name=re.compile("Most direct")).first.wait_for(timeout=20000)
        page.evaluate("() => document.getElementById('scientist-panel')?.scrollIntoView({block:'center'})")
    except Exception as exc:
        print("  scientist skipped:", exc)
    pad_to(page, t1, CHAPTERS["demo"])


def record_github_clip(
    p, url: str, seconds: float, dest_webm: Path, scroll_px: int = 1400, find_text: str | None = None
) -> Path:
    folder = RAW / dest_webm.stem
    if folder.exists():
        shutil.rmtree(folder)
    browser, context, page = new_recording_page(p, folder)
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2500)
    dismiss_github(page)
    inject_cursor(page)
    inject_chip(page, url.replace("https://", ""), bottom=True)
    start = time.monotonic()
    try:
        page.locator(".markdown-body, .blob-code, article").first.wait_for(timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(1800)
    if find_text:
        page.evaluate(
            """(needle) => {
          const nodes = [...document.querySelectorAll('h1,h2,h3,p,pre')];
          const hit = nodes.find(el => (el.textContent || '').toLowerCase().includes(needle.toLowerCase()));
          if (hit) hit.scrollIntoView({block:'start'});
        }""",
            find_text,
        )
        page.wait_for_timeout(800)
    slow_scroll(page, scroll_px, int(min(seconds - 4, seconds * 0.65) * 1000))
    pad_to(page, start, seconds)
    video = Path(page.video.path())
    context.close()
    browser.close()
    dest_webm.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(video), dest_webm)
    return dest_webm


def screenshot_mermaid(p) -> dict[str, Path]:
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    html_path = DIAGRAMS / "mermaid.html"
    html_path.write_text(MERMAID_HTML, encoding="utf-8")
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto(html_path.as_uri(), wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)
    try:
        page.locator("svg").first.wait_for(timeout=15000)
    except Exception:
        pass
    out = {}
    for key in ("runtime", "sequence", "stages", "modules"):
        loc = page.locator(f"#{key}")
        loc.wait_for()
        loc.scroll_into_view_if_needed()
        page.wait_for_timeout(400)
        dest = DIAGRAMS / f"{key}.png"
        loc.screenshot(path=str(dest))
        out[key] = dest
    browser.close()
    return out


def write_ass_from_srt() -> Path:
    """SRT times + 1080p PlayRes so captions stay small enough to read the UI."""
    text = CAPTIONS.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text.strip())
    dialogues = []
    for block in blocks:
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.search(
            r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})",
            lines[1],
        )
        if not m:
            continue
        sh, sm, ss, sms, eh, em, es, ems = m.groups()
        start = f"{int(sh)}:{sm}:{ss}.{sms[:2]}"
        end = f"{int(eh)}:{em}:{es}.{ems[:2]}"
        body = "\\N".join(lines[2:]).replace("{", "\\{")
        dialogues.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{body}")
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Inter,36,&H00FFFFFF,&H000000FF,&H00201830,&H80000000,1,0,0,0,100,100,0,0,1,3,0,2,70,70,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(dialogues) + "\n"
    CAPTIONS_ASS.write_text(ass, encoding="utf-8")
    return CAPTIONS_ASS


def concat_and_caption(parts: list[Path]) -> Path:
    BUILD.mkdir(parents=True, exist_ok=True)
    lst = BUILD / "concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    naked = BUILD / "naked.mp4"
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c",
            "copy",
            str(naked),
        ]
    )
    write_ass_from_srt()
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(naked),
            "-vf",
            f"ass={CAPTIONS_ASS},format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(MASTER),
        ]
    )
    return MASTER


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def split_play(play_webm: Path) -> tuple[Path, Path]:
    """play.webm is cando then demo, padded in the recorder."""
    full = BUILD / "play_full.mp4"
    fit_webm(play_webm, CHAPTERS["cando"] + CHAPTERS["demo"], full)
    cando = BUILD / "cando.mp4"
    demo = BUILD / "demo.mp4"
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(full),
            "-t",
            f"{CHAPTERS['cando']:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            str(cando),
        ]
    )
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{CHAPTERS['cando']:.3f}",
            "-i",
            str(full),
            "-t",
            f"{CHAPTERS['demo']:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "aac",
            str(demo),
        ]
    )
    return cando, demo


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-record", action="store_true")
    parser.add_argument(
        "--clips",
        default="",
        help="comma list to re-record only: home,play,github,mermaid",
    )
    args = parser.parse_args()
    wanted = {c.strip() for c in args.clips.split(",") if c.strip()}

    for d in (STILLS, DIAGRAMS, RAW, BUILD):
        d.mkdir(parents=True, exist_ok=True)

    cards = make_title_cards()
    print("title cards:", cards)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        diagrams = screenshot_mermaid(p)
        print("mermaid:", diagrams)
        rec_all = not args.skip_record and not wanted
        if rec_all or "home" in wanted:
            if rec_all and (RAW / "home.webm").exists() and (RAW / "home.webm").stat().st_size > 10000:
                print("reusing", RAW / "home.webm")
            else:
                print("home", record_live_home(p))
        if rec_all or "play" in wanted:
            print("play", record_live_cando_demo(p)[0])
        if rec_all or "github" in wanted:
            gen = record_github_clip(p, GEN_PY, CHAPTERS["data_gen"], RAW / "data_gen.webm", scroll_px=900)
            stats = record_github_clip(
                p, ARCH, CHAPTERS["data_stats"], RAW / "data_stats.webm", scroll_px=1100
            )
            arch = record_github_clip(
                p,
                ARCH + "#4-diagrams",
                CHAPTERS["arch_github"],
                RAW / "arch_github.webm",
                scroll_px=2200,
            )
            print("github clips", gen, stats, arch)
        if rec_all or "github" in wanted or "readme" in wanted:
            readme = record_github_clip(
                p,
                README,
                CHAPTERS["arch_readme"],
                RAW / "readme_runtime.webm",
                scroll_px=900,
                find_text="How it works",
            )
            print("readme", readme)

    parts: list[Path] = []
    parts.append(still_mp4(cards["title"], CHAPTERS["title"], BUILD / "01_title.mp4"))
    parts.append(fit_webm(RAW / "home.webm", CHAPTERS["what"], BUILD / "02_what.mp4"))
    parts.append(still_mp4(cards["data_a"], CHAPTERS["data_card_a"], BUILD / "03_data_a.mp4"))
    parts.append(still_mp4(cards["data_b"], CHAPTERS["data_card_b"], BUILD / "04_data_b.mp4"))
    parts.append(fit_webm(RAW / "data_gen.webm", CHAPTERS["data_gen"], BUILD / "05_data_gen.mp4"))
    parts.append(fit_webm(RAW / "data_stats.webm", CHAPTERS["data_stats"], BUILD / "06_data_stats.mp4"))
    cando, demo = split_play(RAW / "play.webm")
    parts.append(cando)
    parts.append(demo)
    parts.append(still_mp4(cards["arch"], CHAPTERS["arch_card"], BUILD / "09_arch_card.mp4"))
    parts.append(fit_webm(RAW / "arch_github.webm", CHAPTERS["arch_github"], BUILD / "10_arch_gh.mp4"))
    parts.append(fit_webm(RAW / "readme_runtime.webm", CHAPTERS["arch_readme"], BUILD / "11_readme.mp4"))
    parts.append(still_mp4(DIAGRAMS / "sequence.png", CHAPTERS["arch_seq"], BUILD / "12_seq.mp4"))
    parts.append(still_mp4(DIAGRAMS / "stages.png", CHAPTERS["arch_stages"], BUILD / "13_stages.mp4"))
    parts.append(still_mp4(DIAGRAMS / "modules.png", CHAPTERS["arch_modules"], BUILD / "14_modules.mp4"))
    parts.append(still_mp4(cards["outro"], CHAPTERS["outro"], BUILD / "15_outro.mp4", kenburns=False))

    concat_and_caption(parts)
    dur = probe_duration(MASTER)
    print(f"MASTER {MASTER} duration={dur:.2f}s")
    expected = sum(CHAPTERS.values())
    print(f"expected {expected:.2f}s")
    art = Path("/opt/cursor/artifacts")
    if art.is_dir() and MASTER.exists():
        shutil.copy2(MASTER, art / "neural_path_finder_product.mp4")
        shutil.copy2(CAPTIONS, art / "neural_path_finder_captions.srt")
        shutil.copy2(VIDEO / "SCRIPT.md", art / "neural_path_finder_SCRIPT.md")
        print("copied artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
