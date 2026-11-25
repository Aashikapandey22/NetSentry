"""
NetSentry UI & Layout Engine (v3.0 Refined)
Provides enterprise cybersecurity styling, unified sidebar architecture,
and consistent layout tokens across all pages.
Compatible with all legacy and updated module imports.
"""

import os
import streamlit as st
from utils.model_utils import load_model, get_model_features, get_model_classes


def inject_enterprise_theme():
    """Injects the enterprise cybersecurity CSS stylesheet."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_enterprise_sidebar(current_page: str = "Overview"):
    """
    Renders a compact, elegant enterprise SOC sidebar with shield branding,
    navigation links with clean SVG icons, and a compact system health status indicator.
    """
    with st.sidebar:
        # Header Branding - Clean, modern cyber logo
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.15rem;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 6V12C3 17.52 6.84 22.74 12 24C17.16 22.74 21 17.52 21 12V6L12 2Z" fill="#1E3A8A" stroke="#3B82F6" stroke-width="1.5" stroke-linejoin="round"/>
                    <path d="M9 12L11 14L15 10" stroke="#FFFFFF" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em; line-height: 1.1;">NETSENTRY</div>
                    <div style="font-size: 0.65rem; color: #64748B; font-weight: 600; letter-spacing: 0.05em;">SECURITY INTELLIGENCE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption("Enterprise NIDS Machine Learning Platform")
        st.markdown("<div style='height: 1px; background-color: #1E2D4A; margin: 0.65rem 0;'></div>", unsafe_allow_html=True)

        # Quick Navigation Links with Icons
        nav_items = [
            ("Overview", "/", "📊"),
            ("Intrusion Detection", "/Intrusion_Detection", "🛡️"),
            ("Model Evaluation", "/Model_Evaluation", "📈"),
            ("Feature Importance", "/Feature_Importance", "🧬"),
            ("About Project", "/About_Project", "ℹ️"),
        ]

        st.markdown(
            """
            <div style="font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; margin-bottom: 0.4rem;">
                Core Modules
            </div>
            """,
            unsafe_allow_html=True
        )

        # Render styled navigation links matching active page
        for name, path, icon in nav_items:
            is_active = (current_page.lower() == name.lower())
            active_style = (
                "background-color: rgba(37, 99, 235, 0.15); color: #60A5FA; border-left: 3px solid #2563EB; font-weight: 600;"
                if is_active
                else "color: #94A3B8; font-weight: 500;"
            )
            st.markdown(
                f"""
                <a href="{path}" target="_self" style="display: flex; align-items: center; gap: 0.6rem; text-decoration: none; padding: 0.45rem 0.65rem; border-radius: 5px; font-size: 0.82rem; margin-bottom: 2px; {active_style} transition: all 0.15s ease;">
                    <span style="font-size: 0.9rem;">{icon}</span>
                    <span>{name}</span>
                </a>
                """,
                unsafe_allow_html=True
            )

        # Query model status
        try:
            model = load_model()
            n_features = len(get_model_features(model))
            n_classes = len(get_model_classes(model))
            is_online = True
            err_msg = ""
        except Exception as e:
            is_online = False
            err_msg = str(e)
            n_features = 0
            n_classes = 0

        # System Status Block at the bottom of sidebar
        status_color = "#10B981" if is_online else "#EF4444"
        status_text = "Operational" if is_online else "Engine Offline"
        status_sub = f"RF • {n_features} Features • {n_classes} Classes" if is_online else err_msg[:25]

        st.markdown(
            f"""
            <div class="ns-sidebar-status">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <div style="font-size: 0.68rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Engine Status</div>
                    <div style="display: flex; align-items: center; gap: 0.35rem;">
                        <span style="height: 6px; width: 6px; background-color: {status_color}; border-radius: 50%; display: inline-block;"></span>
                        <span style="font-size: 0.72rem; font-weight: 600; color: {status_color};">{status_text}</span>
                    </div>
                </div>
                <div style="font-size: 0.68rem; color: #64748B; font-family: 'JetBrains Mono', monospace;">{status_sub}</div>
                <div style="margin-top: 0.35rem; font-size: 0.65rem; color: #475569;">CICIDS2017 Benchmark • v3.0</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ==============================================================================

def apply_theme_css():
    """Alias for inject_enterprise_theme for backward compatibility."""
    inject_enterprise_theme()
    return "plotly_dark"


def render_sidebar():
    """Alias for render_enterprise_sidebar for backward compatibility."""
    render_enterprise_sidebar()


def init_theme():
    pass


def get_current_theme():
    return "Dark"
