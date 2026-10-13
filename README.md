# 📊 DataLens — Modern Auto-EDA & Data Handling Studio

> **College Data Visualization & Handling Lab Suite**  
> A clean, modern, explainable Auto-EDA dashboard engineered for academic lab coursework, viva defense, and exploratory data analysis.

---

## 🌟 What's New: Clean White Mode & Smart Visuals

- **Modern White Theme**: Crisp, high-end design inspired by Stripe & Linear. Soft slate background (`#f8fafc`), clean white cards (`#ffffff`), subtle shadows, and indigo/emerald accent palettes.
- **Smart Single-Class Handling**: Invariant single-value columns (such as repeated stock symbols like `HINDUNILVR`) are automatically detected and flagged instead of producing flat full-screen bars.
- **Feature Pruning**: One-click feature dropping tool under Tab 02 to discard zero-variance attributes.
- **Financial Candlestick Analysis**: Automatic detection of `Open`, `High`, `Low`, `Close`, and `Volume` columns with interactive candlestick charts, 20-period moving averages, and volume histograms.
- **Donut & Proportional Bar Options**: Categorical distributions now support styled Donut charts and proportional bars with controlled widths.

---

## 🚀 Overview

**DataLens** transforms raw tabular data (`.csv` or `.xlsx`) into interactive, viva-ready analytical telemetry. Built specifically for academic data handling and visualization curricula, every transformation step is logged with its mathematical rationale—empowering students to clearly explain and defend their data hygiene decisions in lab examinations.

---

## ✨ Core Features

### 1. Ingestion & Data Preview (Tab 01)
- Drag-and-drop support for `.csv` and `.xlsx` files.
- Instant benchmark loader (`sample_data/air_quality_india.csv`).
- Top Metric Cards: Total Records, Features, Missing Ratio %, Duplicates, and Data Health Score.
- Real-time schema quality inspection table with type inference.

### 2. Data Handling Studio (Tab 02)
- **Feature Pruning**: Drop uninformative, ID, or constant columns with one click.
- **Missing Value Handling**: Impute using Median (robust against skew), Mean, Mode, or Linear Interpolation.
- **Duplicate Purging**: Identifies and drops redundant row tuples.
- **IQR Outlier Diagnostics**: Tukey's fences $[\text{Q1} - k \times \text{IQR}, \text{Q3} + k \times \text{IQR}]$ with Winsorization (capping) or row dropping.
- **Datetime Casting**: Casts date strings into `datetime64[ns]` timestamps.
- **Before vs. After Delta**: Live metric comparisons of rows, nulls, and health score.
- **Export**: One-click download of the cleaned dataset as a CSV.
- **Viva Defense Cheat Sheet**: Theoretical explanations for common exam questions.

### 3. Auto Visuals & Telemetry (Tab 03)
- **Stock Candlestick Telemetry**: Unlocked automatically when financial OHLC columns are detected.
- **Numerical Distributions**: Histograms with marginal box plots and Mean/Median reference lines.
- **Categorical Distributions**: Proportional bar charts and Donut charts with class dominance insights.
- **Chronological Timeline**: Multi-series line charts with time range slider.
- **Correlation Diagnostics**: Annotated Pearson correlation heatmap with clean diverging palette.
- **Bivariate Scatter**: Interactive scatter plots with category color hue grouping and OLS trendlines.

### 4. Custom Chart Studio (Tab 04)
- Interactive builder supporting Scatter, Line, Bar, Box, Histogram, Donut, Area, and Violin plots.
- Aggregations (Mean, Sum, Count, Min, Max, Median) and high-res PNG export.

### 5. Lab Dossier & Viva Q&A (Tab 05)
- Full parametric descriptive statistics (`describe()`).
- Ranked co-variance pair table sorted by Pearson $|r|$.
- Auto-generated **Executive Lab Dossier Report** in Markdown format ready to copy or download.

---

## 📁 Project Structure

```text
c:/5th sem/data visualization lab/project/
├── app.py                      # Main Streamlit dashboard application
├── utils/
│   ├── __init__.py             # Module initialization
│   ├── style.py                # Clean White Mode CSS, header, metric cards, Plotly light themes
│   ├── cleaning.py             # Profiling, imputation, IQR outliers, column pruning, viva tips
│   └── charts.py               # Auto-EDA charts, Candlestick charts, insight generators, custom chart builder
├── sample_data/
│   └── air_quality_india.csv   # Benchmark India Air Quality dataset
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation & Viva guide
```

---

## 🛠️ Execution

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Open your browser at `http://localhost:8501`.
