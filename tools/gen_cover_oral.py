# -*- coding: utf-8 -*-
"""为「县城招人的就两家」这条口播配封面（冷调，本地渲染零积分）"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1920
BG_TOP, BG_BOT = (22, 36, 47), (11, 19, 27)
CYAN, WHITE = (95, 208, 245), (240, 247, 252)
GRAY, DIM = (138, 158, 178), (96, 122, 145)
F_BOLD, F_REG, F_LIGHT = ("C:/Windows/Fonts/msyhbd.ttc",
                          "C:/Windows/Fonts/msyh.ttc",
                          "C:/Windows/Fonts/msyhl.ttc")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "2026-10-25")
os.makedirs(OUT, exist_ok=True)


def f(p, s):
    return ImageFont.truetype(p, s)


def bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        e = (y / (H - 1)) ** 0.85
        d.line([(0, y), (W, y)], fill=tuple(
            int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * e) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-300, -380, 960, 760], fill=(19, 56, 76))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(230)))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([-int(W * .45), -int(H * .25),
                               int(W * 1.45), int(H * 1.25)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(300))
    return Image.composite(img, Image.blend(img, Image.new("RGB", (W, H)), .52), m)


def seg(d, base, items, gap=4):
    ws = [d.textlength(t, font=ft) for t, ft, _ in items]
    x = (W - (sum(ws) + gap * (len(items) - 1))) / 2
    for (t, ft, c), w in zip(items, ws):
        d.text((x, base), t, font=ft, fill=c, anchor="ls")
        x += w + gap


def tracked(d, base, text, ft, fill, tr=8):
    ws = [d.textlength(ch, font=ft) for ch in text]
    x = (W - (sum(ws) + tr * (len(text) - 1))) / 2
    for ch, w in zip(text, ws):
        d.text((x, base), ch, font=ft, fill=fill, anchor="ls")
        x += w + tr


def main():
    img = bg()
    d = ImageDraw.Draw(img)
    tracked(d, 215, "中年自救日记", f(F_BOLD, 40), GRAY, 9)
    tracked(d, 275, "县城 · 白天", f(F_LIGHT, 34), CYAN, 12)
    d.line([(W / 2 - 40, 315), (W / 2 + 40, 315)], fill=CYAN, width=3)

    seg(d, 700, [("招人的", f(F_BOLD, 112), WHITE),
                 ("就两家", f(F_BOLD, 112), WHITE)])
    seg(d, 850, [("都要 ", f(F_BOLD, 112), WHITE),
                 ("35", f(F_BOLD, 150), CYAN),
                 (" 岁以下", f(F_BOLD, 112), WHITE)])

    d.line([(W / 2 - 120, 960), (W / 2 + 120, 960)], fill=(52, 74, 92), width=2)
    tracked(d, 1040, "40岁 · 失业3年 · 县城", f(F_REG, 40), GRAY, 2)

    seg(d, 1150, [("一家 2800，", f(F_BOLD, 46), CYAN),
                  ("我连被挑的资格都没有", f(F_REG, 46), (126, 154, 176))])

    p = os.path.join(OUT, "cover_招人就两家_1080x1920.png")
    img.save(p)
    print(p)


if __name__ == "__main__":
    main()
