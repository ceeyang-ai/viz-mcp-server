"""viz-mcp-server: Chart Generation MCP Server v0.1.0

Provides data visualization via MCP protocol:
- Bar charts, line charts, pie charts, scatter plots, histograms
- Returns SVG (inline) or PNG (file) output
- Supports customizable colors, labels, titles
"""

import io
import json
import os
import tempfile

import matplotlib
matplotlib.use("Agg")  # No display needed
import matplotlib.pyplot as plt
import numpy as np

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("viz-mcp-server")

# ─── Helpers ───────────────────────────────────────────────────────────

def _validate_data(values) -> list[float]:
    """Convert and validate numeric data."""
    return [float(v) for v in values]


def _validate_labels(labels, data_len: int) -> list[str] | None:
    """Return validated labels or None (auto-generated)."""
    if not labels or len(labels) == 0:
        return None
    labels = [str(l) for l in labels]
    if len(labels) != data_len:
        # Pad or truncate
        if len(labels) > data_len:
            labels = labels[:data_len]
        else:
            labels.extend([""] * (data_len - len(labels)))
    return labels


def _style_chart(ax, title: str | None, xlabel: str | None, ylabel: str | None):
    """Apply common styling to an axis."""
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _chart_to_svg(fig) -> str:
    """Render a matplotlib figure to SVG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", dpi=120)
    plt.close(fig)
    return buf.getvalue().decode("utf-8")


def _chart_to_file(fig, suffix: str = ".png") -> str:
    """Save a matplotlib figure to a temp file and return path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb"):
        pass
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return path


# ─── Color Palettes ───────────────────────────────────────────────────

PALETTES = {
    "default": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
                "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"],
    "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
                "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"],
    "pastel": ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#E8BAFF",
               "#FFD9BA", "#BAFFEC", "#FFC8BA", "#D4BAFF", "#BAF2FF"],
    "monochrome": ["#2C3E50", "#34495E", "#5D6D7E", "#85929E", "#AEB6BF",
                   "#D5DBDB", "#1A5276", "#2E86C1", "#5DADE2", "#A9CCE3"],
}

COLORS_LEN = 10


def _colors(palette: str = "default") -> list[str]:
    return PALETTES.get(palette, PALETTES["default"])


# ─── MCP Tools ────────────────────────────────────────────────────────


@mcp.tool()
def create_bar_chart(
    values: list[float],
    labels: list[str] | None = None,
    title: str = "Bar Chart",
    xlabel: str = "",
    ylabel: str = "",
    palette: str = "default",
    horizontal: bool = False,
    output: str = "svg",
) -> str:
    """Create a bar chart.

    Args:
        values: Numeric values for each bar
        labels: Category labels (optional, auto-generated if omitted)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        palette: Color palette: default, vibrant, pastel, monochrome
        horizontal: If True, render horizontal bars
        output: 'svg' for inline SVG string, 'png' for file path
    """
    data = _validate_data(values)
    lbls = _validate_labels(labels, len(data))
    if lbls is None:
        lbls = [f"Item {i+1}" for i in range(len(data))]

    fig, ax = plt.subplots(figsize=(8, max(4, len(data) * 0.35)))
    colors = _colors(palette)

    indices = np.arange(len(data))

    if horizontal:
        bars = ax.barh(indices, data, color=[colors[i % COLORS_LEN] for i in range(len(data))],
                       edgecolor="white", linewidth=0.5)
        ax.set_yticks(indices)
        ax.set_yticklabels(lbls)
        # Add value labels
        for i, bar in enumerate(bars):
            ax.text(bar.get_width() + max(data) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{data[i]:.1f}", va="center", fontsize=9)
    else:
        bars = ax.bar(indices, data, color=[colors[i % COLORS_LEN] for i in range(len(data))],
                      edgecolor="white", linewidth=0.5)
        ax.set_xticks(indices)
        ax.set_xticklabels(lbls, rotation=30, ha="right")
        for i, bar in enumerate(bars):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(data) * 0.01,
                    f"{data[i]:.1f}", ha="center", fontsize=9)

    _style_chart(ax, title, xlabel if not horizontal else ylabel,
                 ylabel if not horizontal else xlabel)

    if output == "png":
        path = _chart_to_file(fig)
        return json.dumps({"success": True, "file_path": path, "format": "png"})
    else:
        svg = _chart_to_svg(fig)
        return json.dumps({"success": True, "svg": svg, "format": "svg"})


@mcp.tool()
def create_line_chart(
    x_values: list[float],
    y_values: list[float],
    title: str = "Line Chart",
    xlabel: str = "",
    ylabel: str = "",
    palette: str = "default",
    show_points: bool = True,
    output: str = "svg",
) -> str:
    """Create a line chart.

    Args:
        x_values: X-axis data points
        y_values: Y-axis data points
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        palette: Color palette: default, vibrant, pastel, monochrome
        show_points: Show data point markers
        output: 'svg' for inline SVG, 'png' for file path
    """
    x = _validate_data(x_values)
    y = _validate_data(y_values)
    if len(x) != len(y):
        return json.dumps({"success": False, "error": f"x_values ({len(x)}) and y_values ({len(y)}) must have same length"})

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = _colors(palette)

    marker = "o" if show_points else ""
    ax.plot(x, y, color=colors[0], marker=marker, linewidth=2, markersize=6,
            markerfacecolor=colors[0], markeredgecolor="white", markeredgewidth=1)

    _style_chart(ax, title, xlabel, ylabel)
    ax.fill_between(x, y, alpha=0.08, color=colors[0])

    if output == "png":
        path = _chart_to_file(fig)
        return json.dumps({"success": True, "file_path": path, "format": "png"})
    else:
        svg = _chart_to_svg(fig)
        return json.dumps({"success": True, "svg": svg, "format": "svg"})


