# -*- coding: utf-8 -*-
"""版式样张：三套版面 × 两套配色（冷调 / 照搬原版），静态单帧确认用"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work", "mock")
os.makedirs(WORK, exist_ok=True)
W, H = 1080, 1920
FB, FR = "C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"

SCHEMES = {
    "cold": dict(bg=(233, 238, 242), ink=(22, 36, 47), accent=(31, 127, 208),
                 card=(22, 36, 47), cardtx=(240, 247, 252), muted=(107, 130, 150)),
    "warm": dict(bg=(239, 237, 232), ink=(26, 26, 26), accent=(22, 119, 255),
                 card=(27, 27, 27), cardtx=(245, 245, 245), muted=(122, 117, 108)),
}


def f(p, s):
    return ImageFont.truetype(p, s)


def base(sc):
    img = Image.new("RGB", (W, H), sc["bg"])
    n = Image.effect_noise((W, H), 7).convert("L")
    img = Image.composite(img, img.point(lambda v: min(255, v + 4)), n.point(lambda v: 255 if v > 140 else 0))
    return img


def avatar(size=180):
    im = Image.open(os.path.join(WORK, "fr_20.png")).convert("RGB")
    box = (100, 118, 500, 518)
    sq = im.crop(box).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(sq, (0, 0), m)
    dr = ImageDraw.Draw(out)
    dr.ellipse([1, 1, size - 2, size - 2], outline=(255, 255, 255, 230), width=3)
    return out


def paste_avatar(img, sc, cx=810, cy=420, size=180):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - size // 2 - 4, cy - size // 2 + 2,
                                cx + size // 2 + 4, cy + size // 2 + 12],
                               fill=(0, 0, 0, 60))
    img.paste(Image.new("RGB", (W, H), sc["ink"]), (0, 0), sh.split()[3].filter(ImageFilter.GaussianBlur(12)))
    av = avatar(size)
    img.paste(av, (cx - size // 2, cy - size // 2), av)


def header(d, sc, idx, name, code):
    d.text((72, 150), f"{idx} · {name}", font=f(FR, 34), fill=sc["muted"], anchor="ls")
    d.text((1008, 150), code, font=f(FR, 34), fill=sc["muted"], anchor="rs")
    d.line([(72, 186), (1008, 186)], fill=sc["muted"] + (60,) if False else sc["muted"], width=1)


def footnote(d, sc, text):
    d.text((W // 2, 1742), text, font=f(FR, 26), fill=sc["muted"], anchor="ms")


def L1(img, sc):
    d = ImageDraw.Draw(img)
    header(d, sc, "01", "撑不住了", "00:12")
    d.text((90, 800), "撑不住了", font=f(FB, 150), fill=sc["ink"], anchor="ls")
    d.text((90, 972), "回家还得装", font=f(FB, 150), fill=sc["accent"], anchor="ls")
    footnote(d, sc, "真实记录 · 不解释")
    paste_avatar(img, sc)


def L2(img, sc):
    d = ImageDraw.Draw(img)
    header(d, sc, "02", "这三年", "00:21")
    d.text((90, 600), "县城这三年", font=f(FB, 108), fill=sc["ink"], anchor="ls")
    cards = [("01", "退房"), ("02", "回市里"), ("03", "陪家人")]
    x, y, cw, ch, gap = 90, 700, 296, 280, 26
    for i, (no, t) in enumerate(cards):
        hl = i == 2
        bg = sc["accent"] if hl else sc["card"]
        tx = sc["cardtx"]
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=6, fill=bg)
        d.text((x + 24, y + 44), no, font=f(FR, 32), fill=tx, anchor="ls")
        d.text((x + 24, y + 176), t, font=f(FB, 62), fill=tx, anchor="ls")
        d.line([(x + 24, y + 92), (x + cw - 24, y + 92)], fill=tx, width=2)
        x += cw + gap
    footnote(d, sc, "3 年 · 3 个决定")
    paste_avatar(img, sc)


def L3(img, sc):
    d = ImageDraw.Draw(img)
    header(d, sc, "03", "下一步", "00:34")
    d.text((90, 700), "下一步", font=f(FB, 150), fill=sc["accent"], anchor="ls")
    tags = ["找活", "学技能", "回市里"]
    x, y, tw, th = 90, 790, 210, 78
    for i, t in enumerate(tags):
        on = i == 1
        d.rounded_rectangle([x, y, x + tw, y + th], radius=6,
                            fill=sc["ink"] if on else None,
                            outline=sc["ink"], width=2)
        d.text((x + tw // 2, y + th // 2 + 4), t, font=f(FR, 40),
               fill=sc["cardtx"] if on else sc["ink"], anchor="mm")
        x += tw + 22
    by = 960
    d.rounded_rectangle([90, by, 990, by + 168], radius=8, fill=sc["accent"])
    d.text((122, by + 52), "我的步骤", font=f(FB, 46), fill=(255, 255, 255), anchor="ls")
    d.text((122, by + 116), "先活下去  →  再找出路", font=f(FR, 34), fill=(232, 242, 252), anchor="ls")
    footnote(d, sc, "没有答案，只有下一步")
    paste_avatar(img, sc)


if __name__ == "__main__":
    layouts = [("大字卡", L1), ("三卡横排", L2), ("标签+蓝条", L3)]
    outs = []
    for key, sc in SCHEMES.items():
        for name, fn in layouts:
            img = base(sc)
            fn(img, sc)
            p = os.path.join(WORK, f"{key}_{name}.png")
            img.save(p)
            outs.append((key, name, p))
            print(p)
    # 拼成 2 行 3 列对照表
    tw, th = 360, 640
    sheet = Image.new("RGB", (tw * 3 + 60, th * 2 + 90), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (key, name, p) in enumerate(outs):
        r, c = (0 if key == "cold" else 1), [n for n, _ in layouts].index(name)
        im = Image.open(p).resize((tw, th))
        sheet.paste(im, (c * (tw + 20) + 10, r * (th + 40) + 30))
    d.text((10, 6), "冷调版（建议）", fill=(230, 230, 230))
    d.text((10, th + 46), "照搬原版（米白+亮蓝）", fill=(180, 180, 180))
    sheet.save(os.path.join(WORK, "sheet.png"))
    print("sheet ok")
