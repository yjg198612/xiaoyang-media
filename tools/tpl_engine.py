# -*- coding: utf-8 -*-
"""自制「模板样式」口播版式引擎（纯开源：ffmpeg + Pillow + ASS）
版式仿「黑底大字 + 真人窗口 + 底部字幕」，不依赖任何付费模板，0 积分 0 联网校验。
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work", "out", "v1_nosub.mp4")          # 已裁切调色的真人素材
WORK = os.path.join(ROOT, "work", "tpl")
OUTDIR = os.path.join(ROOT, "content", "2026-10-27")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

W, H = 1080, 1920
WIN_W, WIN_H, WIN_X, WIN_Y = 800, 860, 140, 690
RADIUS = 26

BG_TOP, BG_BOT = (22, 36, 47), (11, 19, 27)
CYAN = "&HF5D05F"      # ASS 用 BGR：#5FD0F5
WHITE = "&HFCF7F0"
GRAY = "&HB29E8A"
DIM = "&H916E50"


def make_bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        e = (y / (H - 1)) ** 0.9
        d.line([(0, y), (W, y)], fill=tuple(
            int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * e) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-280, -420, 880, 620], fill=(16, 50, 68))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(240)))

    # 真人窗口的投影，让窗口“浮”起来
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle(
        [WIN_X - 26, WIN_Y - 14, WIN_X + WIN_W + 26, WIN_Y + WIN_H + 40],
        radius=RADIUS + 10, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(34))
    img = Image.composite(Image.new("RGB", (W, H), (4, 7, 10)), img, sh)
    p = os.path.join(WORK, "bg.png")
    img.save(p)
    return p


def make_mask():
    m = Image.new("L", (WIN_W, WIN_H), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, WIN_W - 1, WIN_H - 1], radius=RADIUS, fill=255)
    rgba = Image.new("RGBA", (WIN_W, WIN_H), (255, 255, 255, 0))
    rgba.putalpha(m)
    p = os.path.join(WORK, "mask.png")
    rgba.save(p)
    return p


HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Microsoft YaHei,36,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,9,0,1,0,0,7,60,60,150,1
Style: Title,Microsoft YaHei,112,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,7,60,60,270,1
Style: Sub,Microsoft YaHei,58,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,3.4,1.2,2,50,50,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (GRAY, WHITE, WHITE)


def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


# 大字标题分三段推进（跟着音频走）
TITLES = [
    (0.00, 7.90, [("招人的就", 116, WHITE), ("两家", 116, CYAN)]),
    (8.00, 12.50, [("一家写着", 104, WHITE), ("35岁以下", 104, CYAN)]),
    (12.60, 18.50, [("我今年", 104, WHITE), ("40岁", 104, CYAN)]),
]

SUBS = [
    (0.10, 2.30, "我在一个没有网约车的县城"),
    (2.46, 4.40, "失业快3年"),
    (4.40, 6.55, "今天在街上转了一上午"),
    (6.55, 7.85, "招人的就两家"),
    (8.06, 9.95, "一家写着35岁以下"),
    (10.16, 12.55, "一家工资只有2800"),
    (12.55, 14.15, "我今年40岁了"),
    (14.36, 16.00, "连被挑的资格都没有"),
    (16.21, 18.10, "你们那还有活干吗"),
]


def build_ass():
    L = [HEAD]
    L.append(f"Dialogue: 0,{ts(0)},{ts(99)},Label,,0,0,0,,"
             + "中年自救日记 {\\c" + CYAN + "&}●{\\c" + WHITE + "&} 县城 · 白天")
    for a, b, segs in TITLES:
        # 两行：按段内空格拆分；无空格则整行
        body = "".join(
            "{\\c" + c + "&}" + t for t, sz, c in segs)
        L.append(f"Dialogue: 1,{ts(a)},{ts(b)},Title,,0,0,0,,"
                 f"{{\\fad(260,160)\\t(0,300,\\fscx104\\fscy104)}}{body}")
    for a, b, text in SUBS:
        L.append(f"Dialogue: 2,{ts(a)},{ts(b)},Sub,,0,0,0,,{text}")
    p = os.path.join(WORK, "tpl.ass")
    open(p, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    return p


def render(bg, mask):
    dst = os.path.join(OUTDIR, "口播_模板版_招人就两家_18s.mp4")
    fc = (
        f"[1:v]scale={WIN_W}:-1,crop={WIN_W}:{WIN_H}:0:20,format=rgba[person];"
        f"[2:v]format=rgba[mask];"
        f"[person][mask]alphamerge[p2];"
        f"[0:v][p2]overlay={WIN_X}:{WIN_Y}[base];"
        f"[base]ass=tpl.ass,format=yuv420p[vout]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-i", bg,
           "-i", SRC,
           "-loop", "1", "-framerate", "30", "-i", mask,
           "-filter_complex", fc,
           "-map", "[vout]", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-profile:v", "high", "-level", "4.1", "-r", "30",
           "-c:a", "copy", "-shortest", "-movflags", "+faststart", dst]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=WORK)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    return dst


if __name__ == "__main__":
    bg = make_bg(); mask = make_mask(); build_ass()
    print("OK ->", render(bg, mask))
