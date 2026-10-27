# -*- coding: utf-8 -*-
"""口播模板引擎 v3 —— 场景版式系统（对应模板「现代图文」的版面重构）
改进点：
  1. 每段内容一套独立版面（居中/左对齐/列表/药丸标签），不再是"换字不换版"
  2. 段落交接处重叠 0.15s，消除标题真空
  3. 加包装层：左上角作者、右上角时间码
  4. 无底部字幕，版面文字即字幕（对齐模板做法）
素材：微信 36.2s / 540x960 / 24fps，无烧死字幕
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = r"C:\Users\yjg198612\Documents\xwechat_files\wxid_84aqoy41tsam42_7626\msg\video\2026-10\10abd88415b7dc91da19e70d9bcf8436.mp4"
WORK = os.path.join(ROOT, "work", "scene")
OUTDIR = os.path.join(ROOT, "content", "2026-10-27")
os.makedirs(WORK, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)

W, H = 1080, 1920
WIN_W, WIN_H, WIN_X, WIN_Y = 780, 880, 150, 760
CROP_Y = 55
RADIUS = 26

WHITE, CYAN = "&HFCF7F0", "&HF5D05F"      # ASS = BGR
DARK = "&H2F2416"
GRAY, DIMC = "&HB29E8A", "&H8A7A66"

# 源片段：去掉开头「啊？」和大量空白停顿
SEGS = [
    (6.02, 9.20),     # 一个40多岁的男人 / 最怕啥？
    (10.54, 15.70),   # 我最怕的，是明明撑不住了，回家还得装
    (16.98, 23.55),   # 县城租的房子打算退了 / 回市里 / 跟老婆孩子住
    (25.35, 27.85),   # 这三年啥也没干成
    (29.63, 33.98),   # 下一步不知道咋办 / 你们有什么建议
]

T = []              # 时间轴
acc = 0.0
for a, b in SEGS:
    T.append((acc, acc + (b - a), a))
    acc += (b - a)
TOTAL = acc          # 21.76s
OVERLAP = 0.0        # 不做重叠：重叠会让两套版面文字叠在一起


def ts(t):
    t = max(t, 0)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def f(tag=0):
    """淡入淡出，tag 区分不同节奏"""
    return r"{\fad(260,260)}" if tag == 0 else r"{\fad(300,220)}"


def rise(dy=26, dur=320):
    return r"\move(%d,%d,%d,%d,0,%d)\fscx97\fscy97\t(0,%d,\fscx100\fscy100)"


def build_bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top, bot = (22, 36, 47), (11, 19, 27)
    for y in range(H):
        e = (y / (H - 1)) ** 0.9
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * e) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-280, -420, 880, 620], fill=(16, 50, 68))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(240)))

    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle(
        [WIN_X - 18, WIN_Y - 8, WIN_X + WIN_W + 18, WIN_Y + WIN_H + 30],
        radius=RADIUS + 8, fill=150)
    img = Image.composite(Image.new("RGB", (W, H), (4, 7, 10)), img,
                          sh.filter(ImageFilter.GaussianBlur(28)))
    # 左上装饰短线
    ImageDraw.Draw(img).line([(150, 214), (150 + 56, 214)], fill=(95, 208, 245), width=4)
    p = os.path.join(WORK, "bg.png"); img.save(p); return p


def build_mask():
    m = Image.new("L", (WIN_W, WIN_H), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, WIN_W - 1, WIN_H - 1], radius=RADIUS, fill=255)
    rgba = Image.new("RGBA", (WIN_W, WIN_H), (255, 255, 255, 0))
    rgba.putalpha(m)
    p = os.path.join(WORK, "mask.png"); rgba.save(p); return p


HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Microsoft YaHei,32,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,9,0,1,0,0,7,150,60,186,1
Style: Code,Microsoft YaHei,30,%s,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,9,60,150,182,1
Style: M,Microsoft YaHei,110,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,8,80,80,0,1
Style: L,Microsoft YaHei,96,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,0,0,7,90,60,0,1
Style: ML,Microsoft YaHei,110,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,0,0,7,90,60,0,1
Style: Tag,Microsoft YaHei,54,%s,&H000000FF,&H00F5D05F,&H00000000,-1,0,0,0,100,100,2,0,3,22,0,8,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (GRAY, DIMC, WHITE, WHITE, WHITE, DARK)


def ev(layer, a, b, style, text):
    return f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{text}"


def build_ass():
    L = [HEAD]
    # 包装层
    L.append(ev(0, 0, 99, "Label", "中年自救日记"))
    for s in range(int(TOTAL) + 1):
        L.append(ev(0, s, s + 1, "Code", f"00:{s:02d}"))

    # 场景1：居中问句  0 ~ S1end
    s1a, s1b = 0.00, T[0][1] + OVERLAP
    L.append(ev(1, s1a, s1b, "M",
                r"{\fad(260,240)\move(540,470,540,440,0,340)}"
                f"40多岁{{\\c{CYAN}&}}的男人".replace("{CYAN}", CYAN)))
    L.append(ev(2, s1a + 0.45, s1b, "M",
                r"{\fad(240,200)\move(540,640,540,610,0,300)}"
                f"最怕{{\\c{CYAN}&}}啥{{\\c{WHITE}&}}".replace("{CYAN}", CYAN).replace("{WHITE}", WHITE)))

    # 场景2：左对齐三行  3.18 ~ 8.34
    a2 = T[1][0] - OVERLAP
    L.append(ev(1, a2, T[1][1] + OVERLAP, "L",
                f"{{\\fad(190,130)\\move(90,356,90,330,0,320)}}我最怕的，是"))
    L.append(ev(2, a2 + 0.55, T[1][1] + OVERLAP, "ML",
                f"{{\\fad(190,130)\\move(90,506,90,480,0,320)}}明明{{\\c{CYAN}&}}撑不住{{\\c{WHITE}&}}了".replace("{CYAN}", CYAN).replace("{WHITE}", WHITE)))
    L.append(ev(3, a2 + 1.30, T[1][1] + OVERLAP, "L",
                f"{{\\fad(190,130)\\move(90,656,90,630,0,320)}}回家还得装"))

    # 场景3：列表  8.34 ~ 14.91
    a3 = T[2][0] - OVERLAP
    lines = [("退掉县城的房子", 320, WHITE), ("回市里", 470, CYAN), ("跟老婆孩子住", 620, WHITE)]
    for i, (txt, y, col) in enumerate(lines):
        L.append(ev(1 + i, a3 + i * 0.30, T[2][1] + OVERLAP, "ML",
                    f"{{\\fad(190,130)\\move(120,{y+24},120,{y},0,300)}}{{\\c{col}&}}{txt}".replace("{col}", col)))

    # 场景4：居中两行 14.91 ~ 17.41
    a4 = T[3][0] - OVERLAP
    L.append(ev(1, a4, T[3][1] + OVERLAP, "M",
                r"{\fad(240,220)\move(540,470,540,440,0,320)}这三年"))
    L.append(ev(2, a4 + 0.40, T[3][1] + OVERLAP, "M",
                f"{{\\fad(190,130)\\move(540,650,540,620,0,320)}}{{\\c{CYAN}&}}啥也没干成".replace("{CYAN}", CYAN)))

    # 场景5：问句 + 药丸标签 17.41 ~ 结束
    a5 = T[4][0] - OVERLAP
    L.append(ev(1, a5, TOTAL, "M",
                r"{\fad(260,300)\move(540,362,540,334,0,320)}下一步"))
    L.append(ev(2, a5 + 0.45, TOTAL, "M",
                f"{{\\fad(190,130)\\move(540,506,540,478,0,320)}}不知道该{{\\c{CYAN}&}}咋办".replace("{CYAN}", CYAN)))
    L.append(ev(3, a5 + 1.20, TOTAL, "Tag",
                r"{\fad(280,300)\move(540,644,540,616,0,320)}你们有什么建议？"))

    p = os.path.join(WORK, "scene.ass")
    open(p, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    return p


def render():
    bg, mask, ass = build_bg(), build_mask(), build_ass()
    dst = os.path.join(OUTDIR, "口播_场景版_40岁最怕啥_22s.mp4")
    n = len(SEGS)
    fc = []
    for i, (a, b) in enumerate(SEGS):
        fc.append(f"[1:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[1:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]")
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[pv]")
    fc.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[pa]")
    fc.append(f"[pv]crop=540:609:0:{CROP_Y},scale={WIN_W}:{WIN_H}:flags=lanczos,format=rgba[person]")
    fc.append(f"[2:v]format=rgba,scale={WIN_W}:{WIN_H}[mk]")
    fc.append("[person][mk]alphamerge,fade=t=in:st=0:d=0.45:alpha=1[p2]")
    fc.append(f"[0:v][p2]overlay={WIN_X}:'{WIN_Y}+48*max(0,1-t/0.5)'[base]")
    fc.append(f"[base]ass={os.path.basename(ass)},format=yuv420p[vout]")
    fc.append("[pa]afftdn=nf=-28,loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000,alimiter=limit=0.95[aout]")

    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", "60", "-i", bg,
           "-i", SRC,
           "-loop", "1", "-framerate", "60", "-i", mask,
           "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-profile:v", "high", "-level", "4.1", "-r", "60", "-g", "120",
           "-c:a", "aac", "-b:a", "192k", "-ac", "2",
           "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", dst]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=WORK)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    return dst


if __name__ == "__main__":
    print("时长", round(TOTAL, 2), "s")
    print("OK ->", render())
