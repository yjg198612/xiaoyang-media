# -*- coding: utf-8 -*-
"""口播引擎 v4 —— 气口对齐 + 真人窗口逐场变化
1) 切点全部落在 silencedetect 测出的静音中点附近，保住每个自然呼吸
2) 每场窗口尺寸/位置都不同（880/740/700/900/720 宽，y 690~800）
3) 每场独立渲染再拼接，60fps
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = r"C:\Users\yjg198612\Documents\xwechat_files\wxid_84aqoy41tsam42_7626\msg\video\2026-10\10abd88415b7dc91da19e70d9bcf8436.mp4"
WORK = os.path.join(ROOT, "work", "v4")
OUTDIR = os.path.join(ROOT, "content", "2026-10-27")
os.makedirs(WORK, exist_ok=True)

W, H = 1080, 1920
WHITE, CYAN, DARK, GRAY, DIMC = "&HFCF7F0", "&HF5D05F", "&H2F2416", "&HB29E8A", "&H8A7A66"

# 切点均已落在静音区间内（silencedetect 实测）
SCENES = [
    dict(ss=6.30, se=9.30, win=(880, 990, 100, 690), cy=50,           # 大窗居中
         els=[(0.10, 1.90, 8, 540, 400, 112, [("40多岁", CYAN), ("的男人", WHITE)]),
              (2.30, 3.00, 8, 540, 580, 112, [("最怕", WHITE), ("啥", CYAN)])]),
    dict(ss=10.70, se=15.90, win=(740, 840, 170, 760), cy=40,         # 中窗偏左
         els=[(0.10, 2.00, 7, 90, 300, 92, [("我最怕的，是", WHITE)]),
              (1.95, 4.20, 7, 90, 448, 104, [("明明", WHITE), ("撑不住", CYAN), ("了", WHITE)]),
              (4.10, 5.20, 7, 90, 596, 96, [("回家还得装", WHITE)])]),
    dict(ss=17.20, se=23.75, win=(700, 790, 190, 800), cy=30,         # 小窗更靠下
         els=[(0.10, 3.40, 7, 100, 300, 92, [("退掉县城的房子", WHITE)]),
              (3.50, 5.10, 7, 100, 448, 96, [("回市里", CYAN)]),
              (5.20, 6.55, 7, 100, 596, 92, [("跟老婆孩子住", WHITE)])]),
    dict(ss=25.60, se=28.00, win=(900, 1010, 90, 680), cy=45,         # 最大窗
         els=[(0.10, 1.30, 8, 540, 370, 112, [("这三年", WHITE)]),
              (1.15, 2.40, 8, 540, 540, 118, [("啥也没干成", CYAN)])]),
    dict(ss=29.90, se=34.20, win=(720, 810, 180, 780), cy=60,         # 小窗留标签位
         els=[(0.10, 2.15, 8, 540, 350, 108, [("下一步", WHITE)]),
              (2.20, 4.30, 8, 540, 500, 108, [("不知道该", WHITE), ("咋办", CYAN)]),
              (2.85, 4.30, 8, 540, 646, 54, [("你们有什么建议？", None)])]),
]

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Microsoft YaHei,32,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,9,0,1,0,0,7,120,60,60,1
Style: Code,Microsoft YaHei,30,%s,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,9,60,120,56,1
Style: CEN,Microsoft YaHei,110,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,8,60,60,0,1
Style: LFT,Microsoft YaHei,96,%s,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,0,0,7,60,60,0,1
Style: Tag,Microsoft YaHei,54,%s,&H000000FF,&H00F5D05F,&H00000000,-1,0,0,0,100,100,2,0,3,22,0,8,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (GRAY, DIMC, WHITE, WHITE, DARK)


def ts(t):
    t = max(t, 0.0)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"


def segs_txt(parts):
    out = ""
    for txt, col in parts:
        out += (f"{{\\c{col}&}}{txt}" if col else txt)
    return out + (f"{{\\c{WHITE}&}}" if any(c for _, c in parts) else "")


def build_bg(idx, win):
    ww, wh, wx, wy = win
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
        [wx - 18, wy - 8, wx + ww + 18, wy + wh + 30], radius=34, fill=150)
    img = Image.composite(Image.new("RGB", (W, H), (4, 7, 10)), img,
                          sh.filter(ImageFilter.GaussianBlur(28)))
    ImageDraw.Draw(img).line([(120, 96), (176, 96)], fill=(95, 208, 245), width=4)
    p = os.path.join(WORK, f"bg{idx}.png"); img.save(p); return p


def build_mask(idx, win):
    ww, wh, _, _ = win
    m = Image.new("L", (ww, wh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ww - 1, wh - 1], radius=26, fill=255)
    rgba = Image.new("RGBA", (ww, wh), (255, 255, 255, 0))
    rgba.putalpha(m)
    p = os.path.join(WORK, f"mk{idx}.png"); rgba.save(p); return p


def frame_rects(d):
    rects = []
    acc = 0.0
    for s in d:
        dur = s["se"] - s["ss"]
        rects.append((acc, acc + dur))
        acc += dur
    return rects, acc


def build_ass(idx, sc, off):
    dur = sc["se"] - sc["ss"]
    L = [HEAD]
    L.append(f"Dialogue: 0,{ts(0)},{ts(dur)},Label,,0,0,0,,中年自救日记")
    t = int(off) + 1
    while t < off + dur:
        L.append(f"Dialogue: 0,{ts(t-off)},{ts(min(t-off+1, dur))},Code,,0,0,0,,"
                 f"00:{t:02d}")
        t += 1
    for (a, b, al, x, y, size, parts) in sc["els"]:
        b = min(b, dur)
        style = "CEN" if al == 8 else "LFT"
        if size == 54:
            body = parts[0][0]
            txt = (f"{{\\fad(200,140)\\move(540,{y},{540},{y-26},0,300)}}" + body)
            L.append(f"Dialogue: 1,{ts(a)},{ts(b)},Tag,,0,0,0,,{txt}")
        else:
            txt = (f"{{\\fad(200,140)\\fs{size}\\move({x},{y},{x},{y-24},0,300)}}"
                   + segs_txt(parts))
            L.append(f"Dialogue: 1,{ts(a)},{ts(b)},{style},,0,0,0,,{txt}")
    p = os.path.join(WORK, f"sc{idx}.ass")
    open(p, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")
    return p


def render_scene(idx, sc, off, rects):
    ww, wh, wx, wy = sc["win"]
    dur = sc["se"] - sc["ss"]
    bg, mk, ass = build_bg(idx, sc["win"]), build_mask(idx, sc["win"]), build_ass(idx, sc, off)
    ch = round(540 * wh / ww)
    fc = (f"[1:v]crop=540:{ch}:0:{sc['cy']},scale={ww}:{wh}:flags=lanczos,format=rgba[person];"
          f"[2:v]format=rgba,scale={ww}:{wh}[mk];"
          f"[person][mk]alphamerge[p2];"
          f"[0:v][p2]overlay={wx}:'{wy}+40*max(0,1-t/0.45)'[base];"
          f"[base]ass={os.path.basename(ass)},format=yuv420p[vout]")
    dst = os.path.join(WORK, f"c{idx}.mp4")
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", "60", "-i", bg,
           "-ss", f"{sc['ss']}", "-t", f"{dur:.3f}", "-i", SRC,
           "-loop", "1", "-framerate", "60", "-i", mk,
           "-filter_complex", fc, "-map", "[vout]", "-an",
           "-t", f"{dur:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-profile:v", "high", "-level", "4.1", "-r", "60", "-g", "120",
           "-pix_fmt", "yuv420p", dst]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WORK)
    if r.returncode != 0:
        print(f"[场景{idx}] 失败\n", r.stderr[-1500:]); sys.exit(1)
    return dst


def build_audio():
    n = len(SCENES)
    parts = [f"[0:a]atrim=start={s['ss']}:end={s['se']},asetpts=PTS-STARTPTS[a{i}]"
             for i, s in enumerate(SCENES)]
    parts.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[ac]")
    parts.append("[ac]afftdn=nf=-28,loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000,"
                 "alimiter=limit=0.95[aout]")
    out = os.path.join(WORK, "audio.m4a")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", SRC,
           "-filter_complex", ";".join(parts), "-map", "[aout]",
           "-c:a", "aac", "-b:a", "192k", "-ac", "2", out]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=WORK)
    if r.returncode != 0:
        print("音频失败\n", r.stderr[-1200:]); sys.exit(1)
    return out


def main():
    rects, total = frame_rects(SCENES)
    clips = []
    for i, sc in enumerate(SCENES):
        clips.append(render_scene(i, sc, rects[i][0], rects))
        print(f"  场景{i+1} ok  {sc['se']-sc['ss']:.2f}s  win={sc['win'][0]}x{sc['win'][1]}")
    lst = os.path.join(WORK, "list.txt")
    open(lst, "w", encoding="utf-8").write(
        "".join(f"file '{c.replace(chr(92), '/')}'\n" for c in clips))
    vid = os.path.join(WORK, "video.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-r", "60", vid],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("拼接失败\n", r.stderr[-1200:]); sys.exit(1)
    aud = build_audio()
    dst = os.path.join(OUTDIR, "口播_场景版v2_40岁最怕啥_21s.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", aud,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", dst],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("合流失败\n", r.stderr[-1200:]); sys.exit(1)
    print(f"总时长 {total:.2f}s\nOK -> {dst}")


if __name__ == "__main__":
    main()
