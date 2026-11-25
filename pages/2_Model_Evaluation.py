"""
NetSentry - Model Evaluation & Diagnostic Matrix
Objective quantitative evaluation against ground-truth datasets.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from utils.model_utils import (
    load_model,
    get_model_features,
    get_model_classes,
    validate_and_prepare_input
)
from utils.theme_utils import inject_enterprise_theme, render_enterprise_sidebar

st.set_page_config(
    page_title="Model Evaluation | NetSentry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply refined enterprise theme & sidebar
inject_enterprise_theme()
render_enterprise_sidebar(current_page="Model Evaluation")

model = load_model()
features = get_model_features(model)
classes = get_model_classes(model)

# Header Section
st.markdown(
    """
    <div style="margin-bottom: 0.4rem;">
        <h1 style="margin: 0;">Model Diagnostic & Evaluation Matrix</h1>
        <p style="color: #94A3B8; font-size: 0.88rem; margin-top: 0.15rem; margin-bottom: 1.1rem; line-height: 1.45;">
            Empirical validation of the trained Random Forest Classifier. All evaluation metrics, confusion matrices, 
            and classification reports are computed strictly against <strong>authentic ground-truth labels</strong>.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Benchmark Evaluation Context Notice
st.markdown(
    """
    <div class="ns-banner-info">
        <div style="font-weight: 600; font-size: 0.82rem; margin-bottom: 0.15rem; color: #93C5FD;">EVALUATION DATASET DISCLOSURE</div>
        <div style="font-size: 0.78rem; color: #BFDBFE; line-height: 1.4;">
            Evaluating small sample batches will reflect the class distribution of that specific sample rather than the full 2.83M CICIDS2017 test set. 
            NetSentry never fabricates static 100% metrics: all numbers below are dynamically computed from the chosen ground-truth source.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Evaluation Source Selector
st.markdown(
    """
    <div style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #94A3B8; margin-bottom: 0.35rem;">
        Ground-Truth Evaluation Source
    </div>
    """,
    unsafe_allow_html=True
)

eval_source = st.radio(
    "Select evaluation dataset source:",
    [
        "Use Built-in Benchmark Sample (sample_data/sample_benchmark_eval.csv)",
        "Upload Custom Ground-Truth Labeled CSV (Must include 'Label' + 78 features)",
        "Use Ingested Batch from Threat Analysis Workspace (if previously uploaded with Label)"
    ],
    index=0,
    label_visibility="collapsed"
)

df_eval = None
eval_source_label = ""

if eval_source.startswith("Use Built-in"):
    bench_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_benchmark_eval.csv")
    if os.path.exists(bench_path):
        df_eval = pd.read_csv(bench_path)
        eval_source_label = f"Local Benchmark Sample ({df_eval.shape[0]} records)"

elif eval_source.startswith("Upload Custom"):
    uploaded_eval = st.file_uploader("Upload Labeled Test CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_eval is not None:
        try:
            df_eval = pd.read_csv(uploaded_eval, low_memory=False)
            eval_source_label = f"Uploaded Test CSV: {uploaded_eval.name} ({df_eval.shape[0]} records)"
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")

elif eval_source.startswith("Use Ingested"):
    if "last_detection_y_true" in st.session_state and "last_detection_results" in st.session_state:
        last_results = st.session_state["last_detection_results"]["results_df"].copy()
        last_results["Label"] = st.session_state["last_detection_y_true"].values
        df_eval = last_results
        eval_source_label = f"Session Telemetry Batch ({df_eval.shape[0]} records)"
    else:
        st.markdown(
            """
            <div class="ns-banner-attack" style="margin-top: 0.5rem;">
                No ground-truth session data located. Please upload a CSV containing a 'Label' column in the Threat Analysis Workspace first.
            </div>
            """,
            unsafe_allow_html=True
        )

# Execute Quantitative Validation
if df_eval is not None:
    X_ready, y_true, missing_cols, warnings = validate_and_prepare_input(df_eval, model=model)

    if missing_cols:
        st.error(f"Dataset missing required features: {missing_cols}")
    elif y_true is None:
        st.markdown(
            """
            <div class="ns-banner-attack">
                <strong>NO GROUND-TRUTH LABELS FOUND:</strong> The provided dataset does not contain a 'Label' column. 
                Evaluation metrics, precision/recall calculations, and confusion matrices cannot be computed without verified labels.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Run real model inference
        y_pred = model.predict(X_ready)

        # Calculate actual sklearn metrics
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
                <div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF;">Quantitative Performance Indicators</div>
                <span class="ns-badge ns-badge-neutral">{eval_source_label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""
                <div class="ns-metric-card">
                    <div class="ns-metric-label">
                        <span>Accuracy Score</span>
                        <span style="font-size: 0.8rem;">🎯</span>
                    </div>
                    <div class="ns-metric-val" style="color: #60A5FA;">{acc*100:.2f}%</div>
                    <div class="ns-metric-sub">Correct Classifications</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"""
                <div class="ns-metric-card">
                    <div class="ns-metric-label">
                        <span>Weighted Precision</span>
                        <span style="font-size: 0.8rem;">🛡️</span>
                    </div>
                    <div class="ns-metric-val">{prec*100:.2f}%</div>
                    <div class="ns-metric-sub">False Positive Resistance</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f"""
                <div class="ns-metric-card">
                    <div class="ns-metric-label">
                        <span>Weighted Recall</span>
                        <span style="font-size: 0.8rem;">📡</span>
                    </div>
                    <div class="ns-metric-val">{rec*100:.2f}%</div>
                    <div class="ns-metric-sub">Threat Detection Rate</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with m4:
            st.markdown(
                f"""
                <div class="ns-metric-card">
                    <div class="ns-metric-label">
                        <span>Weighted F1-Score</span>
                        <span style="font-size: 0.8rem;">⚖️</span>
                    </div>
                    <div class="ns-metric-val">{f1*100:.2f}%</div>
                    <div class="ns-metric-sub">Harmonic Mean</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

        # Visual Analytics Tabs
        tab_cm, tab_corr, tab_report = st.tabs([
            "Confusion Matrix",
            "Top Feature Correlation Heatmap",
            "Classification Report & Class Diagnostics"
        ])

        with tab_cm:
            st.markdown(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF;">Multiclass Confusion Matrix</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">
                        Cross-tabulation comparing true labels against Random Forest predictions for the evaluated dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            present_labels = sorted(list(set(y_true.unique()).union(set(y_pred))))
            cm = confusion_matrix(y_true, y_pred, labels=present_labels)

            # Responsive height calculation: ensure cells don't truncate on laptop screens
            chart_height = max(380, min(550, len(present_labels) * 45 + 120))

            fig_cm = px.imshow(
                cm,
                labels=dict(x="Predicted Label", y="Ground Truth Label", color="Flows"),
                x=present_labels,
                y=present_labels,
                text_auto=True,
                color_continuous_scale="Blues",
                template="plotly_dark",
                aspect="auto"
            )
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(tickangle=35, tickfont=dict(size=10, color="#CBD5E1")),
                yaxis=dict(tickfont=dict(size=10, color="#CBD5E1")),
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                height=chart_height
            )
            st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})

        with tab_corr:
            st.markdown(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF;">Feature Correlation Heatmap</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">
                        Pearson correlation matrix computed across the 12 highest-variance numerical indicators in this dataset (Notebook Graph 5).
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            numeric_data = X_ready.select_dtypes(include=np.number)
            top_var_cols = numeric_data.var().nlargest(12).index.tolist()
            corr_matrix = numeric_data[top_var_cols].corr().round(2)

            fig_corr = px.imshow(
                corr_matrix,
                labels=dict(color="Pearson Corr"),
                x=top_var_cols,
                y=top_var_cols,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                template="plotly_dark",
                zmin=-1,
                zmax=1
            )
            fig_corr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(tickangle=35, tickfont=dict(size=10, color="#CBD5E1")),
                yaxis=dict(tickfont=dict(size=10, color="#CBD5E1")),
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                height=440
            )
            st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

        with tab_report:
            st.markdown(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF;">Per-Class Evaluation Breakdown</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">
                        Precision, recall, and F1-score computed for every class observed in the evaluation data.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            report_df = pd.DataFrame(report_dict).T.round(3)
            # Clean indices
            report_df.index.name = "Class Profile"
            st.dataframe(report_df, use_container_width=True)
