# Trainer Journey configuration
# This is the only file you should need to edit to personalize your card.

# Rolling window used to measure consistency — roughly one semester.
# Level is based on how many of the last N weeks had at least one contribution,
# NOT on lifetime totals. This keeps the metric fair regardless of how long
# your GitHub history is.
ROLLING_WINDOW_WEEKS = 16

# Level bands, based on % of the rolling window that was active.
# (lower_bound_pct, upper_bound_pct, label)
LEVEL_THRESHOLDS = [
    (0, 19.999, "Novice"),
    (20, 39.999, "Trainee"),
    (40, 59.999, "Committed"),
    (60, 79.999, "Consistent"),
    (80, 100, "Dedicated"),
]

PARTNER_NAME = "Porygon"

# Monochromatic blue palette, dark background — no greens, no gradients.
COLORS = {
    "background": "#0d1117",
    "card_border": "#1e2a38",
    "text_primary": "#e6f1fb",
    "text_muted": "#5f6b7a",
    "accent": "#378ADD",
    "cell_empty": "#161b22",
    "cell_low": "#0e3a5f",
    "cell_medium": "#155a8a",
    "cell_high": "#1f7bc4",
    "cell_max": "#378ADD",
}
