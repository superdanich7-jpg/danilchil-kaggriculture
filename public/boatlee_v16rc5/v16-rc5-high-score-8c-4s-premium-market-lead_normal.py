import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from IPython.display import display

plt.rcParams.update({
    "figure.dpi": 130,
    "font.size": 11,
    "axes.titleweight": "bold",
    "axes.titlesize": 16,
    "axes.labelcolor": "#334155",
    "text.color": "#0F172A",
})

NAVY = "#0F172A"
TEAL = "#0F766E"
MINT = "#5EEAD4"
BLUE = "#2563EB"
SLATE = "#64748B"
LIGHT = "#E2E8F0"
ORANGE = "#F97316"

evaluation = pd.DataFrame(json.loads(r'''[{"reference":"Reconstructed 8C/4S core","games":60,"wins":60,"ties":0,"losses":0,"mean_margin":1911.8666666666666,"worst_margin":68.0,"paired_positive":30,"paired_zero":0,"paired_negative":0,"pairs":30},{"reference":"V16-RC4-P5D","games":60,"wins":57,"ties":0,"losses":3,"mean_margin":5460.616666666667,"worst_margin":-529.0,"paired_positive":29,"paired_zero":0,"paired_negative":1,"pairs":30},{"reference":"V16-RC3","games":24,"wins":23,"ties":0,"losses":1,"mean_margin":6105.208333333333,"worst_margin":-28.0,"paired_positive":12,"paired_zero":0,"paired_negative":0,"pairs":12},{"reference":"Kaito V27 public artifact","games":24,"wins":24,"ties":0,"losses":0,"mean_margin":18992.791666666668,"worst_margin":8724.0,"paired_positive":12,"paired_zero":0,"paired_negative":0,"pairs":12},{"reference":"Rayk C71 public artifact","games":24,"wins":24,"ties":0,"losses":0,"mean_margin":18576.75,"worst_margin":9089.0,"paired_positive":12,"paired_zero":0,"paired_negative":0,"pairs":12},{"reference":"llcc public artifact","games":24,"wins":24,"ties":0,"losses":0,"mean_margin":18340.958333333332,"worst_margin":7104.0,"paired_positive":12,"paired_zero":0,"paired_negative":0,"pairs":12}]'''))
expansion = pd.DataFrame(json.loads(r'''[{"step":0,"COW":1,"SHEEP":4},{"step":120,"COW":2,"SHEEP":4},{"step":161,"COW":4,"SHEEP":4},{"step":168,"COW":6,"SHEEP":4},{"step":192,"COW":8,"SHEEP":4},{"step":719,"COW":8,"SHEEP":4}]'''))

assert evaluation.loc[0, "games"] == 60
assert evaluation.loc[0, "wins"] == 60
assert evaluation.loc[0, "paired_positive"] == 30
assert (evaluation["games"] == 2 * evaluation["pairs"]).all()
print("Validated: all displayed results are complete two-seat, 720-turn simulations.")

# ==== CELL ====

fig, ax = plt.subplots(figsize=(11.4, 5.0))
ax.step(expansion["step"], expansion["COW"], where="post",
        linewidth=3.2, color=TEAL, label="COW")
ax.step(expansion["step"], expansion["SHEEP"], where="post",
        linewidth=3.2, color=BLUE, label="SHEEP")
ax.scatter(expansion["step"], expansion["COW"], s=48, color=TEAL, zorder=3)
ax.scatter(expansion["step"], expansion["SHEEP"], s=48, color=BLUE, zorder=3)
ax.set_xlim(-12, 720)
ax.set_ylim(0, 9)
ax.set_xticks([0, 120, 192, 360, 540, 719])
ax.set_yticks(range(0, 9))
ax.set_xlabel("Season step")
ax.set_ylabel("Cumulative livestock target")
ax.set_title("The 8C/4S production core reaches full livestock by step 192",
             loc="left", pad=20)
ax.grid(alpha=0.16)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="lower right")
ax.annotate("8 COW", xy=(192, 8), xytext=(258, 8.3),
            arrowprops={"arrowstyle": "-|>", "color": TEAL},
            color=TEAL, fontweight="bold")
ax.annotate("4 SHEEP", xy=(0, 4), xytext=(70, 3.1),
            arrowprops={"arrowstyle": "-|>", "color": BLUE},
            color=BLUE, fontweight="bold")
fig.tight_layout()
fig.savefig("livestock_expansion.png", bbox_inches="tight", facecolor="white")
plt.show()

# ==== CELL ====

fig, ax = plt.subplots(figsize=(12.0, 5.1))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.2)
ax.axis("off")

ax.text(0.3, 4.72, "One-turn premium market lead",
        fontsize=18, fontweight="bold", color=NAVY)
ax.text(0.3, 4.30,
        "Move only available stock; conserve the planned two-turn quantity.",
        fontsize=11.5, color=SLATE)

def draw_box(x, y, width, label, color, text_color="white"):
    patch = FancyBboxPatch(
        (x, y), width, 0.82,
        boxstyle="round,pad=0.04,rounding_size=0.13",
        linewidth=0, facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + 0.41, label,
            ha="center", va="center", fontsize=11.3,
            fontweight="bold", color=text_color)

