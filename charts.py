"""Radar chart generation using Matplotlib for interview score visualizations."""

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

    # Initialize plot with modern styling
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=200)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    # Draw one axe per variable + add labels
    plt.xticks(
        angles,
        categories,
        color="#1E293B",
        size=12,
        fontweight="bold",
    )

    # Set y-axis ticks and limits (0 to 10 scale)
    ax.set_rlabel_position(45)
    plt.yticks(
        [2, 4, 6, 8, 10],
        ["2", "4", "6", "8", "10"],
        color="#64748B",
        size=9,
    )
    plt.ylim(0, 10)

    # Gridline & Spine styling
    ax.grid(color="#CBD5E1", linestyle="--", linewidth=0.8, alpha=0.8)
    ax.spines["polar"].set_color("#94A3B8")
    ax.spines["polar"].set_linewidth(1.2)

    # Plot data
    ax.plot(
        angles_loop,
        scores_loop,
        color="#2563EB",
        linewidth=2.5,
        linestyle="solid",
        marker="o",
        markersize=7,
        markerfacecolor="#1D4ED8",
        markeredgecolor="#FFFFFF",
        markeredgewidth=1.5,
        label="Candidate Score",
    )

    # Fill area
    ax.fill(angles_loop, scores_loop, color="#3B82F6", alpha=0.25)

    # Add score annotations near vertices
    for angle, score, cat in zip(angles, scores, categories):
        x = angle
        y = min(score + 0.6, 9.8) if score > 1 else score + 0.8
        ax.text(
            x,
            y,
            f"{score:.1f}",
            color="#1E3A8A",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#EFF6FF", edgecolor="#BFDBFE", alpha=0.9),
        )

    # Title
    plt.title(
        "Performance Radar (Scale 1 - 10)",
        size=14,
        color="#0F172A",
        fontweight="bold",
        pad=20,
    )

    plt.tight_layout()

    # Save to in-memory bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor(), dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
