from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1920, 1080
OUT = Path(r"E:\Projects\ErdosProblems\output\math-difficulty-landscape.png")

BG = "#F5F3EE"
INK = "#171A1F"
MUTED = "#666A72"
GRID = "#D9D6CF"
BLUE = "#3677C8"
PURPLE = "#7659A8"
ORANGE = "#C86A2B"

FONT_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SEMIBOLD = r"C:\Windows\Fonts\seguisb.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    path = {
        "regular": FONT_REGULAR,
        "semibold": FONT_SEMIBOLD,
        "bold": FONT_BOLD,
    }[weight]
    return ImageFont.truetype(path, size=size)


TITLE = font(60, "bold")
SUBTITLE = font(28)
AXIS_TITLE = font(21, "semibold")
AXIS = font(18, "semibold")
ROW = font(25, "semibold")
NOTE = font(19)
ANCHOR = font(18, "semibold")
MICRO = font(16)
FOOT = font(17)


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(canvas)


def band(
    y: int,
    start: float,
    end: float,
    color: str,
    peaks: list[tuple[float, float, float]],
    base_height: float = 8,
) -> None:
    """Draw an editorial qualitative distribution band on the shared axis."""
    x0, x1 = PLOT_LEFT, PLOT_RIGHT
    left = x0 + (x1 - x0) * start
    right = x0 + (x1 - x0) * end
    width = max(1.0, right - left)
    top: list[tuple[float, float]] = []
    bottom: list[tuple[float, float]] = []

    steps = max(40, int(width / 4))
    for i in range(steps + 1):
        t = i / steps
        taper = math.sin(math.pi * t) ** 0.45
        density = base_height
        for center, spread, amplitude in peaks:
            density += amplitude * math.exp(-((t - center) ** 2) / (2 * spread**2))
        h = max(1.5, density * taper)
        x = left + width * t
        top.append((x, y - h))
        bottom.append((x, y + h))

    polygon = top + list(reversed(bottom))
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(polygon, fill=118)
    blurred = mask.filter(ImageFilter.GaussianBlur(radius=7))

    soft_layer = Image.new("RGBA", (WIDTH, HEIGHT), rgba(color, 0))
    soft_layer.putalpha(blurred)
    canvas.paste(soft_layer, (0, 0), soft_layer)

    crisp = Image.new("RGBA", (WIDTH, HEIGHT), rgba(color, 0))
    crisp_draw = ImageDraw.Draw(crisp)
    crisp_draw.polygon(polygon, fill=rgba(color, 66))
    crisp_draw.line((left + 14, y, right - 14, y), fill=rgba(color, 224), width=3)
    canvas.paste(crisp, (0, 0), crisp)


def dot(x: int, y: int, color: str, radius: int = 7) -> None:
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=color,
        outline=BG,
        width=3,
    )


def centered(text: str, x: int, y: int, fnt: ImageFont.FreeTypeFont, fill: str) -> None:
    draw.text((x, y), text, font=fnt, fill=fill, anchor="mm")


PLOT_LEFT = 610
PLOT_RIGHT = 1840
AXIS_Y = 236

# Quiet paper-like frontier wash: an atmospheric region, not a panel.
wash = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
wash_px = wash.load()
wash_start = 1500
for x in range(wash_start, WIDTH):
    alpha = int(20 * (x - wash_start) / (WIDTH - wash_start))
    color = rgba(PURPLE, alpha)
    for y in range(178, 930):
        wash_px[x, y] = color
canvas.paste(wash, (0, 0), wash)

# Heading and framing copy.
draw.text((58, 43), "THE SHAPE OF MATHEMATICAL DIFFICULTY", font=TITLE, fill=INK)
draw.text(
    (60, 117),
    "Not a ladder: problem families overlap, and every family contains outliers.",
    font=SUBTITLE,
    fill=MUTED,
)
draw.text(
    (PLOT_LEFT, 164),
    "TYPICAL BARRIER TO A COMPLETE SOLUTION →",
    font=AXIS_TITLE,
    fill=INK,
)

# Legend.
legend_y = 145
legend_items = [
    (BLUE, "known-solution collection"),
    (PURPLE, "mixed-status corpus"),
    (ORANGE, "currently open"),
]
legend_x = 1195
for color, label in legend_items:
    draw.ellipse((legend_x, legend_y - 5, legend_x + 10, legend_y + 5), fill=color)
    draw.text((legend_x + 18, legend_y - 12), label, font=MICRO, fill=MUTED)
    legend_x += 215