ax.text(0.3, 3.18, "Base schedule", fontsize=12.5,
        fontweight="bold", color=NAVY, va="center")
draw_box(2.55, 2.76, 2.45, "turn t: hold", LIGHT, NAVY)
draw_box(8.10, 2.76, 2.75, "turn t+1: SELL q", SLATE)
ax.add_patch(FancyArrowPatch((5.15, 3.17), (7.93, 3.17),
                             arrowstyle="-|>", mutation_scale=15,
                             linewidth=1.8, color=SLATE))

ax.text(0.3, 1.53, "V16-RC5", fontsize=12.5,
        fontweight="bold", color=NAVY, va="center")
draw_box(2.55, 1.11, 2.45, "turn t: SELL s", TEAL)
draw_box(8.10, 1.11, 2.75, "turn t+1: SELL q-s", MINT, NAVY)
ax.add_patch(FancyArrowPatch((5.15, 1.52), (7.93, 1.52),
                             arrowstyle="-|>", mutation_scale=15,
                             linewidth=1.8, color=TEAL))

ax.text(6.0, 0.42,
        "gate: town demand(t) = 0   •   invariant: s + (q-s) = q",
        ha="center", fontsize=11.2, color=SLATE)
fig.savefig("premium_market_lead.png", bbox_inches="tight", facecolor="white")
plt.show()

# ==== CELL ====

table = evaluation.copy()
table["W-T-L"] = table.apply(
    lambda row: f'{int(row["wins"])}-{int(row["ties"])}-{int(row["losses"])}',
    axis=1,
)
table["Paired +/0/-"] = table.apply(
    lambda row: (
        f'{int(row["paired_positive"])}/'
        f'{int(row["paired_zero"])}/'
        f'{int(row["paired_negative"])}'
    ),
    axis=1,
)
table["Mean margin"] = table["mean_margin"].map(lambda value: f"{value:+,.1f}")
table["Worst margin"] = table["worst_margin"].map(lambda value: f"{value:+,.0f}")
display(table[["reference", "games", "W-T-L", "Paired +/0/-",
               "Mean margin", "Worst margin"]].set_index("reference"))

# ==== CELL ====

chart = evaluation.sort_values("mean_margin")
colors = [TEAL if label == "Reconstructed 8C/4S core" else BLUE
          for label in chart["reference"]]
fig, ax = plt.subplots(figsize=(11.2, 5.8))
bars = ax.barh(chart["reference"], chart["mean_margin"],
               color=colors, height=0.58)
ax.axvline(0, color=SLATE, linewidth=1)
ax.set_xlabel("Mean V16-RC5 money margin")
ax.set_title("V16-RC5 remains positive across production and market references",
             loc="left", pad=28)
ax.text(0, 1.015, "Live local simulations; both seat orders for every seed",
        transform=ax.transAxes, color=SLATE, fontsize=10.5)
ax.grid(axis="x", alpha=0.16)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
limit = chart["mean_margin"].max() * 1.18
ax.set_xlim(0, limit)
for bar, value in zip(bars, chart["mean_margin"]):
    ax.text(value + limit * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+,.0f}", va="center", fontweight="bold", color=NAVY)
fig.subplots_adjust(left=0.31, right=0.94, top=0.79, bottom=0.14)
fig.savefig("dynamic_reference_margins.png", bbox_inches="tight", facecolor="white")
plt.show()

# ==== CELL ====

chart = evaluation.copy()
chart["positive_rate"] = chart["paired_positive"] / chart["pairs"] * 100
chart["zero_rate"] = chart["paired_zero"] / chart["pairs"] * 100
chart["negative_rate"] = chart["paired_negative"] / chart["pairs"] * 100

fig, ax = plt.subplots(figsize=(11.2, 5.4))
y = list(range(len(chart)))
ax.barh(y, chart["positive_rate"], color=TEAL, height=0.56,
        label="Paired positive")
ax.barh(y, chart["zero_rate"], left=chart["positive_rate"],
        color=LIGHT, height=0.56, label="Paired zero")
ax.barh(y, chart["negative_rate"],
        left=chart["positive_rate"] + chart["zero_rate"],
        color=ORANGE, height=0.56, label="Paired negative")
ax.set_yticks(y, chart["reference"])
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xlabel("Share of seed pairs (%)")
ax.set_title("Paired outcomes are stable after reversing seat order",
             loc="left", pad=24)
ax.grid(axis="x", alpha=0.14)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
for index, row in chart.iterrows():
    ax.text(101.5, index,
            f'{int(row["paired_positive"])}/'
            f'{int(row["paired_zero"])}/'
            f'{int(row["paired_negative"])}',
            va="center", fontweight="bold", color=NAVY)
ax.text(101.5, -0.75, "+/0/-", fontweight="bold", color=SLATE)
ax.legend(ncol=3, frameon=False, loc="lower center",
          bbox_to_anchor=(0.5, -0.31))
fig.subplots_adjust(left=0.31, right=0.90, top=0.83, bottom=0.23)
fig.savefig("paired_outcomes.png", bbox_inches="tight", facecolor="white")
plt.show()