# -*- coding: utf-8 -*-
"""自制口播模板引擎 v2 —— 三套版式变体 + 动效（ffmpeg + Pillow + ASS，零依赖零积分）
字幕上移到画面底部 300px 以上，避开抖音 UI 遮挡区。
用法： python tools/tpl_engine.py all     或     python tools/tpl_engine.py A
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work", "out", "v1_nosub.mp4")
WORK = os.path.join(ROOT, "work", "tpl2")
OUTDIR = os.path.join(ROOT, "content", "2026-10-27")
os.makedirs(WORK, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)

W, H = 1080, 1920

SUB_MARGIN_V = 340          # 字幕底边距画面底部 300px —— 抖音安全区
TITLE_TOP = 250
LABEL_TOP = 170

WIN_W, WIN_H = 780, 870
WIN_X = (W - WIN_W) // 2
WIN_Y = 500                 # 470~1410，与字幕(1548)间留 138px
CROP_Y = 10
RADIUS = 26

C_WHITE, C_CYAN = "&HFCF7F0", "&HF5D05F"     # ASS 为 BGR
C_DARK, C_CYAN_D = "&H2F2416", "&HC08F1F"

VARIANTS = {
    "A": dict(label="黑底大字", bg_top=(22, 36, 47), bg_bot=(11, 19, 27),
              glow=(16, 50, 68), text=C_WHITE, accent=C_CYAN,
              sub_outline="&H00000000", full=False, shadow=(4, 7, 10)),
    "B": dict(label="浅底图文", bg_top=(241, 245, 248), bg_bot=(212, 223, 231),
              glow=(190, 220, 236), text=C_DARK, accent=C_CYAN_D,
              sub_outline="&H00FFFFFF", full=False, shadow=(118, 138, 152)),
    "C": dict(label="全屏真人", bg_top=(14, 20, 26), bg_bot=(8, 12, 16),
              glow=(16, 44, 60), text=C_WHITE, accent=C_CYAN,
              sub_outline="&H00000000", full=True, shadow=None),
}

TITLES = [
    (0.00, 7.90, [("招人的就", 112, "T"), ("两家", 112, "A")]),
    (8.00, 12.50, [("一家写着", 104, "T"), ("35岁以下", 104, "A")]),
    (12.60, 18.50, [("我今年", 104, "T"), ("40岁", 104, "A")]),
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


def _grad(top, bot):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        e = (y / (H - 1)) ** 0.9
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * e) for i in range(3)))
    return img


def make_bg(cfg, tag):
    img = _grad(cfg["bg_top"], cfg["bg_bot"])
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-280, -420, 880, 620], fill=cfg["glow"])
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(240)))

    if not cfg["full"]:
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).rounded_rectangle(
            [WIN_X - 20, WIN_Y - 8, WIN_X + WIN_W + 20, WIN_Y + WIN_H + 30],
            radius=RADIUS + 8, fill=145)
        img = Image.composite(Image.new("RGB", (W, H), cfg["shadow"]), img,
                              sh.filter(ImageFilter.GaussianBlur(28)))
    p = os.path.join(WORK, f"bg_{tag}.png")
    img.save(p)
    return p


def make_mask():
    m = Image.new("L", (WIN_W, WIN_H), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, WIN_W - 1, WIN_H - 1], radius=RADIUS, fill=255)
    rgba = Image.new("RGBA", (WIN_W, WIN_H), (255, 255, 255, 0))   # RGB 必须全白
    rgba.putalpha(m)
    p = os.path.join(WORK, "mask.png")
    rgba.save(p)
    return p


def make_bottom_fade():
    """全屏版：底部渐变压黑，盖掉原片旧字幕，同时给新字幕留底"""
    a = Image.new("L", (W, H), 0)
    px = a.load()
    for y in range(H):
        v = 0 if y < 1120 else (255 if y >= 1270 else int(255 * (y - 1120) / 150))
        for x in range(W):
            px[x, y] = v
    rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rgba.putalpha(a)
    p = os.path.join(WORK, "fade.png")
    rgba.save(p)
    return p


def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def build_ass(cfg, tag):
    T, A = cfg["text"], cfg["accent"]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Microsoft YaHei,34,{A},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,10,0,1,0,0,8,60,60,{LABEL_TOP},1
Style: Title,Microsoft YaHei,112,{T},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,8,60,60,{TITLE_TOP},1
Style: Sub,Microsoft YaHei,58,{T},&H000000FF,{cfg['sub_outline']},&H00000000,-1,0,0,0,100,100,1,0,1,3.4,1.2,2,50,50,{SUB_MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    L = [head]
    L.append(f"Dialogue: 0,{ts(0)},{ts(99)},Label,,0,0,0,,"
             f"中年自救日记 {{\\c{A}&}}●{{\\c{T}&}} 县城 · 白天")

    for a, b, segs in TITLES:
        body = "".join("{\\c" + (T if k == "T" else A) + "&}" + t for t, sz, k in segs)
        anim = (r"{\fad(300,180)\move(540,%d,540,%d,0,340)"
                r"\fscx94\fscy94\t(0,340,\fscx100\fscy100)}"
                % (TITLE_TOP - 34, TITLE_TOP))
        L.append(f"Dialogue: 1,{ts(a)},{ts(b)},Title,,0,0,0,,{anim}{body}")

    for a, b, text in SUBS:
        L.append(f"Dialogue: 2,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad(240,140)}}{text}")

    p = os.path.join(WORK, f"sub_{tag}.ass")
    open(p, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    return p


def _enc(dst, extra_map):
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-profile:v", "high", "-level", "4.1", "-r", "30"] + extra_map + \
           ["-shortest", "-movflags", "+faststart", dst]


def render(tag):
    cfg = VARIANTS[tag]
    ass = build_ass(cfg, tag)
    dst = os.path.join(OUTDIR, f"口播_模板{tag}_{cfg['label']}_18s.mp4")

    if cfg["full"]:
        fade = make_bottom_fade()
        fc = (f"[0:v]scale={W}:{H},format=yuv420p[base];"
              f"[base][1:v]overlay=0:0[dim];"
              f"[dim]ass={os.path.basename(ass)},format=yuv420p[vout]")
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", SRC,
               "-loop", "1", "-framerate", "30", "-i", fade,
               "-filter_complex", fc, "-map", "[vout]", "-map", "0:a"] \
              + _enc(dst, ["-c:a", "copy"])
    else:
        bg, mask = make_bg(cfg, tag), make_mask()
        fc = (f"[1:v]scale={WIN_W}:-1,crop={WIN_W}:{WIN_H}:0:{CROP_Y},format=rgba[person];"
              f"[2:v]format=rgba,scale={WIN_W}:{WIN_H}[mk];"
              f"[person][mk]alphamerge,fade=t=in:st=0:d=0.40:alpha=1[p2];"
              f"[0:v][p2]overlay={WIN_X}:'{WIN_Y}+44*max(0,1-t/0.45)'[base];"
              f"[base]ass={os.path.basename(ass)},format=yuv420p[vout]")
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-loop", "1", "-framerate", "30", "-i", bg,
               "-i", SRC,
               "-loop", "1", "-framerate", "30", "-i", mask,
               "-filter_complex", fc, "-map", "[vout]", "-map", "1:a"] \
              + _enc(dst, ["-c:a", "copy"])

    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=WORK)
    if r.returncode != 0:
        print(f"[{tag}] FAIL\n", r.stderr[-1500:]); return None
    return dst


if __name__ == "__main__":
    want = (sys.argv[1] if len(sys.argv) > 1 else "all").upper()
    for t in (list(VARIANTS) if want == "ALL" else [want]):
        p = render(t)
        if p:
            print(f"[{t}] OK -> {os.path.basename(p)}  {os.path.getsize(p)//1024} KB")
