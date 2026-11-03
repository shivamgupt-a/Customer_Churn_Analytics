"""
Shared page setup for the Streamlit app.
"""

from typing import Any, Dict, Tuple

import numpy as np
import streamlit as st


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
    st.set_page_config(
        page_title="Customer Churn Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto",  # expanded would cover the whole page on phones
    )
    st.markdown(
        """
        <style>
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
