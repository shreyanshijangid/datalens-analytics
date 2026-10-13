"""
DataLens - Modern Power BI Light Mode Styling Engine
Clean, crisp white dashboard design system inspired by Power BI and Tableau.
"""

import streamlit as st
import plotly.graph_objects as go

# Power BI Theme Palette
COLOR_PBI_BLUE = "#11548a"
COLOR_PRIMARY = "#2563eb"       # Royal Blue
COLOR_SECONDARY = "#0ea5e9"     # Sky Blue
COLOR_EMERALD = "#10b981"       # Emerald
COLOR_AMBER = "#f59e0b"         # Amber
COLOR_PURPLE = "#8b5cf6"        # Violet
COLOR_ROSE = "#f43f5e"          # Rose
COLOR_DARK = "#0f172a"          # Slate 900
COLOR_MUTED = "#64748b"         # Slate 500

PBI_PALETTE = [
    "#2563eb",  # Power BI Blue
    "#0284c7",  # Sky
    "#10b981",  # Emerald
    "#f59e0b",  # Amber
    "#8b5cf6",  # Violet
    "#ec4899",  # Pink
    "#06b6d4",  # Cyan
    "#f97316",  # Orange
]


def get_light_css() -> str:
    """Returns crisp, modern Power BI dashboard CSS for Streamlit."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global reset & Canvas */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #f1f5f9 !important;
        background-image: none !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}

    /* Main Container */
    .main .block-container {{
        max-width: 1450px !important;
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}

    /* Hide standard Streamlit header, footer, decoration */
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{
        visibility: hidden !important;
        display: none !important;
    }}

    /* Modern Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
    }}

    h1 {{
        font-size: 1.75rem !important;
        margin: 0 !important;
    }}

    h2 {{
        font-size: 1.25rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }}

    h3 {{
        font-size: 1.05rem !important;
        color: #1e293b !important;
        font-weight: 600 !important;
    }}

    /* Power BI Top Navigation Banner */
    .pbi-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}

    .pbi-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .pbi-icon {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 800;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
    }}

    /* Power BI KPI Scorecards Grid */
    .pbi-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.9rem;
        margin-bottom: 1.2rem;
    }}

    .pbi-kpi-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .pbi-kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.06);
    }}

    .pbi-kpi-bar {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }}

    .pbi-kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 0.25rem;
    }}

    .pbi-kpi-value {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }}

    .pbi-kpi-subtext {{
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.3rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }}

    /* Power BI Visual Card Container */
    .pbi-visual-card,
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 1.1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    }}

    .pbi-visual-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }}

    .pbi-visual-title {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .pbi-badge {{
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 4px;
        background: #f1f5f9;
        color: #475569;
    }}

    /* Slicer Filter Bar */
    .pbi-slicer-bar {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}

    /* Streamlit Button Styling */
    div.stButton > button {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.15s ease !important;
        width: 100%;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35) !important;
        color: #ffffff !important;
    }}

    /* Download Button */
    div.stDownloadButton > button {{
        background: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        width: 100%;
    }}

    div.stDownloadButton > button:hover {{
        background: #eff6ff !important;
        border-color: #2563eb !important;
    }}

    /* Selectboxes and Inputs */
    div[data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        font-size: 0.88rem !important;
    }}

    div[data-baseweb="select"]:hover > div {{
        border-color: #2563eb !important;
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 7px;
        height: 7px;
    }}
    ::-webkit-scrollbar-track {{
        background: #f1f5f9;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #cbd5e1;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #94a3b8;
    }}
    </style>
    """


def render_pbi_header(dataset_name: str, row_count: int, col_count: int):
    """Renders the top Power BI report header banner."""
    header_html = (
        f'<div class="pbi-header">'
        f'<div class="pbi-brand">'
        f'<div class="pbi-icon">📊</div>'
        f'<div>'
        f'<h1 style="font-size: 1.5rem; color: #0f172a; margin: 0; line-height: 1.2;">'
        f'DataLens <span style="font-size: 1rem; color: #64748b; font-weight: 500;">// Power BI Executive Studio</span>'
        f'</h1>'
        f'<div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">'
        f'Single-Page Interactive Telemetry Dashboard • Data Visualization Lab'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<span class="pbi-badge" style="background: #eff6ff; color: #1d4ed8; font-weight: 600; padding: 4px 10px;">'
        f'📂 Active: {dataset_name}'
        f'</span>'
        f'<span class="pbi-badge" style="background: #ecfdf5; color: #047857; font-weight: 600; padding: 4px 10px;">'
        f'⚡ {row_count:,} Rows × {col_count} Cols'
        f'</span>'
        f'</div>'
        f'</div>'
    )
    if hasattr(st, "html"):
        st.html(header_html)
    else:
        st.markdown(header_html, unsafe_allow_html=True)


def render_pbi_kpis(kpis: list):
    """Renders the top Power BI scorecard KPI row.

    kpis: list of dicts with keys: label, value, subtext, color
    """
    card_items = []
    for k in kpis:
        color = k.get("color", COLOR_PRIMARY)
        label = k.get("label", "")
        value = k.get("value", "")
        subtext = k.get("subtext", "")
        card_items.append(
            f'<div class="pbi-kpi-card">'
            f'<div class="pbi-kpi-bar" style="background: {color};"></div>'
            f'<div class="pbi-kpi-label">{label}</div>'
            f'<div class="pbi-kpi-value">{value}</div>'
            f'<div class="pbi-kpi-subtext">{subtext}</div>'
            f'</div>'
        )
    html_content = f'<div class="pbi-kpi-grid">{"".join(card_items)}</div>'
    if hasattr(st, "html"):
        st.html(html_content)
    else:
        st.markdown(html_content, unsafe_allow_html=True)


def apply_pbi_theme(fig: go.Figure, height: int = 380) -> go.Figure:
    """Applies a crisp Power BI styling theme to Plotly charts."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(
            family="Plus Jakarta Sans, Inter, sans-serif",
            size=11,
            color="#334155"
        ),
        title_font=dict(
            family="Plus Jakarta Sans, sans-serif",
            size=14,
            color="#0f172a",
        ),
        margin=dict(l=40, r=20, t=35, b=35),
        height=height,
        colorway=PBI_PALETTE,
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#0f172a",
            font=dict(family="Inter", size=11, color="#ffffff")
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(family="Inter", size=10, color="#475569")
        ),
    )

    fig.update_xaxes(
        gridcolor="#f1f5f9",
        zerolinecolor="#e2e8f0",
        linecolor="#cbd5e1",
        tickfont=dict(family="Inter", size=10, color="#64748b"),
        title_font=dict(family="Plus Jakarta Sans", size=11, color="#0f172a")
    )
    fig.update_yaxes(
        gridcolor="#f1f5f9",
        zerolinecolor="#e2e8f0",
        linecolor="#cbd5e1",
        tickfont=dict(family="Inter", size=10, color="#64748b"),
        title_font=dict(family="Plus Jakarta Sans", size=11, color="#0f172a")
    )
    return fig


# Backwards compatibility aliases
get_hud_css = get_light_css
render_light_header = render_pbi_header
render_metric_cards = render_pbi_kpis
apply_light_theme = apply_pbi_theme
