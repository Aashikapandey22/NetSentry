"""
NetSentry Model Utilities
Handles loading the actual trained Random Forest PKL model,
input feature extraction and validation, cleaning, prediction, and metrics calculation.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NetSentry_RandomForest_Model.pkl")

# Cache model instance in memory
_CACHED_MODEL = None


def load_model(path: str = MODEL_PATH):
    """
    Loads the trained Random Forest model from the specified pickle file.
    Preserves original attributes like feature_names_in_ and classes_.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is not None:
        return _CACHED_MODEL

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at: {path}")

    model = joblib.load(path)
    _CACHED_MODEL = model
    return model


def get_model_features(model=None) -> List[str]:
    """
    Returns the exact 78 features expected by the model in precise order.
    """
    if model is None:
        model = load_model()
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    raise ValueError("Model does not contain 'feature_names_in_' attribute.")


def get_model_classes(model=None) -> List[str]:
    """
    Returns list of target classes recognized by the model.
    """
    if model is None:
        model = load_model()
    if hasattr(model, "classes_"):
        return [str(c) for c in model.classes_]
    return []


def get_feature_importances(model=None, top_n: int = 15) -> pd.Series:
    """
    Returns the top N feature importances from the trained Random Forest model.
    """
    if model is None:
        model = load_model()
    features = get_model_features(model)
    importances = pd.Series(model.feature_importances_, index=features)
    return importances.sort_values(ascending=False).head(top_n)


def clean_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strips leading/trailing whitespaces and UTF-8 BOM artifacts from column names,
    matching the notebook data cleaning step.
    """
    df = df.copy()
    df.columns = df.columns.astype(str).str.replace('\ufeff', '', regex=False).str.strip()
    return df


def validate_and_prepare_input(
    df: pd.DataFrame,
    model=None
) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str], List[str]]:
    """
    Validates uploaded DataFrame against the model's required 78 features:
    1. Cleans column names (strip whitespace / BOM)
    2. Identifies and separates optional 'Label' column
    3. Checks for missing required features
    4. Replaces infinite values with NaN and fills or drops missing values safely
    5. Converts to numeric
    6. Reorders columns to match exact feature_names_in_ order

    Returns:
        X_ready: DataFrame containing exactly 78 features in correct order
        y_true: Series of actual labels if present, else None
        missing_cols: List of missing required columns
        warnings: List of warning messages (e.g., non-numeric coerced)
    """
    if model is None:
        model = load_model()

    expected_features = get_model_features(model)
    cleaned_df = clean_dataframe_columns(df)

    warnings: List[str] = []

    # Check for optional Label column (case-insensitive)
    label_cols = [c for c in cleaned_df.columns if c.strip().lower() == "label"]
    y_true = None
    if label_cols:
        y_true = cleaned_df[label_cols[0]].copy()
        # Exclude Label column from prediction inputs
        cleaned_df = cleaned_df.drop(columns=[label_cols[0]])

    # Check for missing required features
    existing_cols = set(cleaned_df.columns)
    missing_cols = [col for col in expected_features if col not in existing_cols]
    if missing_cols:
        return pd.DataFrame(), y_true, missing_cols, warnings

    # Select only the expected 78 features in exact order
    X = cleaned_df[expected_features].copy()

    # Replace infinite values with NaN as done in the notebook
    X = X.replace([np.inf, -np.inf], np.nan)

    # Convert all columns to numeric safely
    for col in expected_features:
        if not np.issubdtype(X[col].dtype, np.number):
            non_num_count = pd.to_numeric(X[col], errors='coerce').isna().sum()
            if non_num_count > 0:
                warnings.append(f"Column '{col}' contained {non_num_count} non-numeric values converted to median.")
            X[col] = pd.to_numeric(X[col], errors='coerce')

    # Handle any NaN by filling with column median (fallback if uploaded rows have missing points)
    nan_count = X.isna().sum().sum()
    if nan_count > 0:
        warnings.append(f"Handled {nan_count} missing/NaN values by imputing column medians.")
        X = X.fillna(X.median(numeric_only=True)).fillna(0.0)

    # Re-verify shape and order
    X_ready = X[expected_features].astype(np.float64)

    return X_ready, y_true, [], warnings


def predict_traffic(X: pd.DataFrame, model=None) -> Dict[str, Any]:
    """
    Generates predictions and class probabilities using the loaded PKL model.
    """
    if model is None:
        model = load_model()

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    classes = get_model_classes(model)

    benign_count = int(np.sum(predictions == "BENIGN"))
    attack_count = int(len(predictions) - benign_count)

    # Highest confidence per row
    max_probs = np.max(probabilities, axis=1)

    results_df = X.copy()
    results_df["Predicted_Label"] = predictions
    results_df["Confidence"] = np.round(max_probs * 100, 2)
    results_df["Traffic_Type"] = np.where(predictions == "BENIGN", "Normal Traffic", "ATTACK DETECTED")

    return {
        "predictions": predictions,
        "probabilities": probabilities,
        "classes": classes,
        "benign_count": benign_count,
        "attack_count": attack_count,
        "total_count": len(predictions),
        "results_df": results_df
    }


# Reference ground truth distribution from CICIDS2017 notebook (Cell 12)
BENCHMARK_NOTEBOOK_DISTRIBUTION = {
    "BENIGN": 2273097,
    "DoS Hulk": 231073,
    "PortScan": 158930,
    "DDoS": 128027,
    "DoS GoldenEye": 10293,
    "FTP-Patator": 7938,
    "SSH-Patator": 5897,
    "DoS slowloris": 5796,
    "DoS Slowhttptest": 5499,
    "Bot": 1966,
    "Web Attack - Brute Force": 1507,
    "Web Attack - XSS": 652,
    "Infiltration": 36,
    "Web Attack - Sql Injection": 21,
    "Heartbleed": 11
}

# Reference model parameters from the notebook training cell
MODEL_PARAMETERS_SUMMARY = {
    "Algorithm": "Random Forest Classifier",
    "Source Dataset": "CICIDS2017 (MachineLearningCVE)",
    "Total Dataset Rows": "2,830,743 flows",
    "Cleaned Training Sample": "200,000 stratified samples",
    "Number of Trees (n_estimators)": 30,
    "Max Depth": 15,
    "Min Samples Split": 5,
    "Random State": 42,
    "Input Feature Count": 78,
    "Scaling Applied in Final Model": "None (Tree-based ensemble on raw cleaned features)",
    "Target Classes": 14
}
