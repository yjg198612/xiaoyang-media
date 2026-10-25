# -*- coding: utf-8 -*-
"""阶段2：生成 AS S字幕（重断句 + 关键词高亮）+ 钩子卡，并烧录成片"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "out")
SRC_V1 = os.path.join(OUT, "v1_nosub.mp4")
ASS = os.path.join(OUT, "sub.ass")
FINAL = os.path.join(ROOT, "content", "2026-10-25", "口播_县城招人的就两家_19s.mp4")
os.makedirs(os.path.dirname(FINAL), exist_ok=True)

WHITE = r"&H00FCF7F0"
CYAN = r"&H00F1C34F"
CYAN_TAG = r"{\c&HF5D05F&}"      # ASS 内联色：BGR 顺序
WHITE_TAG = r"{\c&HFCF7F0&}"


def ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# (起, 止, 主句, 高亮词或 None)
SUBS = [
    (1.30, 2.45, "我在一个没有网约车的县城", None),
    (2.46, 4.40, "失业快3年", "3年"),
    (4.40, 6.55, "今天在街上转了一上午", None),
    (6.55, 7.85, "招人的就两家", "两家"),
    (8.06, 9.95, "一家写着35岁以下", "35岁以下"),
    (10.16, 12.55, "一家工资只有2800", "2800"),
    (12.55, 14.15, "我今年40岁了", "40岁"),
    (14.36, 16.00, "连被挑的资格都没有", "被挑"),
    (16.21, 18.10, "你们那还有活干吗", None),
]

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Microsoft YaHei,78,%s,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.2,1.8,2,50,50,400,1
Style: Hook,Microsoft YaHei,88,%s,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,3,0,1,5.0,2.2,2,40,40,350,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (WHITE, WHITE)


def build_ass():
    lines = [HEAD]
    # 钩子卡：0 - 1.55 秒，结论前置
    lines.append(
        f"Dialogue: 1,{ts(0.0)},{ts(1.30)},Hook,,0,0,0,,"
        + "招人的就" + CYAN_TAG + "两家" + WHITE_TAG
        + r"\N都要" + CYAN_TAG + "35岁以下"
    )
    for a, b, text, hl in SUBS:
        if hl and hl in text:
            pre, post = text.split(hl, 1)
            body = pre + CYAN_TAG + hl + WHITE_TAG + post
        else:
            body = text
        lines.append(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{body}")
    open(ASS, "w", encoding="utf-8-sig").write("\n".join(lines) + "\n")


def burn():
    # drawbox 盖掉原片烧死的旧字幕（该区域本身就是深色衣物，纯黑块几乎不可见）
    # 渐变遮罩压暗底部（无硬边），同时彻底盖掉原片烧死的旧字幕
    vf = "[0:v][1:v]overlay=0:0,ass=sub.ass"
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", SRC_V1,
        "-i", os.path.join(OUT, "bottom_mask.png"),
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        FINAL,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=OUT)
    if r.returncode != 0:
        print("ERR:\n", r.stderr[-2500:])
        sys.exit(1)
    print("OK ->", FINAL)


if __name__ == "__main__":
    build_ass()
    burn()
