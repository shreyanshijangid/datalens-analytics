"""
DataLens - Single-Page Power BI Executive Analytics Dashboard
Engineered for College Data Visualization & Handling Lab.
Features a cohesive single-canvas layout, interactive slicers, KPI scorecards,
and diverse visual analytics fully compatible with California Housing & any tabular CSV.
"""

import io
import os
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="DataLens // Power BI Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Internal modules
from utils.style import (
    get_light_css,
    render_pbi_header,
    render_pbi_kpis,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_EMERALD,
    COLOR_AMBER,
    COLOR_PURPLE,
    COLOR_ROSE,
)
from utils.cleaning import (
    get_dataset_profile,
    remove_duplicates,
    drop_unwanted_columns,
    handle_missing_values,
    detect_and_handle_outliers_iqr,
    convert_column_to_datetime,
    get_viva_defense_cheat_sheet,
)
from utils.charts import (
    detect_geo_columns,
    create_geo_map,
    create_distribution_curve,
    create_relationship_scatter,
    create_pbi_correlation_heatmap,
    create_cohort_bar_chart,
    create_outlier_box_plot,
)

# Apply Power BI stylesheet
st.markdown(get_light_css(), unsafe_allow_html=True)


# ==========================================
# CACHED DATA LOADERS
# ==========================================

@st.cache_data(show_spinner=False)
def load_csv_data(file_bytes: bytes) -> pd.DataFrame:
    """Reads CSV file from bytes buffer."""
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def load_california_dataset() -> pd.DataFrame:
    """Loads California Housing benchmark dataset."""
    cali_path = os.path.join(os.path.dirname(__file__), "sample_data", "california_housing.csv")
    if os.path.exists(cali_path):
        return pd.read_csv(cali_path)
    # Generate representative California housing sample if not yet downloaded
    from sklearn.datasets import fetch_california_housing
    data = fetch_california_housing(as_frame=True)
    df = data.frame
    df.to_csv(cali_path, index=False)
    return df


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "df_data" not in st.session_state:
    # Default directly to California Housing dataset so dashboard loads instantly with rich data!
    try:
        sample_df = load_california_dataset()
        st.session_state.df_data = sample_df.copy()
        st.session_state.df_raw = sample_df.copy()
        st.session_state.dataset_name = "California Housing (Benchmark)"
    except Exception:
        # Fallback to air quality
        aqi_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "sample_data", "air_quality_india.csv"))
        st.session_state.df_data = aqi_df.copy()
        st.session_state.df_raw = aqi_df.copy()
        st.session_state.dataset_name = "Air Quality India (Benchmark)"

if "cleaning_logs" not in st.session_state:
    st.session_state.cleaning_logs = ["Initialized benchmark dataset."]


# ==========================================
# TOP POWER BI CONTROL & UPLOAD BAR
# ==========================================

current_df = st.session_state.df_data
profile = get_dataset_profile(current_df)

render_pbi_header(
    dataset_name=st.session_state.dataset_name,
    row_count=len(current_df),
    col_count=current_df.shape[1]
)

