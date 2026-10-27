# -*- coding: utf-8 -*-
"""混合版式分镜样张：圆形头像卡 / 中窗口画中画 / 全屏 / 圆卡 / 全屏
按用户要求交替出现，不再单一模式。
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work", "mock")
W, H = 1080, 1920
FB, FR = "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"

BG = (233, 238, 242)
INK = (22, 36, 47)
ACC = (31, 127, 208)
CARD = (22, 36, 47)
CARDTX = (240, 247, 252)
MUTED = (107, 130, 150)
WHITE = (240, 247, 252)
CYAN = (95, 208, 245)

# 头部实测：发顶 y225 下巴 y640 左 x75 右 x390 → 以 (235,432) 为中心裁 465 方形
FACE_BOX = (22, 214, 452, 644)


def f(p, s):
    return ImageFont.truetype(p, s)


def frame(t):
    return Image.open(os.path.join(WORK, f"fr_{t}.png")).convert("RGB")


def light_base():
    img = Image.new("RGB", (W, H), BG)
    n = Image.effect_noise((W, H), 7).convert("L")
    mask = n.point(lambda v: 255 if v > 138 else 0)
    img = Image.composite(img.point(lambda v: min(255, v + 5)), img, mask)
    return img


def circle_avatar(size=190):
    sq = frame(20).crop(FACE_BOX).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(sq, (0, 0), m)
    ImageDraw.Draw(out).ellipse([1, 1, size - 2, size - 2],
                                outline=(255, 255, 255, 235), width=3)
    return out


def paste_circle(img, cx, cy, size=190):
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse([cx - size // 2, cy - size // 2 + 6,
                                cx + size // 2, cy + size // 2 + 14], fill=90)
    img.paste(Image.new("RGB", (W, H), (60, 70, 80)), (0, 0),
              sh.filter(ImageFilter.GaussianBlur(14)))
    av = circle_avatar(size)
    img.paste(av, (cx - size // 2, cy - size // 2), av)


def header(d, idx, name, code, dark=False):
    c = (150, 168, 184) if dark else MUTED
    d.text((72, 150), f"{idx} · {name}", font=f(FR, 34), fill=c, anchor="ls")
    d.text((1008, 150), code, font=f(FR, 34), fill=c, anchor="rs")
    d.line([(72, 186), (1008, 186)], fill=c, width=1)


def note(d, text, dark=False):
    d.text((W // 2, 1750), text, font=f(FR, 26),
           fill=(150, 168, 184) if dark else MUTED, anchor="ms")


def full_bleed(t, dim=0.55):
    img = frame(t).resize((W, H), Image.LANCZOS)
    g = Image.new("L", (W, H), 0)
    px = g.load()
    for y in range(H):
        if y > 1180:
            px_y = int(255 * min(1, (y - 1180) / 260))
            for x in range(W):
                px[x, y] = int(px_y * dim)
        elif y < 260:
            px_y = int(255 * min(1, (260 - y) / 260))
            for x in range(W):
                px[x, y] = int(px_y * dim * 0.85)
    img.paste(Image.new("RGB", (W, H), (6, 10, 14)), (0, 0), g)
    return img


def s1():
    img = light_base(); d = ImageDraw.Draw(img)
    header(d, "01", "撑不住了", "00:04")
    paste_circle(img, 810, 430, 190)
    d.text((90, 820), "撑不住了", font=f(FB, 148), fill=INK, anchor="ls")
    d.text((90, 990), "回家还得装", font=f(FB, 148), fill=ACC, anchor="ls")
    note(d, "真实记录 · 不解释")
    return img, "① 圆头像 + 大字卡"


def s2():
    img = light_base(); d = ImageDraw.Draw(img)
    header(d, "02", "这三年", "00:09")
    d.text((90, 560), "三年，三次决定", font=f(FB, 84), fill=INK, anchor="ls")
    wx, wy, ww, wh = 400, 640, 620, 700
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([wx - 14, wy - 6, wx + ww + 14, wy + wh + 26],
                                         radius=34, fill=120)
    img.paste(Image.new("RGB", (W, H), (70, 82, 94)), (0, 0),
              sh.filter(ImageFilter.GaussianBlur(20)))
    sq = frame(12).crop((0, 300, 540, 909)).resize((ww, wh), Image.LANCZOS)
    m = Image.new("L", (ww * 2, wh * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, ww * 2 - 1, wh * 2 - 1], radius=52, fill=255)
    m = m.resize((ww, wh), Image.LANCZOS)
    ov = Image.new("RGBA", (ww, wh), (0, 0, 0, 0))
    ov.paste(sq, (0, 0), m)
    img.paste(ov, (wx, wy), ov)
    d.text((90, 1460), "退房  →  回市里  →  陪家人", font=f(FR, 46), fill=ACC, anchor="ls")
    note(d, "没有回头路")
    return img, "② 中窗口画中画"


def s3():
    img = full_bleed(26); d = ImageDraw.Draw(img)
    header(d, "03", "回家还得装", "00:16", dark=True)
    d.text((90, 1520), "回家还得装", font=f(FB, 96), fill=WHITE, anchor="ls")
    note(d, "", dark=True)
    return img, "③ 全屏真人"


def s4():
    img = light_base(); d = ImageDraw.Draw(img)
    header(d, "04", "这三年", "00:21")
    paste_circle(img, 810, 430, 190)
    d.text((90, 620), "县城这三年", font=f(FB, 104), fill=INK, anchor="ls")
    cards = [("01", "退房"), ("02", "回市里"), ("03", "陪家人")]
    x, y, cw, ch, gap = 90, 720, 296, 280, 26
    for i, (no, t) in enumerate(cards):
        hl = i == 2
        bg = ACC if hl else CARD
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=6, fill=bg)
        d.text((x + 24, y + 44), no, font=f(FR, 32), fill=CARDTX, anchor="ls")
        d.line([(x + 24, y + 92), (x + cw - 24, y + 92)], fill=CARDTX, width=2)
        d.text((x + 24, y + 176), t, font=f(FB, 62), fill=CARDTX, anchor="ls")
        x += cw + gap
    note(d, "3 年 · 3 个决定")
    return img, "④ 圆头像 + 三卡"


def s5():
    img = full_bleed(30); d = ImageDraw.Draw(img)
    header(d, "05", "下一步", "00:34", dark=True)
    d.text((540, 1318), "下一步", font=f(FB, 118), fill=WHITE, anchor="ms")
    d.text((540, 1448), "不知道该咋办", font=f(FB, 108), fill=CYAN, anchor="ms")
    tw, th = 448, 86
    d.rounded_rectangle([540 - tw // 2, 1508, 540 + tw // 2, 1508 + th], radius=43, fill=CYAN)
    d.text((540, 1508 + th // 2 + 3), "你们有什么建议？", font=f(FR, 42), fill=INK, anchor="mm")
    return img, "⑤ 全屏 + 大字压屏"


if __name__ == "__main__":
    jobs = [s1, s2, s3, s4, s5]
    outs = []
    for fn in jobs:
        img, label = fn()
        p = os.path.join(WORK, f"sb_{len(outs)+1}.png")
        img.save(p)
        outs.append((label, p))
        print(label, "->", os.path.basename(p))
    tw, th = 310, 551
    sheet = Image.new("RGB", (tw * len(outs) + 20 * (len(outs) + 1), th + 64), (22, 22, 22))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(outs):
        sheet.paste(Image.open(p).resize((tw, th)), (20 + i * (tw + 20), 20))
        d.text((20 + i * (tw + 20), th + 34), label, fill=(220, 220, 220))
    sheet.save(os.path.join(WORK, "storyboard.png"))
    print("storyboard ok")
