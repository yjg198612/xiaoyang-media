# -*- coding: utf-8 -*-
"""小杨口播视频后期 · 阶段1：重构图 + 节奏压缩 + 音质归一（不含字幕）
源：桌面 b15194ad164a10e673bb588a7f314229.mp4（720x1280 HEVC 22.08s）
"""
import subprocess, os, sys

SRC = r"C:\Users\yjg198612\Desktop\b15194ad164a10e673bb588a7f314229.mp4"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "out")
os.makedirs(OUT, exist_ok=True)
V1 = os.path.join(OUT, "v1_nosub.mp4")

# 保留语义段，尾部吃掉原停顿的一部分，实现"压缩停顿但不切碎"
SEGS = [
    (0.00, 2.36),
    (3.04, 8.64),
    (9.38, 11.48),
    (12.12, 16.32),
    (16.85, 18.70),
    (19.58, 21.90),
]

W, H = 1080, 1920
# 原片顶部约 140px 为车内黑顶 + 右上过曝化妆镜灯，全部裁掉；左右各收 40px 做数字变焦
CROP = "crop=600:1067:60:205"


def build():
    n = len(SEGS)
    parts = []
    for i, (s, e) in enumerate(SEGS):
        parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]")
    vs = "".join(f"[v{i}]" for i in range(n))
    as_ = "".join(f"[a{i}]" for i in range(n))
    parts.append(f"{vs}concat=n={n}:v=1:a=0[vc]")
    parts.append(f"{as_}concat=n={n}:v=0:a=1[ac]")

    # 构图：裁切 → 放大到 1080x1920 → 轻微锐化补偿放大损失 → 提对比、压高光
    parts.append(
        f"[vc]{CROP},scale={W}:{H}:flags=lanczos,"
        f"unsharp=5:5:0.7:5:5:0.0,"
        # 冷调白平衡：压红黄、提蓝，抵消车内暖光（用户明确要求冷调、低饱和）
        f"colorbalance=rs=-0.055:gs=-0.005:bs=0.062:rm=-0.030:gm=0.0:bm=0.036:rh=-0.016:gh=0.0:bh=0.030,"
        f"eq=contrast=1.05:brightness=0.006:saturation=0.96,"
        f"format=yuv420p[vout]"
    )
    # 音频：轻度降噪 → EBU R128 归一化到 -14 LUFS（抖音/快手推荐）→ 限峰
    parts.append(
        "[ac]afftdn=nf=-28,"
        "loudnorm=I=-14:TP=-1.0:LRA=9,"
        "aresample=48000,"
        "alimiter=limit=0.95[aout]"
    )

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", SRC,
        "-filter_complex", ";".join(parts),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-profile:v", "high", "-level", "4.1",
        "-r", "30", "-g", "60",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        "-movflags", "+faststart",
        V1,
    ]
    print(" ".join(cmd)[:300], "...")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-3000:])
        sys.exit(1)
    print("OK ->", V1)


if __name__ == "__main__":
    build()
