"""
DataLens - Data Cleaning & Handling Engine
Provides profiling, missing-value imputation, duplicate purging,
IQR outlier treatment, column dropping, and datetime casting with viva-ready explainability.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np


def get_dataset_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes comprehensive profile metadata for the dataset.

    Returns summary metrics, column-level health breakdown, and categorized
    column lists for auto-charting.
    """
    total_rows = int(df.shape[0])
    total_cols = int(df.shape[1])
    total_cells = total_rows * total_cols if total_rows > 0 else 1

    total_missing = int(df.isna().sum().sum())
    missing_pct = round((total_missing / total_cells) * 100, 2) if total_cells > 0 else 0.0

    duplicate_rows = int(df.duplicated().sum()) if total_rows > 0 else 0
    duplicate_pct = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0

    # Memory usage formatting
    mem_bytes = df.memory_usage(deep=True).sum()
    if mem_bytes < 1024 * 1024:
        memory_str = f"{mem_bytes / 1024:.2f} KB"
    else:
        memory_str = f"{mem_bytes / (1024 * 1024):.2f} MB"

    # Identify column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    boolean_cols = df.select_dtypes(include=["bool"]).columns.tolist()
    categorical_cols = [
        c for c in df.columns
        if c not in numeric_cols and c not in datetime_cols and c not in boolean_cols
    ]

    constant_cols = []
    high_cardinality_cols = []

    # Column-level breakdown table
    col_breakdown = []
    for col in df.columns:
        col_series = df[col]
        missing_count = int(col_series.isna().sum())
        missing_col_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        unique_cnt = int(col_series.nunique(dropna=True))

        if unique_cnt == 1:
            constant_cols.append(col)
        elif col in categorical_cols and unique_cnt > 50 and total_rows > 50:
            high_cardinality_cols.append(col)

        # Sample value representation
        valid_vals = col_series.dropna()
        sample_val = str(valid_vals.iloc[0]) if len(valid_vals) > 0 else "N/A"
        if len(sample_val) > 28:
            sample_val = sample_val[:25] + "..."

        # Inferred type tag
        if col in numeric_cols:
            dtype_tag = "Numeric (Float/Int)"
        elif col in datetime_cols:
            dtype_tag = "Datetime"
        elif col in boolean_cols:
            dtype_tag = "Boolean"
        else:
            dtype_tag = "Categorical / String"

        quality_note = "Invariant (1 Value)" if unique_cnt == 1 else ("High Cardinality" if unique_cnt > 50 and col in categorical_cols else "Normal")

        col_breakdown.append({
            "Column Name": col,
            "Type": str(col_series.dtype),
            "Category": dtype_tag,
            "Non-Null Count": total_rows - missing_count,
            "Missing Count": missing_count,
            "Missing %": f"{missing_col_pct}%",
            "Unique Values": unique_cnt,
            "Quality Flag": quality_note,
            "Sample Value": sample_val
        })

    col_profile_df = pd.DataFrame(col_breakdown)

    # Health score heuristic (0 - 100)
    missing_penalty = min(missing_pct * 1.5, 45.0)
    dup_penalty = min(duplicate_pct * 2.0, 30.0)
    constant_penalty = min(len(constant_cols) * 5.0, 15.0)
    health_score = int(max(0, min(100, round(100.0 - missing_penalty - dup_penalty - constant_penalty))))

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "memory_str": memory_str,
        "col_profile_df": col_profile_df,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols,
        "boolean_cols": boolean_cols,
        "constant_cols": constant_cols,
        "high_cardinality_cols": high_cardinality_cols,
        "health_score": health_score,
    }


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, str]:
    """Removes duplicate rows from dataframe and provides a viva explanation."""
    initial_len = len(df)
    df_cleaned = df.drop_duplicates().copy()
    removed_count = initial_len - len(df_cleaned)

    explanation = (
        f"Purged {removed_count} redundant duplicate rows. "
        f"Dataset cardinality reduced from {initial_len} to {len(df_cleaned)}."
        if removed_count > 0
        else "No duplicate rows were present in the dataset."
    )
    return df_cleaned, removed_count, explanation