# Shared qualitative axis.
axis_ticks = [
    (0.00, "KNOWN\nMETHODS"),
    (0.25, "SUSTAINED\nINGENUITY"),
    (0.50, "SPECIALIST\nSYNTHESIS"),
    (0.75, "ORIGINAL\nRESEARCH"),
    (1.00, "UNKNOWN\nFRONTIER"),
]
draw.line((PLOT_LEFT, AXIS_Y, PLOT_RIGHT, AXIS_Y), fill=MUTED, width=2)
draw.polygon(
    [(PLOT_RIGHT, AXIS_Y), (PLOT_RIGHT - 16, AXIS_Y - 8), (PLOT_RIGHT - 16, AXIS_Y + 8)],
    fill=MUTED,
)
for position, label in axis_ticks:
    x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * position)
    draw.line((x, AXIS_Y - 7, x, 937), fill=GRID, width=2)
    centered(label, x, 207, AXIS, MUTED)

# Rows: each path is a range, never a point score.
rows = [
    (310, "PROJECT EULER", "known answers · warm-ups to expert computational mathematics"),
    (400, "OLYMPIADS / IMO", "known solutions · accessible entries to world-class proofs"),
    (490, "PUTNAM / GRADUATE", "known solutions · proof craft through advanced theory"),
    (580, "ACTIVE RESEARCH QUESTIONS", "currently open · new lemmas to long-lived conjectures"),
    (670, "ERDŐS PROBLEM CORPUS", "1,200+ catalogued · mixed, evolving, exceptionally broad"),
    (760, "HILBERT’S 23", "historical mixed set · resolved, partial, reformulated and open"),
    (850, "MILLENNIUM FRONTIER", "7 Prize Problems · 6 open, Poincaré solved"),
]
for y, label, note in rows:
    draw.text((58, y - 18), label, font=ROW, fill=INK)
    draw.text((58, y + 17), note, font=NOTE, fill=MUTED)

band(310, 0.00, 0.69, BLUE, [(0.17, 0.12, 21), (0.42, 0.18, 17), (0.70, 0.16, 10)])
band(400, 0.12, 0.69, BLUE, [(0.30, 0.18, 15), (0.63, 0.20, 21)])
band(490, 0.18, 0.78, BLUE, [(0.38, 0.21, 16), (0.68, 0.17, 22)])
band(580, 0.28, 1.00, ORANGE, [(0.22, 0.15, 14), (0.52, 0.20, 20), (0.82, 0.16, 25)])
band(670, 0.14, 1.00, PURPLE, [(0.18, 0.14, 14), (0.48, 0.23, 22), (0.82, 0.16, 27)])
band(760, 0.46, 1.00, PURPLE, [(0.27, 0.18, 17), (0.74, 0.22, 25)])
band(850, 0.70, 1.00, ORANGE, [(0.52, 0.25, 28)])

# Project Euler: three current site-rating anchors make the wide range concrete.
pe_points = [
    (0.025, "#1 · 1%"),
    (0.36, "#659 · 50%"),
    (0.63, "#526 · 86%"),
]
for position, label in pe_points:
    x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * position)
    dot(x, 310, BLUE)
    centered(label, x, 282, ANCHOR, INK)
draw.text((1418, 330), "Project Euler site ratings · July 2026", font=MICRO, fill=MUTED)

# Competition and research anchors.
imo_x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * 0.61)
dot(imo_x, 400, BLUE)
centered("IMO 1988 / P6", imo_x, 372, ANCHOR, INK)

research_x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * 0.84)
dot(research_x, 580, ORANGE)
centered("short statement ≠ short solution", research_x, 552, ANCHOR, INK)

# Erdős–Straus is one highlighted example inside a broad corpus, never its rank.
es_x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * 0.76)
dot(es_x, 670, PURPLE, radius=8)
centered("ERDŐS–STRAUS", es_x, 640, ANCHOR, INK)
centered("4/n = 1/x + 1/y + 1/z ?", es_x, 699, MICRO, MUTED)

# Riemann Hypothesis belongs to both the Hilbert and Millennium collections.
rh_x = int(PLOT_LEFT + (PLOT_RIGHT - PLOT_LEFT) * 0.91)
dot(rh_x, 760, PURPLE, radius=8)
dot(rh_x, 850, ORANGE, radius=8)
draw.line((rh_x, 770, rh_x, 840), fill=MUTED, width=2)
centered("RIEMANN HYPOTHESIS", rh_x, 732, ANCHOR, INK)
centered("Hilbert 8 + Millennium", rh_x, 881, MICRO, MUTED)

# Footer: the epistemic guardrail is part of the graphic, not fine-print legalese.
draw.line((58, 965, 1862, 965), fill=GRID, width=2)
draw.text(
    (58, 994),
    "Illustrative, not empirical  •  bands show span, not rank  •  open is a status, not a difficulty score",
    font=FOOT,
    fill=MUTED,
)
draw.text(
    (1862, 994),
    "A simple statement can hide a generational problem.",
    font=FOOT,
    fill=INK,
    anchor="ra",
)

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUT, format="PNG", optimize=True)
print(OUT)
