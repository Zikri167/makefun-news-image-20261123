"""Deterministic broadsheet news poster, pure stdlib PNG rendering."""
import math
import struct
import zlib

W = 1024
H = 1024

NAVY = (10, 31, 61)
PANEL = (18, 42, 79)
WHITE = (245, 245, 240)
RED = (192, 57, 43)
ORANGE = (217, 78, 31)
GRAY = (160, 168, 178)
LGRAY = (192, 198, 206)
PALE = (221, 230, 238)
TEAL = (0, 59, 74)
BLACK = (12, 12, 12)
BLUE = (52, 120, 198)
GREEN = (46, 180, 90)
BROWN = (140, 92, 46)
TEAL2 = (20, 46, 82)

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

fb = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i] = c[0]
        fb[i + 1] = c[1]
        fb[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def polygon(points, c):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        nodes = []
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if (y1 <= yy < y2) or (y2 <= yy < y1):
                nodes.append(int(x1 + (yy - y1) * (x2 - x1) / (y2 - y1)))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            for xx in range(nodes[i], nodes[i + 1] + 1):
                px(xx, yy, c)


def triangle(a, b, c_pt, col):
    polygon([a, b, c_pt], col)


def line(x1, y1, x2, y2, col, thick=3):
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    r = max(thick // 2, 1)
    for i in range(steps + 1):
        x = int(x1 + (x2 - x1) * i / steps)
        y = int(y1 + (y2 - y1) * i / steps)
        circle(x, y, r, col)


def text_width(s, scale, spacing=2):
    if not s:
        return 0
    return len(s) * (5 * scale + spacing) - spacing


def text(x, y, s, scale, col, spacing=2):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col_i in range(5):
                if glyph[row][col_i] == "1":
                    rect(cx + col_i * scale, y + row * scale, scale, scale, col)
        cx += 5 * scale + spacing
    return cx


def text_center(cx_center, y, s, scale, col, spacing=2):
    w = text_width(s, scale, spacing)
    return text(cx_center - w // 2, y, s, scale, col, spacing)


def star(cx, cy, r, col):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r // 3 + 2
        pts.append((int(cx + rad * math.cos(ang)), int(cy + rad * math.sin(ang))))
    polygon(pts, col)


def border(x, y, w, h, col, t=3):
    rect(x, y, w, t, col)
    rect(x, y + h - t, w, t, col)
    rect(x, y, t, h, col)
    rect(x + w - t, y, t, h, col)


def scene_cop():
    # smoke
    for (cx, cy, r) in ((210, 285, 26), (300, 245, 34), (400, 205, 28), (470, 250, 20)):
        circle(cx, cy, r, (143, 163, 184))
    # conference building
    rect(130, 350, 460, 170, LGRAY)
    triangle((110, 350), (610, 350), (360, 285), (150, 158, 168))
    rect(150, 470, 420, 14, (120, 128, 138))
    for i in range(6):
        rect(165 + i * 68, 380, 34, 80, (70, 92, 120))
    rect(330, 484, 60, 36, (70, 92, 120))
    # horizon
    rect(36, 520, 644, 6, ORANGE)
    rect(36, 528, 644, 3, RED)
    # torn paper banner across building
    pts = [(95, 392), (180, 380), (265, 394), (350, 379), (435, 393),
           (520, 381), (625, 392), (610, 428), (540, 442), (455, 427),
           (370, 443), (285, 428), (200, 442), (120, 427), (82, 410)]
    polygon(pts, WHITE)
    text_center(355, 396, "FOSSIL FUELS", 4, BLACK, spacing=3)
    line(120, 440, 600, 388, RED, thick=7)
    line(120, 388, 600, 440, RED, thick=3)


def scene_hormuz():
    # strait: two white coastline polylines
    line(730, 250, 800, 275, WHITE, thick=4)
    line(800, 275, 850, 255, WHITE, thick=4)
    line(850, 255, 920, 285, WHITE, thick=4)
    line(730, 320, 810, 300, WHITE, thick=4)
    line(810, 300, 880, 325, WHITE, thick=4)
    line(880, 325, 1005, 300, WHITE, thick=4)
    # explosions in Bahrain & Saudi area
    star(790, 225, 26, RED)
    star(790, 225, 14, ORANGE)
    star(950, 235, 30, ORANGE)
    star(950, 235, 16, RED)
    # radar dish crossed out
    circle(975, 345, 24, WHITE)
    circle(975, 345, 15, TEAL)
    line(955, 325, 995, 365, RED, thick=5)
    line(995, 325, 955, 365, RED, thick=5)
    rect(760, 345, 90, 10, PALE)
    rect(795, 320, 10, 30, PALE)


def cell_head(cx, y, lines):
    yy = y
    for ln in lines:
        text_center(cx, yy, ln, 2, WHITE, spacing=1)
        yy += 18


def grid_cells():
    cells = [(716, 446), (872, 446), (716, 638), (872, 638)]
    for (x, y) in cells:
        rect(x, y, 152, 192, TEAL2)
        border(x, y, 152, 192, GRAY, t=2)
    # a) cargo ship with flames
    polygon([(736, 545), (840, 545), (828, 568), (748, 568)], BLACK)
    rect(760, 528, 55, 17, BLACK)
    rect(770, 512, 16, 16, BLACK)
    star(800, 492, 20, ORANGE)
    star(822, 500, 14, RED)
    circle(790, 500, 8, ORANGE)
    cell_head(792, 578, ["RUSSIAN", "SHIP BURNS", "OFF FINLAND"])
    # b) gavel over globe
    circle(948, 520, 34, BLUE)
    line(922, 500, 975, 545, (90, 170, 90), thick=3)
    line(975, 500, 922, 545, (90, 170, 90), thick=3)
    line(885, 478, 935, 512, BROWN, thick=9)
    rect(872, 462, 30, 16, BROWN)
    rect(920, 500, 30, 14, BROWN)
    rect(900, 560, 60, 8, BROWN)
    cell_head(948, 578, ["ICJ RULES", "MYANMAR", "GENOCIDE"])
    # c) factory with red X
    rect(736, 700, 90, 55, LGRAY)
    polygon([(736, 700), (770, 678), (770, 700)], LGRAY)
    polygon([(790, 700), (824, 678), (824, 700)], LGRAY)
    rect(748, 720, 16, 20, (70, 92, 120))
    rect(790, 720, 16, 20, (70, 92, 120))
    line(730, 672, 836, 762, RED, thick=7)
    line(836, 672, 730, 762, RED, thick=7)
    cell_head(792, 770, ["FACTORY", "FIRE", "IN INDONESIA"])
    # d) capitol dome with green plus
    triangle((880, 712), (1010, 712), (945, 668), WHITE)
    circle(945, 700, 16, WHITE)
    rect(876, 712, 138, 10, WHITE)
    rect(884, 722, 122, 34, WHITE)
    for i in range(4):
        rect(894 + i * 28, 726, 10, 26, TEAL2)
    rect(972, 664, 10, 34, GREEN)
    rect(960, 676, 34, 10, GREEN)
    cell_head(948, 770, ["DEMOCRATS", "WIN", "US HOUSE"])


def render():
    rect(0, 0, W, H, NAVY)
    # masthead
    text_center(512, 16, "THE WORLD TODAY", 8, WHITE, spacing=6)
    rect(32, 84, 960, 4, RED)
    text_center(512, 94, "MONDAY 23 NOVEMBER 2026", 3, PALE, spacing=3)
    # main panel
    rect(16, 140, 684, 690, PANEL)
    border(16, 140, 684, 690, GRAY, t=3)
    scene_cop()
    # red kicker bar + drop-shadowed, bolder main headline block
    rect(58, 566, 600, 6, RED)
    text_center(362, 589, "COP31 TALKS", 6, RED, spacing=4)
    text_center(358, 585, "COP31 TALKS", 6, WHITE, spacing=4)
    text_center(362, 644, "COLLAPSE", 6, RED, spacing=4)
    text_center(358, 640, "COLLAPSE", 6, WHITE, spacing=4)
    rect(96, 692, 524, 3, WHITE)
    text_center(358, 712, "NO DEAL ON FOSSIL FUELS", 4, (255, 110, 80), spacing=3)
    rect(120, 770, 476, 4, ORANGE)
    # extra scene detail: warning stars flanking the collapsed talks
    star(84, 610, 16, ORANGE)
    star(632, 610, 16, ORANGE)
    star(84, 668, 12, RED)
    star(632, 668, 12, RED)
    # right top panel
    rect(716, 140, 292, 290, TEAL)
    border(716, 140, 292, 290, GRAY, t=3)
    scene_hormuz()
    text_center(862, 356, "IRAN CLAIMS", 3, WHITE, spacing=2)
    text_center(862, 380, "HORMUZ", 3, ORANGE, spacing=2)
    rect(748, 404, 228, 2, RED)
    text_center(862, 410, "US BASE HIT IN BAHRAIN", 2, PALE, spacing=1)
    # small sub-headline sits in grid gap? keep inside panel bottom via overlap handled below
    grid_cells()
    text_center(862, 436 - 22, "", 1, WHITE)
    # hormuz sub-line drawn over panel seam in white on navy strip
    # (placed just under the teal panel, above grid)
    # dotted world strip
    for gx in range(48, 990, 28):
        for gy in (862, 890, 918):
            if (gx // 28 + gy) % 3 != 0:
                circle(gx, gy, 4, (70, 96, 138))
    # footer
    rect(32, 950, 960, 2, GRAY)
    text_center(512, 968, "23 NOVEMBER 2026 - THE WORLD IN ONE DAY", 3, GRAY, spacing=2)
    return encode_png()


def encode_png():
    raw = bytearray()
    row = W * 3
    for y in range(H):
        raw.append(0)
        raw += fb[y * row:(y + 1) * row]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png
