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
QUEST_TEXT = "Shipping full-stack + GenAI projects"

# Monochromatic blue palette, dark background — vibrant top tier, clearly
# stepped so each activity level reads distinctly at a glance.
COLORS = {
    "background": "#0b0f17",
    "card_border": "#1e2a3a",
    "text_primary": "#eaf3fc",
    "text_muted": "#7a8699",
    "accent": "#4DA8FF",
    "cell_empty": "#151b25",
    "cell_low": "#173d61",
    "cell_medium": "#1c5c92",
    "cell_high": "#2f8fd1",
    "cell_max": "#5fc1ff",
}