# Collapsible Quick-Bar for File Ingestion & Data Hygiene
with st.expander("📁 INGESTION & DATA CLEANING CONTROLS (CLICK TO EXPAND / COLLAPSE)", expanded=False):
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1, 1], gap="medium")

    with ctrl_col1:
        st.markdown("**Upload Custom CSV or Excel File**")
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["csv", "xlsx"],
            label_visibility="collapsed",
            key="pbi_uploader"
        )
        if uploaded_file is not None:
            try:
                f_bytes = uploaded_file.read()
                if uploaded_file.name.endswith(".csv"):
                    new_df = load_csv_data(f_bytes)
                else:
                    new_df = pd.read_excel(io.BytesIO(f_bytes))

                st.session_state.df_data = new_df.copy()
                st.session_state.df_raw = new_df.copy()
                st.session_state.dataset_name = uploaded_file.name
                st.session_state.cleaning_logs = [f"Ingested '{uploaded_file.name}'."]
                st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with ctrl_col2:
        st.markdown("**Quick Preset Datasets**")
        if st.button("🏠 LOAD CALIFORNIA HOUSING DATASET"):
            cali_df = load_california_dataset()
            st.session_state.df_data = cali_df.copy()
            st.session_state.df_raw = cali_df.copy()
            st.session_state.dataset_name = "California Housing (Benchmark)"
            st.session_state.cleaning_logs = ["Loaded California Housing benchmark dataset."]
            st.rerun()

        if st.button("🌫️ LOAD AIR QUALITY DATASET"):
            aqi_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "sample_data", "air_quality_india.csv"))
            st.session_state.df_data = aqi_df.copy()
            st.session_state.df_raw = aqi_df.copy()
            st.session_state.dataset_name = "Air Quality India"
            st.session_state.cleaning_logs = ["Loaded Air Quality India benchmark dataset."]
            st.rerun()

    with ctrl_col3:
        st.markdown("**Data Hygiene & Export**")
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🧹 REMOVE DUPS"):
                cleaned_df, dup_n, msg = remove_duplicates(st.session_state.df_data)
                st.session_state.df_data = cleaned_df
                st.session_state.cleaning_logs.append(msg)
                st.success(f"Removed {dup_n} duplicates!")
                st.rerun()
        with c_btn2:
            if st.button("↺ RESET DATA"):
                st.session_state.df_data = st.session_state.df_raw.copy()
                st.session_state.cleaning_logs = ["Reset to raw dataset."]
                st.rerun()

        csv_bytes = st.session_state.df_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 DOWNLOAD CLEANED CSV",
            data=csv_bytes,
            file_name=f"cleaned_{st.session_state.dataset_name.split()[0].lower()}.csv",
            mime="text/csv"
        )


# ==========================================
# POWER BI INTERACTIVE SLICER STRIP
# ==========================================

num_cols = profile["numeric_cols"]
plot_filtered_df = current_df.copy()

# Add a clean slicer bar if numeric features exist
if len(num_cols) >= 2:
    with st.container(border=True):
        st.markdown(
            '<div style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 6px;">'
            '<span>🎛️ POWER BI INTERACTIVE SLICERS</span>'
            '<span style="font-weight: 400; color: #94a3b8; font-size: 0.75rem;">(Adjusting filters dynamically updates all charts below)</span>'
            '</div>',
            unsafe_allow_html=True
        )

        slicer_col1, slicer_col2, slicer_col3 = st.columns(3)

        # Primary Slicer: HouseAge or first numeric
        slicer1_col = "HouseAge" if "HouseAge" in num_cols else num_cols[0]
        min1 = float(current_df[slicer1_col].min())
        max1 = float(current_df[slicer1_col].max())

        with slicer_col1:
            if min1 < max1:
                val_range1 = st.slider(
                    f"Slicer // {slicer1_col}",
                    min_value=min1,
                    max_value=max1,
                    value=(min1, max1),
                    key="slicer_1"
                )
                plot_filtered_df = plot_filtered_df[
                    (plot_filtered_df[slicer1_col] >= val_range1[0]) &
                    (plot_filtered_df[slicer1_col] <= val_range1[1])
                ]

        # Secondary Slicer: MedInc or second numeric
        slicer2_col = "MedInc" if "MedInc" in num_cols and "MedInc" != slicer1_col else (num_cols[1] if len(num_cols) > 1 else num_cols[0])
        min2 = float(current_df[slicer2_col].min())
        max2 = float(current_df[slicer2_col].max())

        with slicer_col2:
            if min2 < max2:
                val_range2 = st.slider(
                    f"Slicer // {slicer2_col}",
                    min_value=min2,
                    max_value=max2,
                    value=(min2, max2),
                    key="slicer_2"
                )
                plot_filtered_df = plot_filtered_df[
                    (plot_filtered_df[slicer2_col] >= val_range2[0]) &
                    (plot_filtered_df[slicer2_col] <= val_range2[1])
                ]

        # Tertiary Slicer or Quick Metric selector
        with slicer_col3:
            target_focus = st.selectbox(
                "Primary Analysis Dimension",
                options=num_cols,
                index=0 if "MedInc" not in num_cols else num_cols.index("MedInc"),
                key="target_focus_sel"
            )


