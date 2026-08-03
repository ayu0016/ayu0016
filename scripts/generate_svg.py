"""
Rendering layer.

Responsibility: convert prepared data (contributions.json + trainer.json)
into the final SVG. This file knows nothing about GitHub's API — it only
knows how to draw.

Layer order: background -> header/progress -> heatmap -> footer/partner.
"""

import json
import os

import config

CELL_SIZE = 11
CELL_GAP = 3
CARD_PADDING = 24
HEATMAP_TOP_OFFSET = 96
PROGRESS_BAR_WIDTH = 160


def contribution_color(count: int) -> str:
    c = config.COLORS
    if count == 0:
        return c["cell_empty"]
    if count <= 3:
        return c["cell_low"]
    if count <= 6:
        return c["cell_medium"]
    if count <= 9:
        return c["cell_high"]
    return c["cell_max"]


def render_heatmap(weeks: list, x0: int, y0: int) -> str:
    parts = []
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            cx = x0 + week_index * (CELL_SIZE + CELL_GAP)
            cy = y0 + day_index * (CELL_SIZE + CELL_GAP)
            color = contribution_color(day["count"])
            parts.append(
                f'<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="2.5" ry="2.5" fill="{color}" />'
            )
    return "".join(parts)


def render_partner_icon(x: int, y: int) -> str:
    """
    Original abstract low-poly icon representing the partner as a symbolic
    'digital construct' — intentionally NOT a reproduction of any
    copyrighted Pokemon character or official artwork.

    If you want the specific character likeness, swap this <g> block for
    your own licensed or commissioned artwork; keep the same transform
    position if you do.
    """
    accent = config.COLORS["accent"]
    primary = config.COLORS["text_primary"]
    return f'''<g transform="translate({x},{y})" opacity="0.9">
    <polygon points="14,0 28,10 22,26 6,26 0,10" fill="{accent}" fill-opacity="0.16" stroke="{accent}" stroke-width="1.2"/>
    <polygon points="14,6 21,12 18,22 10,22 7,12" fill="{accent}" fill-opacity="0.55"/>
    <circle cx="14" cy="13" r="2.1" fill="{primary}"/>
  </g>'''


def build_svg(trainer: dict, contributions: dict) -> str:
    colors = config.COLORS
    weeks = contributions["weeks"]
    num_weeks = len(weeks)

    heatmap_x = CARD_PADDING
    heatmap_y = HEATMAP_TOP_OFFSET
    heatmap_width = num_weeks * (CELL_SIZE + CELL_GAP)
    heatmap_height = 7 * (CELL_SIZE + CELL_GAP)

    card_width = max(heatmap_width + CARD_PADDING * 2, 480)
    card_height = heatmap_y + heatmap_height + 64

    progress_fill_width = round(PROGRESS_BAR_WIDTH * (trainer["progressPercent"] / 100))

    heatmap_svg = render_heatmap(weeks, heatmap_x, heatmap_y)
    partner_svg = render_partner_icon(card_width - 60, card_height - 56)

    return f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Trainer Journey: Level {trainer['level']} {trainer['levelLabel']}, active {trainer['activeWeeks']} of the last {trainer['totalWeeks']} weeks">
  <rect x="0" y="0" width="{card_width}" height="{card_height}" rx="14" fill="{colors['background']}" stroke="{colors['card_border']}" stroke-width="1"/>

  <text x="{CARD_PADDING}" y="34" fill="{colors['text_primary']}" font-family="Segoe UI, Inter, sans-serif" font-size="16" font-weight="600">Trainer Journey</text>
  <text x="{CARD_PADDING}" y="52" fill="{colors['text_muted']}" font-family="Segoe UI, Inter, sans-serif" font-size="11">@{trainer['username']} · Level {trainer['level']} — {trainer['levelLabel']}</text>

  <rect x="{CARD_PADDING}" y="62" width="{PROGRESS_BAR_WIDTH}" height="5" rx="2.5" fill="{colors['cell_empty']}"/>
  <rect x="{CARD_PADDING}" y="62" width="{progress_fill_width}" height="5" rx="2.5" fill="{colors['accent']}"/>
  <text x="{CARD_PADDING + PROGRESS_BAR_WIDTH + 10}" y="67" fill="{colors['text_muted']}" font-family="Segoe UI, Inter, sans-serif" font-size="10">{trainer['progressPercent']}% to next level</text>

  {heatmap_svg}

  <text x="{CARD_PADDING}" y="{card_height - 18}" fill="{colors['text_muted']}" font-family="Segoe UI, Inter, sans-serif" font-size="10">Active {trainer['activeWeeks']}/{trainer['totalWeeks']} of the last {trainer['totalWeeks']} weeks</text>

  {partner_svg}
</svg>'''


def main():
    with open("data/contributions.json") as f:
        contributions = json.load(f)
    with open("data/trainer.json") as f:
        trainer = json.load(f)

    svg = build_svg(trainer, contributions)

    os.makedirs("assets", exist_ok=True)
    with open("assets/trainer-journey.svg", "w") as f:
        f.write(svg)

    print(f"Generated assets/trainer-journey.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
