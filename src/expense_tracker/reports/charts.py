import io
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_pie_chart(by_category: list[tuple[str, str, Decimal]]) -> bytes:
    if not by_category:
        return b""

    labels = [f"{emoji} {name}" for name, emoji, _ in by_category]
    sizes = [float(amount) for _, _, amount in by_category]
    colors = [
        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
        "#FF9F40", "#FF6384", "#C9CBCF", "#7BC225", "#E7E9ED",
        "#845EC2", "#D65DB1", "#FF6F91", "#FF9671", "#FFC75F",
    ][:len(labels)]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        pctdistance=0.85,
    )

    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig.gca().add_artist(centre_circle)
    ax.set_title("Expenses by Category", fontsize=14, fontweight="bold", pad=20)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def generate_bar_chart(daily_totals: list[tuple[int, Decimal]], month_name: str) -> bytes:
    if not daily_totals:
        return b""

    days = [d for d, _ in daily_totals]
    amounts = [float(a) for _, a in daily_totals]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(days, amounts, color="#36A2EB", edgecolor="white", linewidth=0.5)

    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${height:.0f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )

    ax.set_xlabel("Day of Month", fontsize=11)
    ax.set_ylabel("Amount ($)", fontsize=11)
    ax.set_title(f"Daily Expenses - {month_name}", fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
