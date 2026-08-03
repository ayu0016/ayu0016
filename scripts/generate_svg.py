"""
Rendering layer.

Responsibility: convert prepared data (contributions.json + trainer.json)
into the final SVG. This file knows nothing about GitHub's API — it only
knows how to draw.

Layer order: background -> header (title, level badge, partner, quest,
XP bar) -> divider -> month/weekday labels -> heatmap -> legend -> divider
-> footer stats row.
"""

import json
import os
from datetime import datetime

import config

CELL_SIZE = 12
CELL_GAP = 3
CARD_PADDING = 24
WEEKDAY_LABEL_WIDTH = 26
PROGRESS_BAR_WIDTH = 160

WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # index within a Sun-Sat week

FONT = "Segoe UI, Inter, sans-serif"


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


def render_partner_icon(x: int, y: int, size: float = 1.0) -> str:
    """
    Original abstract low-poly icon representing the partner as a symbolic
    'digital construct' — intentionally NOT a reproduction of any
    copyrighted Pokemon character or official artwork.
    """
    accent = config.COLORS["accent"]
    primary = config.COLORS["text_primary"]
    return f'''<g transform="translate({x},{y}) scale({size})">
    <polygon points="14,0 28,10 22,26 6,26 0,10" fill="{accent}" fill-opacity="0.18" stroke="{accent}" stroke-width="1.2"/>
    <polygon points="14,6 21,12 18,22 10,22 7,12" fill="{accent}" fill-opacity="0.6"/>
    <circle cx="14" cy="13" r="2.1" fill="{primary}"/>
  </g>'''


def render_month_labels(weeks: list, x0: int, y: int) -> str:
    parts = []
    last_month = None
    for week_index, week in enumerate(weeks):
        if not week:
            continue
        month = datetime.strptime(week[0]["date"], "%Y-%m-%d").strftime("%b")
        if month != last_month:
            cx = x0 + week_index * (CELL_SIZE + CELL_GAP)
            parts.append(
                f'<text x="{cx}" y="{y}" fill="{config.COLORS["text_muted"]}" '
                f'font-family="{FONT}" font-size="9">{month}</text>'
            )
            last_month = month
    return "".join(parts)


def render_weekday_labels(x0: int, y0: int) -> str:
    parts = []
    for day_index, label in WEEKDAY_LABELS.items():
        cy = y0 + day_index * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
        parts.append(
            f'<text x="{x0}" y="{cy}" fill="{config.COLORS["text_muted"]}" '
            f'font-family="{FONT}" font-size="9" text-anchor="end">{label}</text>'
        )
    return "".join(parts)


def render_heatmap(weeks: list, x0: int, y0: int) -> str:
    parts = []
    for week_index, week in enumerate(weeks):
        for day_index, day in enumerate(week):
            cx = x0 + week_index * (CELL_SIZE + CELL_GAP)
            cy = y0 + day_index * (CELL_SIZE + CELL_GAP)
            color = contribution_color(day["count"])
            parts.append(
                f'<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="3" ry="3" fill="{color}" />'
            )
    return "".join(parts)


def render_legend(x_right: int, y: int) -> str:
    c = config.COLORS
    swatches = [c["cell_empty"], c["cell_low"], c["cell_medium"], c["cell_high"], c["cell_max"]]
    size, gap = 9, 3
    total_w = len(swatches) * (size + gap) - gap
    start_x = x_right - total_w
    parts = [
        f'<text x="{start_x - 30}" y="{y + size - 1}" fill="{c["text_muted"]}" '
        f'font-family="{FONT}" font-size="9">Less</text>'
    ]
    for i, color in enumerate(swatches):
        sx = start_x + i * (size + gap)
        parts.append(f'<rect x="{sx}" y="{y}" width="{size}" height="{size}" rx="2" fill="{color}"/>')
    parts.append(
        f'<text x="{x_right + 8}" y="{y + size - 1}" fill="{c["text_muted"]}" '
        f'font-family="{FONT}" font-size="9">More</text>'
    )
    return "".join(parts)


def render_footer_stats(trainer: dict, x_left: int, x_right: int, y: int) -> str:
    c = config.COLORS
    mid = (x_left + x_right) // 2
    active = f"Active Weeks • {trainer['activeWeeks']}/{trainer['totalWeeks']}"
    consistency = f"Consistency • {trainer['consistencyPercent']}%"
    next_lv = f"Next Lv • {trainer['progressPercent']}%"
    return f'''
    <text x="{x_left}" y="{y}" fill="{c['text_primary']}" font-family="{FONT}" font-size="10.5" text-anchor="start">{active}</text>
    <text x="{mid}" y="{y}" fill="{c['text_primary']}" font-family="{FONT}" font-size="10.5" text-anchor="middle">{consistency}</text>
    <text x="{x_right}" y="{y}" fill="{c['text_primary']}" font-family="{FONT}" font-size="10.5" text-anchor="end">{next_lv}</text>'''