@mcp.tool()
def create_pie_chart(
    values: list[float],
    labels: list[str] | None = None,
    title: str = "Pie Chart",
    palette: str = "default",
    show_percent: bool = True,
    output: str = "svg",
) -> str:
    """Create a pie / donut chart.

    Args:
        values: Numeric values (proportions)
        labels: Slice labels (optional)
        title: Chart title
        palette: Color palette: default, vibrant, pastel, monochrome
        show_percent: Show percentage labels on slices
        output: 'svg' for inline SVG, 'png' for file path
    """
    data = _validate_data(values)
    lbls = _validate_labels(labels, len(data))
    colors = _colors(palette)

    fig, ax = plt.subplots(figsize=(7, 7))

    wedges, texts, autotexts = ax.pie(
        data,
        labels=lbls,
        autopct="%1.1f%%" if show_percent else None,
        startangle=90,
        colors=[colors[i % COLORS_LEN] for i in range(len(data))],
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        pctdistance=0.75,
    )
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=16)

    # Equal aspect ratio ensures circle
    ax.axis("equal")

    if output == "png":
        path = _chart_to_file(fig)
        return json.dumps({"success": True, "file_path": path, "format": "png"})
    else:
        svg = _chart_to_svg(fig)
        return json.dumps({"success": True, "svg": svg, "format": "svg"})


@mcp.tool()
def create_scatter_plot(
    x_values: list[float],
    y_values: list[float],
    labels: list[str] | None = None,
    title: str = "Scatter Plot",
    xlabel: str = "",
    ylabel: str = "",
    palette: str = "default",
    regression_line: bool = False,
    output: str = "svg",
) -> str:
    """Create a scatter plot.

    Args:
        x_values: X data points
        y_values: Y data points
        labels: Optional point labels (for hover)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        palette: Color palette: default, vibrant, pastel, monochrome
        regression_line: Show trend line
        output: 'svg' for inline SVG, 'png' for file path
    """
    x = _validate_data(x_values)
    y = _validate_data(y_values)
    if len(x) != len(y):
        return json.dumps({"success": False, "error": "x_values and y_values must have same length"})

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = _colors(palette)

    ax.scatter(x, y, c=colors[0], s=50, alpha=0.75, edgecolors="white", linewidth=0.5, zorder=3)

    if regression_line and len(x) > 1:
        coefs = np.polyfit(x, y, 1)
        poly = np.poly1d(coefs)
        x_sorted = np.linspace(min(x), max(x), 100)
        ax.plot(x_sorted, poly(x_sorted), color=colors[1], linewidth=1.5,
                linestyle="--", alpha=0.7, label=f"Trend (y={coefs[0]:.2f}x+{coefs[1]:.2f})")
        ax.legend(frameon=False)

    _style_chart(ax, title, xlabel, ylabel)

    if output == "png":
        path = _chart_to_file(fig)
        return json.dumps({"success": True, "file_path": path, "format": "png"})
    else:
        svg = _chart_to_svg(fig)
        return json.dumps({"success": True, "svg": svg, "format": "svg"})


@mcp.tool()
def create_histogram(
    values: list[float],
    bins: int = 10,
    title: str = "Histogram",
    xlabel: str = "",
    ylabel: str = "Frequency",
    palette: str = "default",
    cumulative: bool = False,
    output: str = "svg",
) -> str:
    """Create a histogram.

    Args:
        values: Numeric data points
        bins: Number of bins (default: 10)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        palette: Color palette: default, vibrant, pastel, monochrome
        cumulative: Show cumulative distribution
        output: 'svg' for inline SVG, 'png' for file path
    """
    data = _validate_data(values)
    colors = _colors(palette)
    bins = max(2, min(bins, 100))

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(data, bins=bins, color=colors[0], edgecolor="white", linewidth=0.8,
            alpha=0.8, cumulative=cumulative)

    _style_chart(ax, title, xlabel, ylabel)

    # Add mean line
    mean_val = np.mean(data)
    ax.axvline(mean_val, color=colors[1], linestyle="--", linewidth=1.5,
               alpha=0.8, label=f"Mean: {mean_val:.1f}")
    ax.legend(frameon=False, loc="upper right")

    if output == "png":
        path = _chart_to_file(fig)
        return json.dumps({"success": True, "file_path": path, "format": "png"})
    else:
        svg = _chart_to_svg(fig)
        return json.dumps({"success": True, "svg": svg, "format": "svg"})


# ─── Entry Point ───────────────────────────────────────────────────────


def main():
    mcp.run()


if __name__ == "__main__":
    main()
