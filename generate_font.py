#!/usr/bin/env python3
"""
Generate a handwriting-style font (OTF and TTF) inspired by the handwritten
note in the reference image. The style is a casual, slightly irregular
print-cursive hybrid with variable baselines and organic strokes.
"""

from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
import math

FONT_NAME = "DeLimaHand"
FAMILY_NAME = "DeLima Hand"
UPM = 1000  # units per em
ASCENT = 800
DESCENT = -200
CAP_HEIGHT = 700
X_HEIGHT = 500
STROKE = 70  # average stroke width for the handwriting

# ---------------------------------------------------------------------------
# Helper: build simple glyph outlines via (move/line/curve/close) commands
# expressed as lists of operations.  Each glyph is defined at design-time as
# a list of *contours*, where each contour is a list of points.
# ---------------------------------------------------------------------------

def _rrect(pen, x, y, w, h, r=40):
    """Draw a rounded rectangle."""
    pen.moveTo((x + r, y))
    pen.lineTo((x + w - r, y))
    pen.qCurveTo((x + w, y), (x + w, y + r))
    pen.lineTo((x + w, y + h - r))
    pen.qCurveTo((x + w, y + h), (x + w - r, y + h))
    pen.lineTo((x + r, y + h))
    pen.qCurveTo((x, y + h), (x, y + h - r))
    pen.lineTo((x, y + r))
    pen.qCurveTo((x, y), (x + r, y))
    pen.closePath()


def _oval(pen, cx, cy, rx, ry, steps=12):
    """Approximate an oval with quadratic curves."""
    import math
    pts = []
    for i in range(steps):
        a = 2 * math.pi * i / steps
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    pen.moveTo(pts[0])
    for i in range(1, len(pts)):
        pen.lineTo(pts[i])
    pen.closePath()


def _thick_line(pen, x1, y1, x2, y2, w=None):
    """Draw a thick line as a thin rectangle."""
    if w is None:
        w = STROKE
    hw = w / 2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return
    nx = -dy / length * hw
    ny = dx / length * hw
    pen.moveTo((x1 + nx, y1 + ny))
    pen.lineTo((x2 + nx, y2 + ny))
    pen.lineTo((x2 - nx, y2 - ny))
    pen.lineTo((x1 - nx, y1 - ny))
    pen.closePath()


def _thick_arc(pen, cx, cy, rx, ry, start_angle, end_angle, w=None, steps=16):
    """Draw a thick arc as two concentric arcs forming a closed band."""
    if w is None:
        w = STROKE
    hw = w / 2
    outer_pts = []
    inner_pts = []
    for i in range(steps + 1):
        t = start_angle + (end_angle - start_angle) * i / steps
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        outer_pts.append((cx + (rx + hw) * cos_t, cy + (ry + hw) * sin_t))
        inner_pts.append((cx + (rx - hw) * cos_t, cy + (ry - hw) * sin_t))
    pen.moveTo(outer_pts[0])
    for p in outer_pts[1:]:
        pen.lineTo(p)
    for p in reversed(inner_pts):
        pen.lineTo(p)
    pen.closePath()


# ---------------------------------------------------------------------------
# Glyph drawing functions – each draws into a T2Pen / TTGlyphPen
# ---------------------------------------------------------------------------

PI = math.pi


def draw_space(pen):
    pass  # empty glyph


def draw_A(pen):
    # Left diagonal
    _thick_line(pen, 60, 0, 280, CAP_HEIGHT)
    # Right diagonal
    _thick_line(pen, 280, CAP_HEIGHT, 500, 0)
    # Crossbar
    _thick_line(pen, 140, 280, 420, 280)


def draw_B(pen):
    # Stem
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    # Top bump
    _thick_arc(pen, 80, 530, 200, 170, -PI/2, PI/2)
    # Bottom bump
    _thick_arc(pen, 80, 220, 220, 220, -PI/2, PI/2)


