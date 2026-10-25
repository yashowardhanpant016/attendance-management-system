import matplotlib.pyplot as plt

def generate_pareto_chart():
    defects = [
        "Visual Contrast / Illegibility",
        "Missing Focus Ring",
        "Layout Clutter",
        "Font Resizing Overflow",
        "Duplicate Submission",
        "SQLite Lock / Delay"
    ]
    counts = [27, 20, 12, 8, 5, 3]

    cumulative_percentages = []
    total = sum(counts)
    running_sum = 0
    for count in counts:
        running_sum += count
        cumulative_percentages.append((running_sum / total) * 100)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for defect frequencies
    bars = ax1.bar(defects, counts, color="#2b5c8f", edgecolor="black", width=0.55)
    ax1.set_xlabel("Defect Classification Categories", fontweight="bold", labelpad=10)
    ax1.set_ylabel("Defect Frequency (Count)", color="#2b5c8f", fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#2b5c8f")
    plt.xticks(rotation=20, ha="right")

    # Secondary axis for cumulative percentage (Pareto curve)
    ax2 = ax1.twinx()
    ax2.plot(defects, cumulative_percentages, color="#c0392b", marker="D", linewidth=2.5, markersize=7)
    ax2.set_ylabel("Cumulative Percentage (%)", color="#c0392b", fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#c0392b")
    ax2.set_ylim(0, 110)

    # 80/20 threshold line
    ax2.axhline(80, color="gray", linestyle="--", linewidth=1.5, label="80% Cutoff Line")
    ax2.legend(loc="center right")

    plt.title("Pareto Analysis (80/20 Rule) - Defect Distribution [Q12 Accessibility]", fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("pareto_analysis_q12.png", dpi=300)
    print("Pareto chart successfully generated: pareto_analysis_q12.png")

if __name__ == "__main__":
    generate_pareto_chart()
