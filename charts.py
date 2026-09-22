"""Radar chart generation using Matplotlib for interview score visualizations (Dark Theme)."""

import io
import math
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
import matplotlib.pyplot as plt
import numpy as np


def make_radar_chart(avg_scores: dict[str, float]) -> bytes:
    """
    Generates a high-resolution radar (spider) chart of the candidate's average
    performance across the 4 core dimensions: Relevance, Depth, Structure, Clarity.
    Uses a dark theme matching the app's premium UI.

    Args:
        avg_scores: Dictionary containing keys 'relevance', 'depth', 'structure', 'clarity'.

    Returns:
        bytes: PNG image data in bytes.
    """
    categories = ["Relevance", "Depth", "Structure", "Clarity"]
    scores = [
        float(avg_scores.get("relevance", 0)),
        float(avg_scores.get("depth", 0)),
        float(avg_scores.get("structure", 0)),
        float(avg_scores.get("clarity", 0)),
    ]

    # Number of variables
    num_vars = len(categories)

    # Compute angle for each axis
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]
    # Close the polygon loop
    scores_loop = scores + [scores[0]]
    angles_loop = angles + [angles[0]]

    # Dark theme colors
    bg_color = "#0a122a"
    plot_bg = "#131a33"
    grid_color = "#2c344d"
    spine_color = "#404752"
    text_color = "#dbe1ff"
    label_color = "#c0c7d4"
    primary_blue = "#a3c9ff"
    fill_blue = "#0078d4"
    accent_green = "#4edea3"
    accent_amber = "#ffb95f"

    # Initialize plot with dark styling
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=200)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(plot_bg)

    # Draw one axe per variable + add labels
    plt.xticks(
        angles,
        categories,
        color=text_color,
        size=12,
        fontweight="bold",
    )

    # Set y-axis ticks and limits (0 to 10 scale)
    ax.set_rlabel_position(45)
    plt.yticks(
        [2, 4, 6, 8, 10],
        ["2", "4", "6", "8", "10"],
        color=label_color,
        size=9,
    )
    plt.ylim(0, 10)

    # Gridline & Spine styling
    ax.grid(color=grid_color, linestyle="--", linewidth=0.8, alpha=0.8)
    ax.spines["polar"].set_color(spine_color)
    ax.spines["polar"].set_linewidth(1.2)

    # Plot data
    ax.plot(
        angles_loop,
        scores_loop,
        color=primary_blue,
        linewidth=2.5,
        linestyle="solid",
        marker="o",
        markersize=8,
        markerfacecolor=accent_green,
        markeredgecolor=bg_color,
        markeredgewidth=2,
        label="Candidate Score",
    )

    # Fill area with gradient-like effect
    ax.fill(angles_loop, scores_loop, color=fill_blue, alpha=0.25)

    # Add score annotations near vertices
    vertex_colors = [accent_green, accent_amber, primary_blue, accent_green]
    for angle, score, cat, v_color in zip(angles, scores, categories, vertex_colors):
        x = angle
        y = min(score + 0.8, 9.8) if score > 1 else score + 1.0
        ax.text(
            x,
            y,
            f"{score:.1f}",
            color=text_color,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="#212942",
                edgecolor=v_color,
                alpha=0.95,
                linewidth=1.5,
            ),
        )

    # Title
    plt.title(
        "Performance Radar (Scale 1 – 10)",
        size=14,
        color=text_color,
        fontweight="bold",
        pad=20,
    )

    # Tick label colors and padding
    ax.tick_params(colors=text_color, pad=25)

    plt.tight_layout()

    # Save to in-memory bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
