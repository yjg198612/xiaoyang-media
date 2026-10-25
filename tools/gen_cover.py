# -*- coding: utf-8 -*-
"""小杨 · 中年自救日记 第1天 素材生成器（本地渲染，不消耗生成积分）
输出：封面 1080x1920、钩子大字透明图 1080x1920
配色：深蓝灰 #16242F 渐变 + 冷青蓝 #4FC3F1（用户指定冷调，禁暖棕）
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1920
BG_TOP = (22, 36, 47)      # #16242F
BG_BOT = (11, 19, 27)
CYAN = (79, 195, 241)      # #4FC3F1
WHITE = (240, 247, 252)
GRAY = (138, 158, 178)
DIM = (96, 122, 145)

F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
F_REG = "C:/Windows/Fonts/msyh.ttc"
F_LIGHT = "C:/Windows/Fonts/msyhl.ttc"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAY_DIR = os.path.join(ROOT, "content", "2026-10-26")
os.makedirs(DAY_DIR, exist_ok=True)


def font(path, size):
    return ImageFont.truetype(path, size)


def build_bg():
    """冷调竖向渐变 + 冷青柔光 + 暗角"""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        e = (y / (H - 1)) ** 0.85
        d.line([(0, y), (W, y)], fill=(
            int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * e),
            int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * e),
            int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * e),
        ))

    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-300, -380, 960, 760], fill=(19, 56, 76))
    glow = glow.filter(ImageFilter.GaussianBlur(230))
    img = ImageChops.screen(img, glow)

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse(
        [-int(W * .45), -int(H * .25), int(W * 1.45), int(H * 1.25)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(300))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, Image.blend(img, dark, 0.52), mask)


def segments(d, baseline_y, segs, gap=6, stroke=None):
    """[(text, font, color)] 基线对齐 + 整体居中"""
    widths = [d.textlength(t, font=f) for t, f, _ in segs]
    x = (W - (sum(widths) + gap * (len(segs) - 1))) / 2
    for (t, f, c), w in zip(segs, widths):
        kw = {}
        if stroke:
            kw = dict(stroke_width=stroke[0], stroke_fill=stroke[1])
        d.text((x, baseline_y), t, font=f, fill=c, anchor="ls", **kw)
        x += w + gap


def tracked(d, baseline_y, text, f, fill, tracking=8):
    widths = [d.textlength(ch, font=f) for ch in text]
    x = (W - (sum(widths) + tracking * (len(text) - 1))) / 2
    for ch, w in zip(text, widths):
        d.text((x, baseline_y), ch, font=f, fill=fill, anchor="ls")
        x += w + tracking


def make_cover():
    img = build_bg()
    d = ImageDraw.Draw(img)

    tracked(d, 215, "中年自救日记", font(F_BOLD, 40), GRAY, tracking=9)
    tracked(d, 275, "第 1 天", font(F_LIGHT, 34), CYAN, tracking=12)
    d.line([(W / 2 - 40, 315), (W / 2 + 40, 315)], fill=CYAN, width=3)

    segments(d, 700, [
        ("不到 ", font(F_BOLD, 116), WHITE),
        ("100", font(F_BOLD, 172), CYAN),
        (" 块", font(F_BOLD, 116), WHITE),
    ], gap=4)

    segments(d, 886, [
        ("要撑 ", font(F_BOLD, 116), WHITE),
        ("7", font(F_BOLD, 172), CYAN),
        (" 天", font(F_BOLD, 116), WHITE),
    ], gap=4)

    d.line([(W / 2 - 120, 978), (W / 2 + 120, 978)], fill=(52, 74, 92), width=2)
    tracked(d, 1060, "40岁 · 失业 · 负债 · 退回县城", font(F_REG, 40), GRAY, tracking=2)

    segments(d, 1400, [
        ("唯一的动作：", font(F_LIGHT, 38), DIM),
        ("每天下楼转一圈", font(F_REG, 38), (126, 154, 176)),
    ], gap=0)

    path = os.path.join(DAY_DIR, "cover_第1天_1080x1920.png")
    img.save(path)
    return path


def make_hook():
    """透明底钩子大字，供前3秒压字"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    l1 = [("不到 ", font(F_BOLD, 126), WHITE), ("100", font(F_BOLD, 184), CYAN),
          (" 块", font(F_BOLD, 126), WHITE)]
    l2 = [("撑 ", font(F_BOLD, 126), WHITE), ("7", font(F_BOLD, 184), CYAN),
          (" 天", font(F_BOLD, 126), WHITE)]
    segments(d, 830, l1, gap=4, stroke=(3, (8, 15, 22, 210)))
    segments(d, 1070, l2, gap=4, stroke=(3, (8, 15, 22, 210)))

    shadow = layer.split()[3].point(lambda v: int(v * 0.55))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(shadow)
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    out = Image.alpha_composite(sh, layer)

    path = os.path.join(DAY_DIR, "hook_大字_透明_1080x1920.png")
    out.save(path)
    return path


if __name__ == "__main__":
    print("封面:", make_cover())
    print("大字:", make_hook())
