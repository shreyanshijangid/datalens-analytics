"""
DataLens - Power BI Visuals Engine
Generates interactive charts tailored for single-page executive dashboards,
including Geographic Maps, Correlation Heatmaps, Distribution Curves, and Cohort Analytics.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.style import (
    apply_pbi_theme,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_EMERALD,
    COLOR_AMBER,
    COLOR_PURPLE,
    PBI_PALETTE,
)


def detect_geo_columns(df: pd.DataFrame) -> Optional[Tuple[str, str]]:
    """Detects latitude and longitude columns in dataframe."""
    col_map = {c.lower().strip(): c for c in df.columns}
    lat_col = next((col_map[k] for k in ["latitude", "lat", "lat_deg"] if k in col_map), None)
    lon_col = next((col_map[k] for k in ["longitude", "lon", "lng", "long", "lon_deg"] if k in col_map), None)

    if lat_col and lon_col:
        return lat_col, lon_col
    return None


def create_geo_map(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    max_points: int = 1500
) -> go.Figure:
    """Builds an interactive geographic map visual for Power BI dashboard."""
    plot_df = df.dropna(subset=[lat_col, lon_col]).copy()
    if len(plot_df) > max_points:
        plot_df = plot_df.sample(max_points, random_state=42)

    try:
        fig = px.scatter_map(
            plot_df,
            lat=lat_col,
            lon=lon_col,
            color=color_col if color_col in plot_df.columns else None,
            size=size_col if size_col in plot_df.columns and plot_df[size_col].min() >= 0 else None,
            color_continuous_scale="Viridis",
            size_max=10,
            zoom=5,
            map_style="open-street-map",
            title=f"Geographic Spatial Distribution ({lat_col} × {lon_col})"
        )
    except Exception:
        # Fallback to high-speed 2D spatial scatter
        fig = px.scatter(
            plot_df,
            x=lon_col,
            y=lat_col,
            color=color_col if color_col in plot_df.columns else None,
            color_continuous_scale="Viridis",
            title=f"Geographic Coordinate Map ({lat_col} vs {lon_col})",
            opacity=0.75
        )
        fig.update_traces(marker=dict(size=5))

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(
            title=color_col or "Value",
            thickness=12,
            len=0.7
        )
    )
    return apply_pbi_theme(fig, height=380)


def create_distribution_curve(df: pd.DataFrame, col: str) -> go.Figure:
    """Builds a Power BI histogram with density curve and mean/median markers."""
    clean_series = df[col].dropna()
    mean_val = float(clean_series.mean())
    median_val = float(clean_series.median())

    fig = px.histogram(
        df,
        x=col,
        marginal="box",
        nbins=40,
        title=f"Distribution Profile // {col}",
        color_discrete_sequence=[COLOR_PRIMARY],
        opacity=0.82
    )

    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="#dc2626",
        line_width=1.5,
        annotation_text=f"Mean: {mean_val:.2f}",
        annotation_position="top right",
        annotation_font=dict(family="Inter", size=10, color="#dc2626")
    )

    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_color=COLOR_EMERALD,
        line_width=1.5,
        annotation_text=f"Median: {median_val:.2f}",
        annotation_position="top left",
        annotation_font=dict(family="Inter", size=10, color=COLOR_EMERALD)
    )

    fig.update_layout(
        bargap=0.08,
        xaxis_title=col,
        yaxis_title="Record Count"
    )
    return apply_pbi_theme(fig, height=380)


def create_relationship_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
    max_points: int = 1500
) -> go.Figure:
    """Builds a scatter plot with regression trendline."""
    plot_df = df.dropna(subset=[x_col, y_col]).copy()
    if len(plot_df) > max_points:
        plot_df = plot_df.sample(max_points, random_state=42)

    has_color = color_col and color_col in plot_df.columns

    try:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col if has_color else None,
            trendline="ols" if not has_color and pd.api.types.is_numeric_dtype(plot_df[x_col]) else None,
            title=f"Relationship // {x_col} vs {y_col}",
            color_continuous_scale="Tealgrn" if has_color and pd.api.types.is_numeric_dtype(plot_df[color_col]) else None,
            opacity=0.75
        )
    except Exception:
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            color=color_col if has_color else None,
            title=f"Relationship // {x_col} vs {y_col}",
            opacity=0.75
        )

    fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color="#ffffff")))
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    return apply_pbi_theme(fig, height=380)


def create_pbi_correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> go.Figure:
    """Builds an executive correlation matrix heatmap for Power BI."""
    if len(numeric_cols) < 2:
        fig = go.Figure()
        fig.update_layout(title="At least 2 numeric features needed for correlation")
        return apply_pbi_theme(fig, height=380)

    corr_df = df[numeric_cols].corr().round(2)
    z_vals = corr_df.values
    x_labels = corr_df.columns.tolist()
    y_labels = corr_df.index.tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#3b82f6"],   # Inverse: Blue
            [0.5, "#ffffff"],   # Neutral: White
            [1.0, "#f43f5e"]    # Positive: Rose
        ],
        zmin=-1.0,
        zmax=1.0,
        text=z_vals,
        texttemplate="%{text}",
        textfont=dict(family="Inter", size=10, color="#0f172a"),
        colorbar=dict(title="r", thickness=12, len=0.8)
    ))

    fig.update_layout(
        title="Cross-Feature Correlation Matrix (r)",
        xaxis=dict(tickangle=-35)
    )
    return apply_pbi_theme(fig, height=380)


def create_cohort_bar_chart(
    df: pd.DataFrame,
    group_col: Optional[str] = None,
    metric_col: Optional[str] = None
) -> go.Figure:
    """Builds a cohort bar visual by binning a continuous variable (like HouseAge) or categorical."""
    plot_df = df.copy()

    # If no group column provided, auto-detect HouseAge or create bins from first numeric
    if not group_col or group_col not in plot_df.columns:
        if "HouseAge" in plot_df.columns:
            group_col = "HouseAge"
        else:
            nums = plot_df.select_dtypes(include=[np.number]).columns.tolist()
            group_col = nums[0] if nums else plot_df.columns[0]

    # If numeric, create cohorts
    if pd.api.types.is_numeric_dtype(plot_df[group_col]):
        clean_s = plot_df[group_col].dropna()
        q_bins = [clean_s.min(), clean_s.quantile(0.25), clean_s.quantile(0.50), clean_s.quantile(0.75), clean_s.max()]
        labels = ["Lowest 25%", "25% - 50%", "50% - 75%", "Top 25%"]
        
        # If HouseAge, use realistic labels
        if group_col.lower() in ["houseage", "age"]:
            q_bins = [0, 15, 30, 45, 100]
            labels = ["Newer (<15y)", "15-30y", "30-45y", "Historic (45y+)"]

        try:
            plot_df["Cohort"] = pd.cut(plot_df[group_col], bins=q_bins, labels=labels, include_lowest=True)
            grp = "Cohort"
        except Exception:
            grp = group_col
    else:
        grp = group_col

    # Target metric
    if not metric_col or metric_col not in plot_df.columns:
        metric_col = "MedInc" if "MedInc" in plot_df.columns else (
            plot_df.select_dtypes(include=[np.number]).columns[0] if len(plot_df.select_dtypes(include=[np.number]).columns) > 0 else None
        )

    if metric_col:
        agg_df = plot_df.groupby(grp, observed=False)[metric_col].mean().reset_index()
        fig = px.bar(
            agg_df,
            x=grp,
            y=metric_col,
            title=f"Cohort Analysis // Avg. {metric_col} by {group_col}",
            color=metric_col,
            color_continuous_scale="Blues",
            text_auto=".2f"
        )
    else:
        counts = plot_df[grp].value_counts().reset_index()
        counts.columns = [grp, "Count"]
        fig = px.bar(
            counts,
            x=grp,
            y="Count",
            title=f"Category Distribution // {grp}",
            color="Count",
            color_continuous_scale="Blues"
        )

    fig.update_traces(width=0.45, marker_line_color="#1d4ed8", marker_line_width=1)
    fig.update_layout(coloraxis_showscale=False, bargap=0.3)
    return apply_pbi_theme(fig, height=380)


def create_outlier_box_plot(df: pd.DataFrame, num_cols: List[str]) -> go.Figure:
    """Builds a multi-feature box and whisker plot for outlier analysis."""
    cols_to_plot = num_cols[:4] if len(num_cols) >= 4 else num_cols
    
    # Normalize features between 0 and 100 for clean comparative visualization
    melt_df = df[cols_to_plot].dropna()

    fig = go.Figure()
    for idx, col in enumerate(cols_to_plot):
        fig.add_trace(go.Box(
            y=melt_df[col],
            name=col,
            marker_color=PBI_PALETTE[idx % len(PBI_PALETTE)],
            boxpoints="outliers"
        ))

    fig.update_layout(
        title=f"Outlier & Spread Inspection (Box & Whisker)",
        yaxis_title="Feature Value"
    )
    return apply_pbi_theme(fig, height=380)
