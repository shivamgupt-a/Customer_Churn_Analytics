"""
Shared page setup for the Streamlit app.
"""

from typing import Any, Dict, Tuple

import matplotlib as mpl
import numpy as np
import streamlit as st
from cycler import cycler

CHART_STYLE = {
    "figure.facecolor": "#0A192F",
    "savefig.facecolor": "#0A192F",
    "axes.facecolor": "#0A192F",
    "axes.edgecolor": "#475569",
    "axes.labelcolor": "#CBD5E1",
    "axes.titlecolor": "#E2E8F0",
    "text.color": "#E2E8F0",
    "xtick.color": "#CBD5E1",
    "ytick.color": "#CBD5E1",
    "grid.color": "#334155",
    "axes.prop_cycle": cycler(color=["#3987e5"]),
}


def top_decile_stats(metrics: Dict[str, Any]) -> Tuple[int, float, float]:
    """Returns customers flagged in the top 10%, the % of them who churned, and the % churned overall."""
    test_customers = metrics["test_support_0"] + metrics["test_support_1"]
    flagged = int(np.ceil(test_customers * 0.10))
    flagged_rate = metrics["churners_caught_in_top_10"] / flagged * 100
    overall_rate = metrics["total_churners_in_test"] / test_customers * 100
    return flagged, flagged_rate, overall_rate


def apply_page_style() -> None:
    """
    Sets page config and shared CSS. Call first on every page:
    Streamlit runs only the selected page's script, never Home.py as well.
    Colors come from the theme in .streamlit/config.toml.
    """
    mpl.rcParams.update(CHART_STYLE)
    st.set_page_config(
        page_title="Customer Churn Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto",  # expanded would cover the whole page on phones
    )
    st.markdown(
        """
        <style>
        [data-testid="stMetric"] {
            padding: 14px 18px;
            border: 1px solid rgba(250, 250, 250, 0.2);
            border-radius: 8px;
        }
        .hero-block {
            padding: 12px 0;
        }
        .hero-eyebrow {
            color: #94A3B8;
            font-size: 0.85rem;
        }
        .hero-figure {
            color: #FFFFFF;
            font-size: 4.5rem;
            font-weight: 600;
            line-height: 1.15;
        }
        .hero-text {
            color: #E2E8F0;
            font-size: 1.05rem;
            line-height: 1.45;
            margin-bottom: 12px;
        }
        .hero-note {
            color: #94A3B8;
            font-size: 0.85rem;
            line-height: 1.45;
        }
        .soft-card, .section-card {
            padding: 16px 20px;
            border-radius: 14px;
            margin-bottom: 16px;
        }
        .soft-card {
            background-color: #112240;
            border: 1px solid #233554;
        }
        .section-card {
            background: linear-gradient(135deg, #312E81, #4338CA);
            color: white;
        }
        section[data-testid="stSidebar"] a {
            color: #CBD5F5;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            margin: 6px 10px;
            border-radius: 14px;
            font-weight: 500;
            transition: all 0.25s ease;
            text-decoration: none;
        }
        section[data-testid="stSidebar"] a:hover {
            background: linear-gradient(135deg, #312E81, #4338CA);
            color: #C7D2FE;
            transform: translateX(4px);
            box-shadow: 0 6px 16px rgba(79,70,229,0.15);
        }
        section[data-testid="stSidebar"] a[aria-current="page"] {
            background: linear-gradient(135deg, #4F46E5, #6366F1);
            color: white;
            box-shadow: 0 12px 30px rgba(79,70,229,0.35);
        }
        section[data-testid="stSidebar"] a[aria-current="page"] svg {
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
