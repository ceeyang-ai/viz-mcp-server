# Viz MCP Server 📊

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A **Model Context Protocol (MCP)** server for data visualization — generate bar charts, line charts, pie charts, scatter plots, and histograms. Returns SVG (inline) or PNG (file).

> Built for AI agents. Works with **Hermes Agent**, **Claude Code**, **Cursor**, and any MCP-compatible client.

## ✨ Features

| Tool | Description |
|------|-------------|
| `create_bar_chart` | Bar chart (vertical/horizontal) with value labels |
| `create_line_chart` | Line chart with area fill, markers, trend |
| `create_pie_chart` | Pie/donut chart with percentage labels |
| `create_scatter_plot` | Scatter plot with optional regression line |
| `create_histogram` | Histogram with mean line, optional cumulative |

**All tools support:**
- 4 color palettes: `default`, `vibrant`, `pastel`, `monochrome`
- SVG output (inline for MCP response) or PNG output (saved to file)
- Custom titles, axis labels
- Clean matplotlib styling (no chartjunk)

## 🚀 Quick Start

```bash
# Install from GitHub
pip install git+https://github.com/ceeyang-ai/viz-mcp-server.git

# Run as MCP server
viz-mcp-server
```

## 🔌 Usage with Hermes Agent

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  viz:
    command: "viz-mcp-server"
```

Restart Hermes → tools available as `mcp_viz_create_bar_chart`, etc.

## 📖 Examples

### Bar Chart

```python
# Via MCP tool call
result = create_bar_chart(
    values=[10, 25, 15, 30, 20],
    labels=["Q1", "Q2", "Q3", "Q4", "Q5"],
    title="Quarterly Revenue",
    ylabel="Revenue ($K)",
    palette="vibrant"
)
```

### Scatter with Trend Line

```python
result = create_scatter_plot(
    x_values=[1, 2, 3, 4, 5, 6, 7, 8],
    y_values=[2, 3, 5, 7, 11, 13, 17, 19],
    title="Growth Analysis",
    regression_line=True
)
```

### Histogram

```python
result = create_histogram(
    values=[12, 15, 13, 20, 19, 18, 14, 16, 22, 25, 21, 17],
    bins=8,
    title="Score Distribution",
    xlabel="Score"
)
```

## 🛠 Requirements

- Python 3.10+
- matplotlib ≥ 3.7
- numpy ≥ 1.24
- mcp ≥ 1.0

## 👨‍💻 Development

```bash
git clone https://github.com/ceeyang-ai/viz-mcp-server.git
cd viz-mcp-server
pip install -e .
viz-mcp-server  # Start MCP server
```

## 📄 License

MIT