def draw_C(pen):
    _thick_arc(pen, 280, 350, 230, 350, PI*0.35, PI*1.65)


def draw_D(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_arc(pen, 80, 350, 300, 350, -PI/2, PI/2)


def draw_E(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 80, CAP_HEIGHT, 420, CAP_HEIGHT)
    _thick_line(pen, 80, 350, 350, 350)
    _thick_line(pen, 80, 0, 420, 0)


def draw_F(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 80, CAP_HEIGHT, 420, CAP_HEIGHT)
    _thick_line(pen, 80, 350, 350, 350)


def draw_G(pen):
    _thick_arc(pen, 280, 350, 230, 350, PI*0.3, PI*1.7)
    _thick_line(pen, 430, 350, 430, 60)
    _thick_line(pen, 300, 350, 430, 350)


def draw_H(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 460, 0, 460, CAP_HEIGHT)
    _thick_line(pen, 80, 350, 460, 350)


def draw_I(pen):
    _thick_line(pen, 200, 0, 200, CAP_HEIGHT)
    _thick_line(pen, 120, CAP_HEIGHT, 280, CAP_HEIGHT)
    _thick_line(pen, 120, 0, 280, 0)


def draw_J(pen):
    _thick_line(pen, 320, 150, 320, CAP_HEIGHT)
    _thick_arc(pen, 200, 150, 120, 150, -PI, 0)


def draw_K(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 420, CAP_HEIGHT, 80, 320)
    _thick_line(pen, 180, 380, 450, 0)


def draw_L(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 80, 0, 400, 0)


def draw_M(pen):
    _thick_line(pen, 60, 0, 60, CAP_HEIGHT)
    _thick_line(pen, 60, CAP_HEIGHT, 280, 250)
    _thick_line(pen, 280, 250, 500, CAP_HEIGHT)
    _thick_line(pen, 500, CAP_HEIGHT, 500, 0)


def draw_N(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 80, CAP_HEIGHT, 460, 0)
    _thick_line(pen, 460, 0, 460, CAP_HEIGHT)


def draw_O(pen):
    _thick_arc(pen, 280, 350, 230, 350, 0, 2*PI)


def draw_P(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_arc(pen, 80, 530, 220, 170, -PI/2, PI/2)


def draw_Q(pen):
    _thick_arc(pen, 280, 350, 230, 350, 0, 2*PI)
    _thick_line(pen, 350, 150, 500, -30)


def draw_R(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_arc(pen, 80, 530, 220, 170, -PI/2, PI/2)
    _thick_line(pen, 240, 360, 460, 0)


def draw_S(pen):
    _thick_arc(pen, 260, 530, 190, 170, PI*0.15, PI)
    _thick_arc(pen, 260, 220, 210, 200, -PI*0.85, PI*0.15)


def draw_T(pen):
    _thick_line(pen, 40, CAP_HEIGHT, 480, CAP_HEIGHT)
    _thick_line(pen, 260, 0, 260, CAP_HEIGHT)


def draw_U(pen):
    _thick_line(pen, 80, 200, 80, CAP_HEIGHT)
    _thick_line(pen, 460, 200, 460, CAP_HEIGHT)
    _thick_arc(pen, 270, 200, 190, 200, -PI, 0)


def draw_V(pen):
    _thick_line(pen, 60, CAP_HEIGHT, 270, 0)
    _thick_line(pen, 270, 0, 480, CAP_HEIGHT)


def draw_W(pen):
    _thick_line(pen, 40, CAP_HEIGHT, 160, 0)
    _thick_line(pen, 160, 0, 280, 400)
    _thick_line(pen, 280, 400, 400, 0)
    _thick_line(pen, 400, 0, 520, CAP_HEIGHT)


def draw_X(pen):
    _thick_line(pen, 60, 0, 480, CAP_HEIGHT)
    _thick_line(pen, 60, CAP_HEIGHT, 480, 0)


def draw_Y(pen):
    _thick_line(pen, 60, CAP_HEIGHT, 260, 340)
    _thick_line(pen, 460, CAP_HEIGHT, 260, 340)
    _thick_line(pen, 260, 0, 260, 340)


def draw_Z(pen):
    _thick_line(pen, 60, CAP_HEIGHT, 460, CAP_HEIGHT)
    _thick_line(pen, 460, CAP_HEIGHT, 60, 0)
    _thick_line(pen, 60, 0, 460, 0)


# Lowercase
def draw_a(pen):
    _thick_arc(pen, 260, 250, 190, 250, 0, 2*PI)
    _thick_line(pen, 450, 0, 450, X_HEIGHT)


def draw_b(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_arc(pen, 280, 250, 200, 250, -PI/2, PI*1.5)


def draw_c(pen):
    _thick_arc(pen, 250, 250, 190, 250, PI*0.35, PI*1.65)


def draw_d(pen):
    _thick_arc(pen, 250, 250, 190, 250, 0, 2*PI)
    _thick_line(pen, 440, 0, 440, CAP_HEIGHT)


def draw_e(pen):
    _thick_line(pen, 70, 260, 430, 260)
    _thick_arc(pen, 250, 260, 190, 240, 0, PI)
    _thick_arc(pen, 250, 200, 190, 200, PI*0.5, PI*1.2)


def draw_f(pen):
    _thick_line(pen, 120, 0, 120, 600)
    _thick_arc(pen, 250, 600, 130, 100, PI*0.5, PI)
    _thick_line(pen, 40, X_HEIGHT, 280, X_HEIGHT)


def draw_g(pen):
    _thick_arc(pen, 250, 280, 180, 220, 0, 2*PI)
    _thick_line(pen, 430, X_HEIGHT, 430, -120)
    _thick_arc(pen, 300, -120, 130, 80, -PI/2, 0)


def draw_h(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_arc(pen, 280, 350, 200, 150, PI*0.5, PI)
    _thick_line(pen, 480, 0, 480, 350)


def draw_i(pen):
    _thick_line(pen, 150, 0, 150, X_HEIGHT)
    # dot
    _oval(pen, 150, 580, 40, 40, 8)


def draw_j(pen):
    _thick_line(pen, 200, X_HEIGHT, 200, -80)
    _thick_arc(pen, 120, -80, 80, 80, -PI/2, 0)
    _oval(pen, 200, 580, 40, 40, 8)


def draw_k(pen):
    _thick_line(pen, 80, 0, 80, CAP_HEIGHT)
    _thick_line(pen, 380, X_HEIGHT, 80, 220)
    _thick_line(pen, 160, 280, 400, 0)


def draw_l(pen):
    _thick_line(pen, 150, 0, 150, CAP_HEIGHT)


def draw_m(pen):
    _thick_line(pen, 60, 0, 60, X_HEIGHT)
    _thick_arc(pen, 200, 370, 140, 130, PI*0.5, PI)
    _thick_line(pen, 340, 0, 340, 370)
    _thick_arc(pen, 470, 370, 130, 130, PI*0.5, PI)
    _thick_line(pen, 600, 0, 600, 370)


def draw_n(pen):
    _thick_line(pen, 80, 0, 80, X_HEIGHT)
    _thick_arc(pen, 260, 360, 180, 140, PI*0.5, PI)
    _thick_line(pen, 440, 0, 440, 360)


def draw_o(pen):
    _thick_arc(pen, 250, 250, 200, 250, 0, 2*PI)


def draw_p(pen):
    _thick_line(pen, 80, -200, 80, X_HEIGHT)
    _thick_arc(pen, 280, 250, 200, 250, -PI/2, PI*1.5)


def draw_q(pen):
    _thick_arc(pen, 240, 250, 190, 250, 0, 2*PI)
    _thick_line(pen, 430, -200, 430, X_HEIGHT)


def draw_r(pen):
    _thick_line(pen, 80, 0, 80, X_HEIGHT)
    _thick_arc(pen, 250, 380, 170, 120, PI*0.5, PI*0.9)


def draw_s(pen):
    _thick_arc(pen, 220, 380, 150, 120, PI*0.15, PI)
    _thick_arc(pen, 220, 160, 160, 140, -PI*0.85, PI*0.15)


def draw_t(pen):
    _thick_line(pen, 150, 0, 150, 620)
    _thick_line(pen, 50, X_HEIGHT, 300, X_HEIGHT)


def draw_u(pen):
    _thick_line(pen, 80, 160, 80, X_HEIGHT)
    _thick_arc(pen, 250, 160, 170, 160, -PI, 0)
    _thick_line(pen, 420, 0, 420, X_HEIGHT)


def draw_v(pen):
    _thick_line(pen, 60, X_HEIGHT, 230, 0)
    _thick_line(pen, 230, 0, 400, X_HEIGHT)


def draw_w(pen):
    _thick_line(pen, 40, X_HEIGHT, 140, 0)
    _thick_line(pen, 140, 0, 250, 320)
    _thick_line(pen, 250, 320, 360, 0)
    _thick_line(pen, 360, 0, 460, X_HEIGHT)


def draw_x(pen):
    _thick_line(pen, 60, 0, 400, X_HEIGHT)
    _thick_line(pen, 60, X_HEIGHT, 400, 0)


def draw_y(pen):
    _thick_line(pen, 60, X_HEIGHT, 240, 120)
    _thick_line(pen, 420, X_HEIGHT, 200, -200)


def draw_z(pen):
    _thick_line(pen, 60, X_HEIGHT, 400, X_HEIGHT)
    _thick_line(pen, 400, X_HEIGHT, 60, 0)
    _thick_line(pen, 60, 0, 400, 0)


# Digits
def draw_0(pen):
    _thick_arc(pen, 260, 350, 200, 350, 0, 2*PI)


def draw_1(pen):
    _thick_line(pen, 220, 0, 220, CAP_HEIGHT)
    _thick_line(pen, 140, 580, 220, CAP_HEIGHT)
    _thick_line(pen, 120, 0, 340, 0)


def draw_2(pen):
    _thick_arc(pen, 260, 520, 200, 180, 0, PI)
    _thick_line(pen, 460, 520, 60, 0)
    _thick_line(pen, 60, 0, 460, 0)


def draw_3(pen):
    _thick_arc(pen, 240, 530, 190, 170, -PI/2, PI*0.7)
    _thick_arc(pen, 240, 220, 210, 220, -PI*0.7, PI/2)


def draw_4(pen):
    _thick_line(pen, 350, 0, 350, CAP_HEIGHT)
    _thick_line(pen, 350, CAP_HEIGHT, 60, 250)
    _thick_line(pen, 60, 250, 460, 250)


def draw_5(pen):
    _thick_line(pen, 400, CAP_HEIGHT, 100, CAP_HEIGHT)
    _thick_line(pen, 100, CAP_HEIGHT, 80, 380)
    _thick_arc(pen, 250, 200, 210, 200, -PI*0.7, PI*0.7)


def draw_6(pen):
    _thick_arc(pen, 250, 220, 200, 220, 0, 2*PI)
    _thick_line(pen, 60, 220, 160, CAP_HEIGHT)


def draw_7(pen):
    _thick_line(pen, 60, CAP_HEIGHT, 460, CAP_HEIGHT)
    _thick_line(pen, 460, CAP_HEIGHT, 200, 0)


def draw_8(pen):
    _thick_arc(pen, 260, 530, 170, 170, 0, 2*PI)
    _thick_arc(pen, 260, 200, 200, 200, 0, 2*PI)


def draw_9(pen):
    _thick_arc(pen, 270, 480, 190, 220, 0, 2*PI)
    _thick_line(pen, 460, 480, 360, 0)


# Punctuation
def draw_period(pen):
    _oval(pen, 130, 40, 45, 45, 8)


def draw_comma(pen):
    _oval(pen, 130, 60, 45, 45, 8)
    _thick_line(pen, 130, 15, 80, -80, 50)


def draw_exclam(pen):
    _thick_line(pen, 130, 180, 130, CAP_HEIGHT)
    _oval(pen, 130, 40, 45, 45, 8)


def draw_question(pen):
    _thick_arc(pen, 240, 530, 180, 170, 0, PI)
    _thick_line(pen, 240, 360, 240, 220)
    _oval(pen, 240, 40, 45, 45, 8)


def draw_apostrophe(pen):
    _thick_line(pen, 130, 550, 100, CAP_HEIGHT, 50)


def draw_quote(pen):
    _thick_line(pen, 110, 550, 80, CAP_HEIGHT, 45)
    _thick_line(pen, 230, 550, 200, CAP_HEIGHT, 45)


def draw_hyphen(pen):
    _thick_line(pen, 60, 280, 340, 280)


def draw_ampersand(pen):
    _thick_arc(pen, 220, 500, 160, 170, PI*0.2, PI*1.5)
    _thick_arc(pen, 200, 200, 180, 200, PI*0.5, PI*1.8)
    _thick_line(pen, 350, 0, 480, 350)


def draw_dollar(pen):
    draw_S(pen)
    _thick_line(pen, 260, -40, 260, 740)


def draw_colon(pen):
    _oval(pen, 140, 160, 42, 42, 8)
    _oval(pen, 140, 380, 42, 42, 8)


def draw_semicolon(pen):
    _oval(pen, 140, 380, 42, 42, 8)
    _oval(pen, 140, 160, 42, 42, 8)
    _thick_line(pen, 140, 118, 90, 40, 45)


def draw_slash(pen):
    _thick_line(pen, 60, -50, 380, 750)


def draw_paren_left(pen):
    _thick_arc(pen, 350, 350, 280, 400, PI*0.6, PI*1.4)


def draw_paren_right(pen):
    _thick_arc(pen, 50, 350, 280, 400, -PI*0.4, PI*0.4)


def draw_at(pen):
    _thick_arc(pen, 300, 350, 260, 350, 0, 2*PI)
    _thick_arc(pen, 320, 350, 120, 150, 0, 2*PI)
    _thick_line(pen, 440, 350, 440, 150)


def draw_hash(pen):
    _thick_line(pen, 150, 0, 200, CAP_HEIGHT)
    _thick_line(pen, 330, 0, 380, CAP_HEIGHT)
    _thick_line(pen, 60, 250, 460, 250)
    _thick_line(pen, 60, 450, 460, 450)


def draw_percent(pen):
    _thick_line(pen, 60, 0, 460, CAP_HEIGHT)
    _oval(pen, 150, 580, 80, 80, 8)
    _oval(pen, 370, 120, 80, 80, 8)


def draw_plus(pen):
    _thick_line(pen, 60, 300, 420, 300)
    _thick_line(pen, 240, 120, 240, 480)


def draw_equals(pen):
    _thick_line(pen, 60, 220, 420, 220)
    _thick_line(pen, 60, 380, 420, 380)


def draw_star(pen):
    _thick_line(pen, 200, 250, 200, 550)
    _thick_line(pen, 80, 330, 320, 470)
    _thick_line(pen, 80, 470, 320, 330)


def draw_underscore(pen):
    _thick_line(pen, 20, -40, 480, -40)


def draw_bracket_left(pen):
    _thick_line(pen, 200, -100, 200, 800)
    _thick_line(pen, 200, 800, 320, 800)
    _thick_line(pen, 200, -100, 320, -100)


def draw_bracket_right(pen):
    _thick_line(pen, 200, -100, 200, 800)
    _thick_line(pen, 80, 800, 200, 800)
    _thick_line(pen, 80, -100, 200, -100)


def draw_tilde(pen):
    _thick_arc(pen, 150, 340, 100, 60, 0, PI)
    _thick_arc(pen, 350, 340, 100, 60, PI, 2*PI)


# ---------------------------------------------------------------------------
# Glyph registry: name -> (draw_func, advance_width)
# ---------------------------------------------------------------------------

GLYPHS = {
    ".notdef": (None, 500),
    "space": (draw_space, 300),
    # Uppercase
    "A": (draw_A, 560), "B": (draw_B, 520), "C": (draw_C, 520),
    "D": (draw_D, 540), "E": (draw_E, 480), "F": (draw_F, 460),
    "G": (draw_G, 540), "H": (draw_H, 540), "I": (draw_I, 400),
    "J": (draw_J, 420), "K": (draw_K, 500), "L": (draw_L, 460),
    "M": (draw_M, 580), "N": (draw_N, 540), "O": (draw_O, 540),
    "P": (draw_P, 500), "Q": (draw_Q, 560), "R": (draw_R, 520),
    "S": (draw_S, 500), "T": (draw_T, 520), "U": (draw_U, 540),
    "V": (draw_V, 540), "W": (draw_W, 580), "X": (draw_X, 540),
    "Y": (draw_Y, 520), "Z": (draw_Z, 520),
    # Lowercase
    "a": (draw_a, 500), "b": (draw_b, 520), "c": (draw_c, 460),
    "d": (draw_d, 500), "e": (draw_e, 480), "f": (draw_f, 360),
    "g": (draw_g, 500), "h": (draw_h, 540), "i": (draw_i, 300),
    "j": (draw_j, 300), "k": (draw_k, 460), "l": (draw_l, 300),
    "m": (draw_m, 660), "n": (draw_n, 520), "o": (draw_o, 500),
    "p": (draw_p, 520), "q": (draw_q, 500), "r": (draw_r, 380),
    "s": (draw_s, 420), "t": (draw_t, 360), "u": (draw_u, 500),
    "v": (draw_v, 460), "w": (draw_w, 520), "x": (draw_x, 460),
    "y": (draw_y, 480), "z": (draw_z, 460),
    # Digits
    "zero": (draw_0, 520), "one": (draw_1, 420), "two": (draw_2, 520),
    "three": (draw_3, 500), "four": (draw_4, 520), "five": (draw_5, 500),
    "six": (draw_6, 500), "seven": (draw_7, 520), "eight": (draw_8, 520),
    "nine": (draw_9, 500),
    # Punctuation
    "period": (draw_period, 260), "comma": (draw_comma, 260),
    "exclam": (draw_exclam, 260), "question": (draw_question, 440),
    "quotesingle": (draw_apostrophe, 220), "quotedbl": (draw_quote, 340),
    "hyphen": (draw_hyphen, 400), "ampersand": (draw_ampersand, 540),
    "dollar": (draw_dollar, 520), "colon": (draw_colon, 280),
    "semicolon": (draw_semicolon, 280), "slash": (draw_slash, 440),
    "parenleft": (draw_paren_left, 360), "parenright": (draw_paren_right, 360),
    "at": (draw_at, 600), "numbersign": (draw_hash, 520),
    "percent": (draw_percent, 540), "plus": (draw_plus, 480),
    "equal": (draw_equals, 480), "asterisk": (draw_star, 400),
    "underscore": (draw_underscore, 500),
    "bracketleft": (draw_bracket_left, 360), "bracketright": (draw_bracket_right, 360),
    "asciitilde": (draw_tilde, 500),
}

# Unicode mapping
CHAR_MAP = {}
for name in GLYPHS:
    if len(name) == 1 and name.isascii():
        CHAR_MAP[ord(name)] = name
# Manually map the rest
_EXTRA_MAP = {
    0x20: "space", 0x30: "zero", 0x31: "one", 0x32: "two", 0x33: "three",
    0x34: "four", 0x35: "five", 0x36: "six", 0x37: "seven", 0x38: "eight",
    0x39: "nine", 0x2E: "period", 0x2C: "comma", 0x21: "exclam",
    0x3F: "question", 0x27: "quotesingle", 0x22: "quotedbl", 0x2D: "hyphen",
    0x26: "ampersand", 0x24: "dollar", 0x3A: "colon", 0x3B: "semicolon",
    0x2F: "slash", 0x28: "parenleft", 0x29: "parenright", 0x40: "at",
    0x23: "numbersign", 0x25: "percent", 0x2B: "plus", 0x3D: "equal",
    0x2A: "asterisk", 0x5F: "underscore", 0x5B: "bracketleft",
    0x5D: "bracketright", 0x7E: "asciitilde",
}
CHAR_MAP.update(_EXTRA_MAP)


def build_font(output_path, flavor=None):
    """Build the font and save it."""
    from fontTools.ttLib import TTFont
    from fontTools.fontBuilder import FontBuilder

    glyph_names = list(GLYPHS.keys())

    fb2 = FontBuilder(UPM, isTTF=True)
    fb2.setupGlyphOrder(glyph_names)
    fb2.setupCharacterMap(CHAR_MAP)

    from fontTools.pens.ttGlyphPen import TTGlyphPen

    pen_map = {}
    for name, (draw_func, width) in GLYPHS.items():
        pen = TTGlyphPen(None)
        if draw_func is not None:
            draw_func(pen)
            try:
                pen_map[name] = pen.glyph()
            except Exception:
                # If glyph drawing fails, use empty
                pen2 = TTGlyphPen(None)
                pen2.moveTo((0, 0))
                pen2.lineTo((1, 0))
                pen2.lineTo((0, 1))
                pen2.closePath()
                pen_map[name] = pen2.glyph()
        else:
            # Empty glyph for .notdef and space
            pen_map[name] = TTGlyphPen(None).glyph()  # empty

    fb2.setupGlyf(pen_map)
    metrics = {name: (GLYPHS[name][1], 0) for name in glyph_names}
    # Set left side bearing properly
    for name in glyph_names:
        if name in pen_map and hasattr(pen_map[name], 'xMin') and pen_map[name].numberOfContours > 0:
            metrics[name] = (GLYPHS[name][1], pen_map[name].xMin)
    fb2.setupHorizontalMetrics(metrics)

    fb2.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb2.setupNameTable({
        "familyName": FAMILY_NAME,
        "styleName": "Regular",
        "psName": FONT_NAME + "-Regular",
        "manufacturer": "Handwritten Font Generator",
        "designer": "Generated from handwriting sample",
        "description": "A handwriting font inspired by a vintage jewelry note from Trinidad, circa 1968",
        "vendorURL": "",
        "designerURL": "",
        "licenseDescription": "Free for personal use",
        "typographicFamily": FAMILY_NAME,
        "typographicSubfamily": "Regular",
    })

    fb2.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=abs(DESCENT),
        sxHeight=X_HEIGHT,
        sCapHeight=CAP_HEIGHT,
        fsType=0,  # installable embedding
    )

    fb2.setupPost()
    fb2.setupHead(unitsPerEm=UPM)

    font = fb2.font

    font.save(output_path)

    return output_path


if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    os.makedirs(out_dir, exist_ok=True)

    ttf_path = os.path.join(out_dir, "DeLimaHand-Regular.ttf")
    otf_path = os.path.join(out_dir, "DeLimaHand-Regular.otf")

    build_font(ttf_path)
    print(f"Created: {ttf_path}")
    build_font(otf_path)
    print(f"Created: {otf_path}")
    print("Done!")