def build_svg(trainer: dict, contributions: dict) -> str:
    c = config.COLORS
    weeks = contributions["weeks"]
    num_weeks = len(weeks)

    heatmap_x = CARD_PADDING + WEEKDAY_LABEL_WIDTH
    heatmap_width = num_weeks * (CELL_SIZE + CELL_GAP)
    heatmap_height = 7 * (CELL_SIZE + CELL_GAP)
    card_width = max(heatmap_x + heatmap_width + CARD_PADDING, 540)
    right_edge = card_width - CARD_PADDING

    title_y = 30
    username_y = 48
    partner_y = 68
    quest_y = 84
    progress_y = 100
    divider1_y = progress_y + 14

    month_label_y = divider1_y + 16
    heatmap_y = month_label_y + 8
    legend_y = heatmap_y + heatmap_height + 20
    divider2_y = legend_y + 16
    footer_y = divider2_y + 22
    card_height = footer_y + 14

    progress_fill_width = round(PROGRESS_BAR_WIDTH * (trainer["progressPercent"] / 100))

    partner_icon = render_partner_icon(CARD_PADDING, partner_y - 11, size=0.62)
    month_labels_svg = render_month_labels(weeks, heatmap_x, month_label_y)
    weekday_labels_svg = render_weekday_labels(heatmap_x - 8, heatmap_y)
    heatmap_svg = render_heatmap(weeks, heatmap_x, heatmap_y)
    legend_svg = render_legend(right_edge - 34, legend_y)
    footer_svg = render_footer_stats(trainer, CARD_PADDING, right_edge, footer_y)

    level_badge_w = 54
    level_badge_x = right_edge - level_badge_w

    return f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Trainer Journey: Level {trainer['level']} {trainer['levelLabel']}, active {trainer['activeWeeks']} of the last {trainer['totalWeeks']} weeks, partner {trainer['partner']}">
  <rect x="0" y="0" width="{card_width}" height="{card_height}" rx="14" fill="{c['background']}" stroke="{c['card_border']}" stroke-width="1"/>

  <text x="{CARD_PADDING}" y="{title_y}" fill="{c['text_primary']}" font-family="{FONT}" font-size="15" font-weight="700" letter-spacing="0.5">TRAINER JOURNEY</text>
  <rect x="{level_badge_x}" y="{title_y - 15}" width="{level_badge_w}" height="20" rx="10" fill="{c['accent']}" fill-opacity="0.15" stroke="{c['accent']}" stroke-width="1"/>
  <text x="{level_badge_x + level_badge_w / 2}" y="{title_y - 1}" fill="{c['accent']}" font-family="{FONT}" font-size="11" font-weight="700" text-anchor="middle">Lv. {trainer['level']}</text>

  <text x="{CARD_PADDING}" y="{username_y}" fill="{c['text_muted']}" font-family="{FONT}" font-size="11">@{trainer['username']} — {trainer['levelLabel']}</text>

  {partner_icon}
  <text x="{CARD_PADDING + 26}" y="{partner_y}" fill="{c['text_primary']}" font-family="{FONT}" font-size="11">Partner • {trainer['partner']}</text>

  <text x="{CARD_PADDING}" y="{quest_y}" fill="{c['text_muted']}" font-family="{FONT}" font-size="10.5">Current Quest • {config.QUEST_TEXT}</text>

  <rect x="{CARD_PADDING}" y="{progress_y}" width="{PROGRESS_BAR_WIDTH}" height="5" rx="2.5" fill="{c['cell_empty']}"/>
  <rect x="{CARD_PADDING}" y="{progress_y}" width="{progress_fill_width}" height="5" rx="2.5" fill="{c['accent']}"/>
  <text x="{CARD_PADDING + PROGRESS_BAR_WIDTH + 10}" y="{progress_y + 5}" fill="{c['text_muted']}" font-family="{FONT}" font-size="10">{trainer['progressPercent']}% to next level</text>

  <line x1="{CARD_PADDING}" y1="{divider1_y}" x2="{right_edge}" y2="{divider1_y}" stroke="{c['card_border']}" stroke-width="1"/>

  {month_labels_svg}
  {weekday_labels_svg}
  {heatmap_svg}
  {legend_svg}

  <line x1="{CARD_PADDING}" y1="{divider2_y}" x2="{right_edge}" y2="{divider2_y}" stroke="{c['card_border']}" stroke-width="1"/>

  {footer_svg}
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