# ==========================================
# POWER BI TOP KPI SCORECARD ROW
# ==========================================

active_rows = len(plot_filtered_df)

if "MedInc" in plot_filtered_df.columns:
    avg_income = f"${plot_filtered_df['MedInc'].mean():.2f}k"
    avg_age = f"{plot_filtered_df['HouseAge'].mean():.1f} yrs" if "HouseAge" in plot_filtered_df.columns else "N/A"
    total_pop = f"{int(plot_filtered_df['Population'].sum()):,}" if "Population" in plot_filtered_df.columns else "N/A"
    avg_rooms = f"{plot_filtered_df['AveRooms'].mean():.2f}" if "AveRooms" in plot_filtered_df.columns else "N/A"

    kpis = [
        {"label": "Total Observations", "value": f"{active_rows:,}", "subtext": f"{active_rows / len(current_df) * 100:.0f}% of total dataset", "color": COLOR_PRIMARY},
        {"label": "Avg. Median Income", "value": avg_income, "subtext": "Median income in block", "color": COLOR_EMERALD},
        {"label": "Avg. Property Age", "value": avg_age, "subtext": "Median housing age", "color": COLOR_SECONDARY},
        {"label": "Total Population", "value": total_pop, "subtext": "Block group population", "color": COLOR_PURPLE},
        {"label": "Avg. Rooms / House", "value": avg_rooms, "subtext": "Household density index", "color": COLOR_AMBER},
    ]
else:
    # Generic adaptive scorecards for any uploaded dataset
    kpis = [
        {"label": "Active Records", "value": f"{active_rows:,}", "subtext": f"Features: {plot_filtered_df.shape[1]}", "color": COLOR_PRIMARY},
    ]
    colors = [COLOR_EMERALD, COLOR_SECONDARY, COLOR_PURPLE, COLOR_AMBER]
    for idx, col in enumerate(num_cols[:4]):
        col_mean = plot_filtered_df[col].mean()
        val_str = f"{col_mean:.2f}" if abs(col_mean) < 10000 else f"{col_mean:,.0f}"
        kpis.append({
            "label": f"Avg. {col}",
            "value": val_str,
            "subtext": f"Std: {plot_filtered_df[col].std():.2f}",
            "color": colors[idx % len(colors)]
        })

render_pbi_kpis(kpis)


# ==========================================
# POWER BI PRIMARY VISUALS GRID
# ==========================================

geo_cols = detect_geo_columns(plot_filtered_df)

# Row 1: Geographic Map & Distribution
col_v1, col_v2 = st.columns([1.25, 1], gap="medium")