def drop_unwanted_columns(df: pd.DataFrame, columns_to_drop: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Drops uninformative, single-value, or redundant columns."""
    df_result = df.copy()
    logs = []
    dropped_cols = []
    for c in columns_to_drop:
        if c in df_result.columns:
            df_result = df_result.drop(columns=[c])
            dropped_cols.append(c)

    if dropped_cols:
        logs.append(
            f"[COLUMN DROP] Removed uninformative/constant column(s): {', '.join(dropped_cols)} "
            f"(Feature count reduced to {len(df_result.columns)})."
        )
    return df_result, logs


def handle_missing_values(
    df: pd.DataFrame,
    strategy_map: Dict[str, str],
    custom_constants: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, List[str]]:
    """Handles missing values based on user configuration per column."""
    df_result = df.copy()
    logs = []
    custom_constants = custom_constants or {}

    for col, strat in strategy_map.items():
        if col not in df_result.columns:
            continue

        missing_before = int(df_result[col].isna().sum())
        if missing_before == 0 and strat != "drop_row":
            continue

        if strat == "keep":
            continue

        elif strat == "drop_row":
            initial_count = len(df_result)
            df_result = df_result.dropna(subset=[col])
            dropped = initial_count - len(df_result)
            logs.append(
                f"[DROP ROWS] Removed {dropped} rows containing null values in column '{col}'."
            )

        elif strat == "mean":
            if pd.api.types.is_numeric_dtype(df_result[col]):
                mean_val = float(df_result[col].mean())
                df_result[col] = df_result[col].fillna(mean_val)
                logs.append(
                    f"[IMPUTE: MEAN] Imputed {missing_before} missing entries in '{col}' "
                    f"using column mean ({mean_val:.2f})."
                )
            else:
                logs.append(
                    f"[SKIPPED] Cannot compute numerical mean for non-numeric column '{col}'."
                )

        elif strat == "median":
            if pd.api.types.is_numeric_dtype(df_result[col]):
                med_val = float(df_result[col].median())
                df_result[col] = df_result[col].fillna(med_val)
                logs.append(
                    f"[IMPUTE: MEDIAN] Imputed {missing_before} missing entries in '{col}' "
                    f"using robust median ({med_val:.2f}) [viva note: resistant to outliers and skew]."
                )
            else:
                logs.append(
                    f"[SKIPPED] Cannot compute numerical median for non-numeric column '{col}'."
                )

        elif strat == "mode":
            mode_series = df_result[col].mode()
            if len(mode_series) > 0:
                mode_val = mode_series.iloc[0]
                df_result[col] = df_result[col].fillna(mode_val)
                logs.append(
                    f"[IMPUTE: MODE] Imputed {missing_before} missing entries in '{col}' "
                    f"with most frequent category ('{mode_val}')."
                )
            else:
                logs.append(f"[SKIPPED] Column '{col}' has no valid mode.")

        elif strat == "interpolate":
            if pd.api.types.is_numeric_dtype(df_result[col]):
                df_result[col] = df_result[col].interpolate(method="linear").bfill().ffill()
                logs.append(
                    f"[INTERPOLATE] Applied linear interpolation to '{col}' for {missing_before} points "
                    f"[viva note: smoothly estimates missing values in sequential/sensor data]."
                )
            else:
                logs.append(
                    f"[SKIPPED] Linear interpolation only supports numeric sequences for '{col}'."
                )

        elif strat == "ffill":
            df_result[col] = df_result[col].ffill().bfill()
            logs.append(
                f"[FORWARD-FILL] Propagated preceding values for {missing_before} nulls in '{col}'."
            )

        elif strat == "bfill":
            df_result[col] = df_result[col].bfill().ffill()
            logs.append(
                f"[BACKWARD-FILL] Propagated subsequent values for {missing_before} nulls in '{col}'."
            )

        elif strat == "constant":
            val = custom_constants.get(col, "Unknown" if not pd.api.types.is_numeric_dtype(df_result[col]) else 0)
            df_result[col] = df_result[col].fillna(val)
            logs.append(
                f"[CONSTANT] Replaced {missing_before} nulls in '{col}' with static value: '{val}'."
            )

    return df_result, logs


def detect_and_handle_outliers_iqr(
    df: pd.DataFrame,
    columns: List[str],
    factor: float = 1.5,
    action: str = "cap"
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]], List[str]]:
    """Detects and resolves numerical outliers using the Interquartile Range (IQR) method."""
    df_result = df.copy()
    outlier_meta = {}
    logs = []

    valid_cols = [c for c in columns if c in df_result.columns and pd.api.types.is_numeric_dtype(df_result[c])]

    if action == "remove":
        outlier_indices = set()
        for col in valid_cols:
            series = df_result[col].dropna()
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - (factor * iqr)
            upper_bound = q3 + (factor * iqr)

            col_outliers = series[(series < lower_bound) | (series > upper_bound)]
            count = len(col_outliers)
            outlier_meta[col] = {
                "q1": round(q1, 3),
                "q3": round(q3, 3),
                "iqr": round(iqr, 3),
                "lower_bound": round(lower_bound, 3),
                "upper_bound": round(upper_bound, 3),
                "count": count
            }
            if count > 0:
                outlier_indices.update(col_outliers.index)
                logs.append(
                    f"[OUTLIERS: PURGE] '{col}': Identified {count} anomalies outside "
                    f"[{lower_bound:.2f}, {upper_bound:.2f}] (Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f})."
                )

        initial_len = len(df_result)
        df_result = df_result.drop(index=list(outlier_indices))
        logs.append(
            f"[ACTION: PURGE] Dropped {len(outlier_indices)} rows with extreme outliers across selected columns "
            f"(Rows: {initial_len} → {len(df_result)})."
        )

    else:  # 'cap' / Winsorize
        for col in valid_cols:
            series = df_result[col].dropna()
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - (factor * iqr)
            upper_bound = q3 + (factor * iqr)

            mask_lower = df_result[col] < lower_bound
            mask_upper = df_result[col] > upper_bound
            count = int(mask_lower.sum() + mask_upper.sum())

            outlier_meta[col] = {
                "q1": round(q1, 3),
                "q3": round(q3, 3),
                "iqr": round(iqr, 3),
                "lower_bound": round(lower_bound, 3),
                "upper_bound": round(upper_bound, 3),
                "count": count
            }

            if count > 0:
                df_result[col] = df_result[col].clip(lower=lower_bound, upper=upper_bound)
                logs.append(
                    f"[OUTLIERS: CAP] '{col}': Capped {count} anomalies to IQR boundaries "
                    f"[{lower_bound:.2f}, {upper_bound:.2f}] (Winsorization preserved all {len(df_result)} rows)."
                )

    return df_result, outlier_meta, logs


def convert_column_to_datetime(
    df: pd.DataFrame,
    column: str,
    date_format: Optional[str] = None
) -> Tuple[pd.DataFrame, bool, str]:
    """Casts specified column to datetime64 format safely."""
    df_result = df.copy()
    if column not in df_result.columns:
        return df_result, False, f"Column '{column}' does not exist."

    try:
        if date_format and date_format.strip():
            df_result[column] = pd.to_datetime(df_result[column], format=date_format.strip(), errors="coerce")
        else:
            df_result[column] = pd.to_datetime(df_result[column], errors="coerce")

        null_after = int(df_result[column].isna().sum())
        msg = (
            f"Successfully converted '{column}' to datetime64[ns] timestamps. "
            f"({null_after} invalid timestamps coerced to NaT)."
        )
        return df_result, True, msg
    except Exception as e:
        return df_result, False, f"Datetime conversion failed: {str(e)}"


def get_viva_defense_cheat_sheet() -> List[Dict[str, str]]:
    """Returns essential Viva Q&A tips for the lab examination."""
    return [
        {
            "question": "Why use IQR for outlier detection over Z-score / 3-sigma?",
            "answer": (
                "Z-score assumes the underlying data follows a Normal (Gaussian) distribution, "
                "and its mean & standard deviation are themselves distorted by extreme outliers. "
                "IQR (Q3 - Q1) is a non-parametric statistic based on percentiles; it is unaffected "
                "by arbitrary distribution shapes and resilient against multiple extreme values."
            )
        },
        {
            "question": "When should we Impute with Median vs Mean?",
            "answer": (
                "Mean is heavily sensitive to skewness and extreme outliers (e.g., pollution spikes or stock volatility). "
                "If the column is skewed (skewness > 1 or < -1), Median is the mathematically sound "
                "choice. Mean is appropriate only when the distribution is symmetric (normal bell curve)."
            )
        },
        {
            "question": "What is the advantage of Winsorization (Capping) over Dropping outlier rows?",
            "answer": (
                "Dropping outlier rows deletes legitimate multi-variable telemetry data and may bias "
                "sample sizes or break sequential time-series intervals. Capping retains all row observations "
                "while restricting extreme leverage on linear models and aggregations."
            )
        },
        {
            "question": "Why should single-value (constant) columns be dropped in preprocessing?",
            "answer": (
                "Columns with a single constant value (zero variance) contain zero information entropy. "
                "They cannot help in classification, regression, or clustering, and only increase memory overhead."
            )
        },
        {
            "question": "Why is Datetime casting necessary for Auto-EDA?",
            "answer": (
                "String/object dates cannot support temporal sorting, resampled frequency aggregation (e.g. daily/weekly), "
                "or continuous chronological trendlines in visualization libraries like Plotly."
            )
        }
    ]
