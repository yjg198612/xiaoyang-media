# -*- coding: utf-8 -*-
"""六镜混合版式成片 v2
改动：开头改全屏；药丸改为青底深字（原先是青字青底，看不见）；镜头节奏 全/窗/全/卡/窗/全
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work", "mix2")
OUTDIR = os.path.join(ROOT, "content", "2026-10-28")
SRC = r"C:\Users\yjg198612\Documents\xwechat_files\wxid_84aqoy41tsam42_7626\msg\video\2026-10\10abd88415b7dc91da19e70d9bcf8436.mp4"
os.makedirs(WORK, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)

W, H = 1080, 1920
FB, FR = "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"
BG, INK, ACC = (233, 238, 242), (22, 36, 47), (31, 127, 208)
CARD, CARDTX, MUTED = (22, 36, 47), (240, 247, 252), (107, 130, 150)
FACE_BOX = (22, 214, 452, 644)

SHOTS = [
    dict(kind="full",  tl=(0.00, 3.00), src=(6.30, 9.30),
         lines=[(0.10, 2.10, "BigD", "一个40多岁的男人", None, 540, 1556),
                (2.18, 2.99, "BigD", "最怕啥", "cyan", 540, 1556)]),
    dict(kind="pip",   tl=(3.00, 8.20), src=(10.70, 15.90),
         lines=[(0.10, 5.20, "SubL", "三年，三次决定", None, 90, 560),
                (2.60, 5.20, "SubL", "退房 → 回市里 → 陪家人", "blue", 90, 1450)]),
    dict(kind="full",  tl=(8.20, 11.20), src=(17.20, 20.20),
         lines=[(0.20, 3.00, "BigD", "退掉县城的房子", None, 540, 1556)]),
    dict(kind="card4", tl=(11.20, 14.75), src=(20.20, 23.75),
         lines=[(0.10, 3.55, "SubL", "县城这三年", None, 90, 640)]),
    dict(kind="pip",   tl=(14.75, 17.15), src=(25.60, 28.00),
         lines=[(0.10, 1.28, "SubL", "这三年", None, 90, 560),
                (1.28, 2.40, "SubL", "啥也没干成", "blue", 90, 560)]),
    dict(kind="big",   tl=(17.15, 21.45), src=(29.90, 34.20),
         lines=[(0.10, 2.25, "BigD", "下一步", None, 540, 1330),
                (2.20, 4.30, "BigD", "不知道该咋办", "cyan", 540, 1458),
                ]),
]
TOTAL = SHOTS[-1]["tl"][1]


def f(p, s):
    return ImageFont.truetype(p, s)


def noise(img, amt=5):
    n = Image.effect_noise((img.width, img.height), 7).convert("L")
    return Image.composite(img.point(lambda v: min(255, v + amt)), img,
                           n.point(lambda v: 255 if v > 138 else 0))


def light_bg():
    return noise(Image.new("RGB", (W, H), BG))


def avatar(size=190):
    im = Image.open(os.path.join(ROOT, "work", "mock", "fr_20.png")).convert("RGB")
    sq = im.crop(FACE_BOX).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(sq, (0, 0), m)
    ImageDraw.Draw(out).ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 235), width=3)
    return out


def circle_at(img, cx, cy, size=190):
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([cx - size // 2, cy - size // 2 + 6,
                                cx + size // 2, cy + size // 2 + 14], fill=90)
    img.paste(Image.new("RGB", (W, H), (60, 70, 80)), (0, 0),
              sh.filter(ImageFilter.GaussianBlur(14)))
    av = avatar(size)
    img.paste(av, (cx - size // 2, cy - size // 2), av)


def header(d, idx, name, code):
    d.text((72, 150), f"{idx} · {name}", font=f(FR, 34), fill=MUTED, anchor="ls")
    d.text((1008, 150), code, font=f(FR, 34), fill=MUTED, anchor="rs")
    d.line([(72, 186), (1008, 186)], fill=MUTED, width=1)


def make_card4():
    img = light_bg(); d = ImageDraw.Draw(img)
    header(d, "04", "这三年", "00:21")
    circle_at(img, 810, 430)
    cards = [("01", "退房"), ("02", "回市里"), ("03", "陪家人")]
    x, y, cw, ch, gap = 90, 720, 296, 280, 26
    for i, (no, t) in enumerate(cards):
        bgc = ACC if i == 2 else CARD
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=6, fill=bgc)
        d.text((x + 24, y + 44), no, font=f(FR, 32), fill=CARDTX, anchor="ls")
        d.line([(x + 24, y + 92), (x + cw - 24, y + 92)], fill=CARDTX, width=2)
        d.text((x + 24, y + 176), t, font=f(FB, 60), fill=CARDTX, anchor="ls")
        x += cw + gap
    d.text((W // 2, 1750), "3 年 · 3 个决定", font=f(FR, 26), fill=MUTED, anchor="ms")
    p = os.path.join(WORK, "card4.png"); img.save(p); return p


def make_pip_bg(idx, name, code):
    img = light_bg(); d = ImageDraw.Draw(img)
    header(d, idx, name, code)
    wx, wy, ww, wh = 400, 640, 620, 700
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([wx - 14, wy - 6, wx + ww + 14, wy + wh + 26],
                                         radius=34, fill=120)
    img.paste(Image.new("RGB", (W, H), (70, 82, 94)), (0, 0),
              sh.filter(ImageFilter.GaussianBlur(20)))
    p = os.path.join(WORK, f"bgpip_{idx}.png"); img.save(p); return p


def make_mask(w, h, r=26):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    out = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    out.putalpha(m)
    p = os.path.join(WORK, f"mask_{w}x{h}.png"); out.save(p); return p


def make_pill():
    tw, th, y = 520, 100, 1492
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(W - tw) // 2, y, (W + tw) // 2, y + th], radius=th // 2,
                        fill=(95, 208, 245, 255))
    d.text((W // 2, y + th // 2 + 2), "你们有什么建议？", font=f(FB, 46),
           fill=(22, 36, 47, 255), anchor="mm")
    p = os.path.join(WORK, "pill.png"); img.save(p); return p


def make_grad():
    a = Image.new("L", (W, H), 0)
    px = a.load()
    for y in range(H):
        v = int(215 * min(1, (y - 1100) / 320)) if y > 1100 else (
            int(140 * min(1, (300 - y) / 300)) if y < 300 else 0)
        for x in range(W):
            px[x, y] = v
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g.putalpha(a)
    p = os.path.join(WORK, "grad.png"); g.save(p); return p


HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubL,Microsoft YaHei,80,&H2F2416,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,0,0,7,90,60,0,1
Style: BigD,Microsoft YaHei,116,&HFCF7F0,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,5,2,2,60,60,0,1
Style: TagD,Microsoft YaHei,46,&H2F2416,&H000000FF,&HF5D05F,&H00000000,-1,0,0,0,100,100,2,0,3,18,0,2,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

COL = {"cyan": "&HF5D05F", "blue": "&HC07A1F"}


def ts(t):
    return f"{int(max(t,0)//3600)}:{int(max(t,0)%3600//60):02d}:{max(t,0)%60:05.2f}"


def ass_for(shot, dur):
    L = [HEAD]
    for (t0, t1, style, text, col, x, y) in shot["lines"]:
        t1 = min(t1, dur)
        if style == "TagD":
            body = (f"{{\\fad(220,200)\\bord18\\3c&HF5D05F&\\1c&H2F2416&"
                    f"\\move({x},{y},{x},{y-26},0,300)}}{text}")
        else:
            c = f"\\c{COL[col]}&" if col else ""
            body = f"{{\\fad(200,150){c}\\move({x},{y},{x},{y-24},0,300)}}{text}"
        L.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},{style},,0,0,0,,{body}")
    p = os.path.join(WORK, f"a_{int(shot['tl'][0]*10)}.ass")
    open(p, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    return p


def run(cmd, tag):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=WORK)
    if r.returncode != 0:
        print(f"[{tag}] 失败\n", r.stderr[-1500:]); sys.exit(1)


def render_shot(i, shot, assets, mask, grad):
    dur = shot["tl"][1] - shot["tl"][0]
    ss = shot["src"][0]
    ass = ass_for(shot, dur)
    out = os.path.join(WORK, f"s{i}.mp4")
    k = shot["kind"]
    if k == "card4":
        cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", "60",
               "-i", assets["card4"],
               "-vf", f"ass={os.path.basename(ass)},format=yuv420p",
               "-t", f"{dur:.3f}", "-r", "60",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-profile:v", "high", "-level", "4.1", out]
    elif k == "pip":
        fc = (f"[1:v]crop=540:609:0:200,scale=620:700:flags=lanczos,format=rgba[person];"
              f"[2:v]format=rgba[mk];[person][mk]alphamerge[p2];"
              f"[0:v][p2]overlay=400:640[base];"
              f"[base]ass={os.path.basename(ass)},format=yuv420p[vout]")
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-loop", "1", "-framerate", "60", "-i", assets[f"pip{int(shot['tl'][0])}"],
               "-ss", f"{ss}", "-t", f"{dur:.3f}", "-i", SRC,
               "-loop", "1", "-framerate", "60", "-i", mask,
               "-filter_complex", fc, "-map", "[vout]", "-an", "-t", f"{dur:.3f}",
               "-r", "60", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-profile:v", "high", "-level", "4.1", out]
    elif k == "big":
        fc = (f"[0:v]scale={W}:{H},format=rgba[b];[b][1:v]overlay=0:0[g];"
              f"[2:v]format=rgba,fade=t=in:st=2.80:d=0.22:alpha=1[pl];"
              f"[g][pl]overlay=0:0:enable='gte(t,2.80)'[q];"
              f"[q]ass={os.path.basename(ass)},format=yuv420p[vout]")
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-ss", f"{ss}", "-t", f"{dur:.3f}", "-i", SRC,
               "-loop", "1", "-framerate", "60", "-i", grad,
               "-loop", "1", "-framerate", "60", "-i", assets["pill"],
               "-filter_complex", fc, "-map", "[vout]", "-an", "-t", f"{dur:.3f}",
               "-r", "60", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-profile:v", "high", "-level", "4.1", out]
    else:
        fc = (f"[0:v]scale={W}:{H},format=rgba[b];[b][1:v]overlay=0:0[g];"
              f"[g]ass={os.path.basename(ass)},format=yuv420p[vout]")
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-ss", f"{ss}", "-t", f"{dur:.3f}", "-i", SRC,
               "-loop", "1", "-framerate", "60", "-i", grad,
               "-filter_complex", fc, "-map", "[vout]", "-an", "-t", f"{dur:.3f}",
               "-r", "60", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-profile:v", "high", "-level", "4.1", out]
    run(cmd, f"镜头{i+1}")
    return out


def build_audio():
    n = len(SHOTS)
    parts = [f"[0:a]atrim=start={s['src'][0]}:end={s['src'][1]},asetpts=PTS-STARTPTS[x{i}]"
             for i, s in enumerate(SHOTS)]
    parts.append("".join(f"[x{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[ac]")
    parts.append("[ac]afftdn=nf=-28,loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000,"
                 "alimiter=limit=0.95[aout]")
    out = os.path.join(WORK, "audio.m4a")
    run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-filter_complex", ";".join(parts),
         "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ac", "2", out], "音频")
    return out


def main():
    assets = {
        "card4": make_card4(),
        "pip3": make_pip_bg("02", "这三年", "00:09"),
        "pip14": make_pip_bg("05", "这三年", "00:26"),
        "pill": make_pill(),
    }
    mask = make_mask(620, 700)
    grad = make_grad()
    clips = []
    for i, s in enumerate(SHOTS):
        clips.append(render_shot(i, s, assets, mask, grad))
        print(f"  镜头{i+1} {s['kind']:6s} {s['tl'][1]-s['tl'][0]:.2f}s ok")
    lst = os.path.join(WORK, "list.txt")
    open(lst, "w", encoding="utf-8").write(
        "".join(f"file '{c.replace(chr(92),'/')}'\n" for c in clips))
    vid = os.path.join(WORK, "video.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "60", vid], "拼接")
    aud = build_audio()
    dst = os.path.join(OUTDIR, "口播_混合版式v2_40岁最怕啥_21s.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", aud, "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
         "-movflags", "+faststart", dst], "合流")
    print("总时长", round(TOTAL, 2), "s\nOK ->", dst)


if __name__ == "__main__":
    main()
