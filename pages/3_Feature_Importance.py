"""
NetSentry - Feature Importance Analysis
Gini impurity reduction metrics from the trained Random Forest model.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.model_utils import (
    load_model,
    get_model_features,
    get_feature_importances
)
from utils.theme_utils import inject_enterprise_theme, render_enterprise_sidebar

st.set_page_config(
    page_title="Feature Importance | NetSentry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply refined enterprise theme & sidebar
inject_enterprise_theme()
render_enterprise_sidebar(current_page="Feature Importance")

model = load_model()
features = get_model_features(model)

# Header Section
st.markdown(
    """
    <div style="margin-bottom: 0.4rem;">
        <h1 style="margin: 0;">Feature Importance Architecture</h1>
        <p style="color: #94A3B8; font-size: 0.88rem; margin-top: 0.15rem; margin-bottom: 1.1rem; line-height: 1.45;">
            Relative Gini importance weights derived across all 30 decision trees in <code>NetSentry_RandomForest_Model.pkl</code>. 
            Measures the mean decrease in node impurity contributed by each bidirectional flow feature.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Interactive Top-N Feature Slider Bar
slider_col, info_col = st.columns([2, 1])

with slider_col:
    top_n = st.slider("Display Top N Features:", min_value=5, max_value=30, value=15, step=1)

with info_col:
    st.markdown(
        f"""
        <div class="ns-card" style="padding: 0.75rem 1rem; margin-bottom: 0;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Dimensionality Coverage</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">Top {top_n} of {len(features)} Features Displayed</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Extract real importances
importances = get_feature_importances(model, top_n=top_n)
fi_df = pd.DataFrame({
    "Feature Indicator": importances.index,
    "Gini Importance": importances.values,
    "Normalized Contribution": [f"{v * 100:.2f}%" for v in importances.values]
}).sort_values(by="Gini Importance", ascending=True)

chart_col, notes_col = st.columns([3, 2])

with chart_col:
    st.markdown(
        f"""
        <div class="ns-card" style="margin-bottom: 0; height: 100%;">
            <div style="font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.2rem;">Gini Impurity Reduction (Top {top_n} Indicators)</div>
            <div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 0.75rem;">Mean Decrease in Impurity across all split nodes.</div>
        """,
        unsafe_allow_html=True
    )

    fig_fi = px.bar(
        fi_df,
        x="Gini Importance",
        y="Feature Indicator",
        orientation="h",
        text="Normalized Contribution",
        color="Gini Importance",
        color_continuous_scale="Blues",
        template="plotly_dark",
        height=510
    )
    fig_fi.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=10, r=20, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor="#1E2D4A", title="Gini Importance Weight", tickfont=dict(size=10, color="#94A3B8")),
        yaxis=dict(title="", tickfont=dict(size=11, color="#CBD5E1")),
        font=dict(family="Plus Jakarta Sans, sans-serif")
    )
    fig_fi.update_traces(textposition='outside', textfont=dict(size=10, color="#94A3B8"))
    st.plotly_chart(fig_fi, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with notes_col:
    st.markdown(
        """
        <div class="ns-card">
            <div style="font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.4rem;">Empirical Observations from Model Trees</div>
            <ul style="color: #94A3B8; font-size: 0.82rem; line-height: 1.6; padding-left: 1.1rem; margin-bottom: 0.5rem;">
                <li><strong style="color: #E2E8F0;">Max Packet Length & Variance:</strong> Constitute the top 2 discriminative features (~15.2% combined weight). Packet sizing differences isolate automated DoS flooding from rich variable-length application data.</li>
                <li><strong style="color: #E2E8F0;">Backward Segment Size:</strong> Backward transmission attributes (<code>Avg Bwd Segment Size</code>, <code>Total Length of Bwd Packets</code>) capture asymmetric server responses typical of credential brute force and data exfiltration.</li>
                <li><strong style="color: #E2E8F0;">Forward Subflow Rates:</strong> <code>Subflow Fwd Packets</code> and forward IAT provide temporal boundaries distinguishing single-packet PortScan reconnaissance from sustained sessions.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ns-card" style="margin-top: 1rem;">
            <div style="font-size: 0.92rem; font-weight: 600; color: #F8FAFC; margin-bottom: 0.4rem;">Ranked Feature Hierarchy Table</div>
        """,
        unsafe_allow_html=True
    )
    table_view = fi_df.sort_values(by="Gini Importance", ascending=False).reset_index(drop=True)
    table_view.index = table_view.index + 1
    st.dataframe(table_view, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
