"""Generates the CCreations brand files: logo variants and social templates as SVG.

All text is converted to outlines, so the files render identically without the fonts installed.
Requires: pip install fonttools brotli uharfbuzz
Usage: python3 tools/build_brand.py   (run from the repository root)
"""
import io
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "brand"

ORANGE, AMBER, CHARCOAL, SAND, CARD = "#e35e20", "#efa037", "#2c302e", "#f0eae1", "#fcfaf7"

MARK_W, MARK_H = 74, 50


class Face:
    def __init__(self, filename):
        self.tt = TTFont(FONTS / filename)
        self.tt.flavor = None
        raw = io.BytesIO()
        self.tt.save(raw)
        self.hb = hb.Font(hb.Face(raw.getvalue()))
        self.upem = self.tt["head"].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def outline(self, text, size, x=0, y=0, tracking=0.0, anchor="start"):
        """Returns (path data, width) for text set at baseline (x, y)."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf)
        scale = size / self.upem
        track = tracking * size
        width = sum(p.x_advance for p in buf.glyph_positions) * scale + track * (len(buf.glyph_infos) - 1)
        cursor = x - {"start": 0, "middle": width / 2, "end": width}[anchor]
        parts = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
            origin_x = cursor + pos.x_offset * scale
            self.glyphs[self.order[info.codepoint]].draw(
                TransformPen(pen, (scale, 0, 0, -scale, origin_x, y - pos.y_offset * scale))
            )
            parts.append(pen.getCommands())
            cursor += pos.x_advance * scale + track
        return "".join(parts), width


DISPLAY = Face("bai-jamjuree-600.woff2")       # wordmark
DISPLAY_HEAVY = Face("bai-jamjuree-700.woff2")  # headlines
BODY = Face("roboto-400.woff2")                 # owner line
LABEL = Face("roboto-condensed-700.woff2")      # eyebrows


def mark(ink):
    """The interlocked monogram on a 74 x 50 grid. `ink` colours the C."""
    return (
        f'<g fill="none" stroke-width="9.6">'
        f'<circle cx="25" cy="25" r="20" stroke="{ORANGE}"/>'
        f'<path d="M65.18 13.24A20 20 0 1 0 65.18 36.76" stroke="{ink}"/>'
        f'<path d="M45 25A20 20 0 0 1 5 25" stroke="{ORANGE}"/>'
        f"</g>"
        f'<path d="M45 10.34A24.8 24.8 0 0 1 45 39.66A15.2 15.2 0 0 1 37 34.33'
        f'A15.2 15.2 0 0 0 37 15.67A15.2 15.2 0 0 1 45 10.34Z" fill="{AMBER}"/>'
    )


def lockup_horizontal(ink):
    """Monogram with the wordmark to its right. Returns (markup, width, height)."""
    name, name_w = DISPLAY.outline("CCreations", 32, 0, 27.5)
    left = MARK_W + 9
    owner, _ = BODY.outline("JORIS SCHETS", 10.5, left + name_w / 2, 44, tracking=0.32, anchor="middle")
    body = f'{mark(ink)}<path fill="{ink}" d="{name}" transform="translate({left} 0)"/><path fill="{ink}" d="{owner}"/>'
    return body, left + name_w + 1, MARK_H


def lockup_stacked(ink):
    """Monogram above the wordmark. Returns (markup, width, height)."""
    _, name_w = DISPLAY.outline("CCreations", 40)
    width = name_w + 2
    centre = width / 2
    scale = 1.7
    name, _ = DISPLAY.outline("CCreations", 40, centre, 133, anchor="middle")
    owner, _ = BODY.outline("JORIS SCHETS", 13, centre, 158, tracking=0.32, anchor="middle")
    body = (
        f'<g transform="translate({centre - MARK_W * scale / 2:.2f} 0) scale({scale})">{mark(ink)}</g>'
        f'<path fill="{ink}" d="{name}"/><path fill="{ink}" d="{owner}"/>'
    )
    return body, width, 162


def svg(width, height, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" '
        f'width="{width:.0f}" height="{height:.0f}" role="img"><title>{title}</title>{body}</svg>\n'
    )


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name}: {len(content) / 1024:.1f} kB")


def placed(lockup, x, y, height):
    body, width, natural = lockup
    scale = height / natural
    return f'<g transform="translate({x} {y}) scale({scale:.4f})">{body}</g>', width * scale


# ---------- Logos ----------
for tone, ink in (("light", CHARCOAL), ("dark", SAND)):
    body, w, h = lockup_stacked(ink)
    write(f"logo-primary-{tone}.svg", svg(w, h, body, "CCreations Joris Schets"))
    body, w, h = lockup_horizontal(ink)
    write(f"logo-horizontal-{tone}.svg", svg(w, h, body, "CCreations Joris Schets"))
    write(f"logo-mark-{tone}.svg", svg(MARK_W, MARK_H, mark(ink), "CCreations"))

# ---------- Favicon ----------
# The monogram fills the full width of a square. The C switches to sand when the browser uses a dark theme.
FAVICON_MARK = mark("currentColor").replace('stroke="currentColor"', 'class="c"')
(ROOT / "assets" / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 74 74">'
    f"<style>.c{{stroke:{CHARCOAL}}}@media(prefers-color-scheme:dark){{.c{{stroke:{SAND}}}}}</style>"
    f'<g transform="translate(0 12)">{FAVICON_MARK}</g></svg>\n',
    encoding="utf-8",
)

# ---------- Social templates ----------
DOTS = (
    '<defs><pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
    f'<circle cx="12" cy="12" r="1" fill="{CHARCOAL}" fill-opacity="0.1"/></pattern></defs>'
)

# LinkedIn banner, 1584 x 396. The left third stays empty: the profile photo covers it.
logo, _ = placed(lockup_horizontal(CHARCOAL), 560, 96, 104)
line, _ = DISPLAY_HEAVY.outline("Systemen die de operatie van KMO’s sturen.", 38, 560, 292)
write(
    "social-linkedin-banner.svg",
    svg(
        1584, 396,
        f'{DOTS}<rect width="1584" height="396" fill="{SAND}"/><rect width="1584" height="396" fill="url(#dots)"/>'
        f'<rect width="1584" height="10" fill="{ORANGE}"/><rect y="394" width="1584" height="2" fill="{CHARCOAL}"/>'
        f'{logo}<path fill="{CHARCOAL}" d="{line}"/>',
        "CCreations LinkedIn-banner",
    ),
)

# Square post, 1080 x 1080.
eyebrow, _ = LABEL.outline("VOORDEEL 02", 30, 96, 190, tracking=0.14)
headline = "".join(
    f'<path fill="{SAND}" d="{DISPLAY_HEAVY.outline(text, 104, 96, 360 + i * 122)[0]}"/>'
    for i, text in enumerate(("Eén overzicht", "in plaats van", "losse tools."))
)
logo, _ = placed(lockup_horizontal(SAND), 96, 880, 96)
write(
    "social-post-square.svg",
    svg(
        1080, 1080,
        f'<rect width="1080" height="1080" fill="{CHARCOAL}"/><rect width="1080" height="16" fill="{ORANGE}"/>'
        f'<path fill="{AMBER}" d="{eyebrow}"/>{headline}'
        f'<rect x="96" y="800" width="888" height="2" fill="{SAND}" fill-opacity="0.3"/>{logo}',
        "CCreations vierkante post",
    ),
)

# Profile image, 400 x 400. The monogram stays inside the circle most platforms crop to.
write(
    "social-avatar.svg",
    svg(
        400, 400,
        f'<rect width="400" height="400" fill="{SAND}"/>'
        f'<g transform="translate(78 117.6) scale(3.3)">{mark(CHARCOAL)}</g>',
        "CCreations profielbeeld",
    ),
)