with col_v1:
    with st.container(border=True):
        if geo_cols:
            lat_col, lon_col = geo_cols
            color_metric = target_focus if target_focus in plot_filtered_df.columns else ("MedInc" if "MedInc" in plot_filtered_df.columns else num_cols[0])
            size_metric = "Population" if "Population" in plot_filtered_df.columns else None

            st.markdown(
                f'<div class="pbi-visual-header">'
                f'<div class="pbi-visual-title">🗺️ Geographic Spatial Map ({lat_col} × {lon_col})</div>'
                f'<span class="pbi-badge">Color: {color_metric}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            geo_fig = create_geo_map(plot_filtered_df, lat_col, lon_col, color_col=color_metric, size_col=size_metric)
            st.plotly_chart(geo_fig, use_container_width=True)
        else:
            # Fallback to relationship visual
            x_dim = num_cols[0] if len(num_cols) > 0 else plot_filtered_df.columns[0]
            y_dim = num_cols[1] if len(num_cols) > 1 else num_cols[0]
            st.markdown(
                f'<div class="pbi-visual-header">'
                f'<div class="pbi-visual-title">📈 Cross-Dimension Relationship ({x_dim} vs {y_dim})</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            rel_fig = create_relationship_scatter(plot_filtered_df, x_dim, y_dim)
            st.plotly_chart(rel_fig, use_container_width=True)

with col_v2:
    with st.container(border=True):
        dist_feature = target_focus if target_focus in plot_filtered_df.columns else (num_cols[0] if num_cols else plot_filtered_df.columns[0])
        st.markdown(
            f'<div class="pbi-visual-header">'
            f'<div class="pbi-visual-title">📊 Distribution & Density Profile</div>'
            f'<span class="pbi-badge">Feature: {dist_feature}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        dist_fig = create_distribution_curve(plot_filtered_df, dist_feature)
        st.plotly_chart(dist_fig, use_container_width=True)


# Row 2: Relationship Scatter & Correlation Matrix
col_v3, col_v4 = st.columns(2, gap="medium")

with col_v3:
    with st.container(border=True):
        # Auto pick interesting pairs
        if "MedInc" in plot_filtered_df.columns and "AveRooms" in plot_filtered_df.columns:
            def_x, def_y = "MedInc", "AveRooms"
        elif len(num_cols) >= 2:
            def_x, def_y = num_cols[0], num_cols[1]
        else:
            def_x = def_y = num_cols[0]

        st.markdown(
            f'<div class="pbi-visual-header">'
            f'<div class="pbi-visual-title">📈 Bivariate Scatter & Regression Trendline</div>'
            f'<span class="pbi-badge">{def_x} vs {def_y}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        color_hue = "HouseAge" if "HouseAge" in plot_filtered_df.columns else None
        scatter_fig = create_relationship_scatter(plot_filtered_df, def_x, def_y, color_col=color_hue)
        st.plotly_chart(scatter_fig, use_container_width=True)

with col_v4:
    with st.container(border=True):
        st.markdown(
            f'<div class="pbi-visual-header">'
            f'<div class="pbi-visual-title">🧩 Pearson Correlation Matrix Heatmap</div>'
            f'<span class="pbi-badge">{len(num_cols)} Numerical Attributes</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        corr_fig = create_pbi_correlation_heatmap(plot_filtered_df, num_cols)
        st.plotly_chart(corr_fig, use_container_width=True)


# Row 3: Cohort Analysis Bar Chart & Outlier Box Plot
col_v5, col_v6 = st.columns(2, gap="medium")

with col_v5:
    with st.container(border=True):
        st.markdown(
            f'<div class="pbi-visual-header">'
            f'<div class="pbi-visual-title">🏷️ Age Cohort Comparison (Power BI Column Visual)</div>'
            f'<span class="pbi-badge">Binned Groups</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        cohort_fig = create_cohort_bar_chart(plot_filtered_df, group_col="HouseAge" if "HouseAge" in plot_filtered_df.columns else None, metric_col=target_focus)
        st.plotly_chart(cohort_fig, use_container_width=True)

with col_v6:
    with st.container(border=True):
        st.markdown(
            f'<div class="pbi-visual-header">'
            f'<div class="pbi-visual-title">📦 Outlier & Dispersion Inspection (Box & Whisker)</div>'
            f'<span class="pbi-badge">Quartiles & Extremes</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        box_fig = create_outlier_box_plot(plot_filtered_df, num_cols)
        st.plotly_chart(box_fig, use_container_width=True)


# ==========================================
# BOTTOM POWER BI EXECUTIVE DATA GRID & VIVA SECTION
# ==========================================

with st.container(border=True):
    st.markdown(
        f'<div class="pbi-visual-header">'
        f'<div class="pbi-visual-title">📋 Tabular Data Grid Preview (Showing Top 15 Records)</div>'
        f'<span class="pbi-badge">{active_rows:,} Filtered Records</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.dataframe(plot_filtered_df.head(15), use_container_width=True)

# Collapsible Viva Theory Accordion
with st.expander("🎓 LAB VIVA EVALUATION CHEAT SHEET & THEORETICAL DEFENSE", expanded=False):
    viva_items = get_viva_defense_cheat_sheet()
    for item in viva_items:
        st.markdown(f"**Q: {item['question']}**\n\n*{item['answer']}*\n\n---")
