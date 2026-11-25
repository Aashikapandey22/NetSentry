"""
NetSentry - Technical Project Documentation & Specification
Executive architecture report and machine learning design specifications.
"""

import os
import streamlit as st
import pandas as pd
from utils.model_utils import (
    load_model,
    get_model_features,
    get_model_classes,
    MODEL_PARAMETERS_SUMMARY
)
from utils.theme_utils import inject_enterprise_theme, render_enterprise_sidebar

st.set_page_config(
    page_title="Technical Documentation | NetSentry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply refined enterprise theme & sidebar
inject_enterprise_theme()
render_enterprise_sidebar(current_page="About Project")

model = load_model()
features = get_model_features(model)
classes = get_model_classes(model)

# Header Section
st.markdown(
    """
    <div style="margin-bottom: 0.4rem;">
        <h1 style="margin: 0;">Technical Architecture & Specification</h1>
        <p style="color: #94A3B8; font-size: 0.88rem; margin-top: 0.15rem; margin-bottom: 1.1rem; line-height: 1.45;">
            Engineering specification and design documentation for the NetSentry Machine Learning Intrusion Detection System.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(
        """
        <div class="ns-card">
            <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.4rem;">1. Problem Formulation & Objective</div>
            <p style="color: #94A3B8; font-size: 0.82rem; line-height: 1.6; margin-bottom: 0.65rem;">
                Enterprise Security Operations Centers (SOCs) face overwhelming alert fatigue from high-throughput network perimeters. 
                Legacy signature-based network intrusion detection systems struggle with zero-day mutations, protocol obfuscation, and volumetric DDoS spikes.
            </p>
            <p style="color: #94A3B8; font-size: 0.82rem; line-height: 1.6; margin-bottom: 0;">
                <strong>NetSentry</strong> provides supervised machine-learning-based network flow triage. By classifying statistical packet header metrics, 
                it differentiates legitimate flows from 13 distinct multi-vector cyber attack profiles without requiring deep packet payload inspection (DPI).
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="ns-card">
            <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.4rem;">2. Data Cleaning & Sanitization Pipeline</div>
            <p style="color: #94A3B8; font-size: 0.82rem; line-height: 1.6; margin-bottom: 0.45rem;">
                Extracted directly from the workflow documented in <code>NetSentry_Network_Intrusion_Detection.ipynb</code>:
            </p>
            <ul style="color: #94A3B8; font-size: 0.82rem; line-height: 1.6; padding-left: 1.1rem; margin-bottom: 0;">
                <li><strong style="color: #E2E8F0;">Column Normalization:</strong> Stripped leading/trailing whitespace and removed UTF-8 Byte Order Marks (<code>\\ufeff</code>).</li>
                <li><strong style="color: #E2E8F0;">Infinite Value Remediation:</strong> Zero-duration flows produced division-by-zero artifacts in rate calculations (e.g. <code>Flow Bytes/s</code>). These were converted to <code>NaN</code> and safely excised.</li>
                <li><strong style="color: #E2E8F0;">Deduplication:</strong> Removed 308,381 duplicate telemetry records to avoid cross-split evaluation leakage.</li>
                <li><strong style="color: #E2E8F0;">Scale Invariance:</strong> Preserved raw integer and float units (microseconds, bytes, packets) without synthetic scaling, matching decision tree invariance.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="ns-card">
            <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.4rem;">3. Model Training & Hyperparameter Matrix</div>
        """,
        unsafe_allow_html=True
    )
    summary_df = pd.DataFrame(list(MODEL_PARAMETERS_SUMMARY.items()), columns=["Configuration Attribute", "Active Specification"])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="ns-card">
            <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.4rem;">4. Target Multiclass Threat Profiles ({len(classes)} Classes)</div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.4rem;">
        """,
        unsafe_allow_html=True
    )
    
    badge_html = []
    for c in classes:
        badge_class = "ns-badge-benign" if c == "BENIGN" else "ns-badge-attack"
        badge_html.append(f"<span class='ns-badge {badge_class}' style='font-size:0.72rem; padding:0.2rem 0.55rem;'>{c}</span>")
    
    st.markdown(" ".join(badge_html), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# Engineering Limitations and Scope
st.markdown(
    """
    <div class="ns-card">
        <div style="font-size: 0.92rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.4rem;">5. Engineering Limitations & Operational Scope</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #E2E8F0; margin-bottom: 0.3rem;">Model Inherent Constraints:</div>
                <ul style="color: #94A3B8; font-size: 0.8rem; line-height: 1.6; padding-left: 1.1rem; margin: 0;">
                    <li><strong>Class Imbalance Sensitivity:</strong> Extreme minority classes in CICIDS2017 (such as Heartbleed with only 11 instances or Infiltration with 36 instances) yield lower macro recall relative to abundant classes like DoS Hulk.</li>
                    <li><strong>Concept Drift:</strong> The model evaluates flows conforming to CICIDS2017 feature definitions; novel protocol variations require periodic retraining.</li>
                </ul>
            </div>
            <div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #E2E8F0; margin-bottom: 0.3rem;">Platform Implementation Scope:</div>
                <ul style="color: #94A3B8; font-size: 0.8rem; line-height: 1.6; padding-left: 1.1rem; margin: 0;">
                    <li><strong>Offline Batch Ingestion:</strong> Ingests network flow statistics generated by flow extractors (CICFlowMeter). Does not perform real-time kernel-level packet capture.</li>
                    <li><strong>Preserved Model Integrity:</strong> The serialized pickle binary (<code>NetSentry_RandomForest_Model.pkl</code>) is treated as immutable and never modified or retrained at runtime.</li>
                </ul>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
