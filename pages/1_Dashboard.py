# =========================================
# pages/1_Dashboard.py — Analytics Dashboard
# =========================================

import pandas as pd
import streamlit as st

from src.charts import band_chart, tenure_chart
from src.preprocess import churn_rate_by_band, load_customer_columns
from src.ui import apply_page_style

apply_page_style()

# -----------------------------------------
# PAGE HEADER
# -----------------------------------------
st.markdown("""
<h2 style="margin-bottom:4px;">Analytics Dashboard</h2>
<p style="color:#94A3B8; margin-top:0;">
Customer base and churn patterns in the 100,000-customer dataset
</p>
""", unsafe_allow_html=True)


# -----------------------------------------
# DATA LOADING (CACHED)
# -----------------------------------------
@st.cache_data
def load_dashboard_data():
    return load_customer_columns(["churn", "months", "eqpdays", "mou_Mean", "change_mou", "rev_Mean"])


df = load_dashboard_data()
overall = df["churn"].mean() * 100

# -----------------------------------------
# KPI SECTION
# -----------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total customers", f"{df.shape[0]:,}")
kpi2.metric("Churn in sample", f"{overall:.1f}%")
kpi3.metric("Median tenure", f"{df['months'].median():.0f} months")
kpi4.metric("Average monthly revenue", f"${df['rev_Mean'].mean():.2f}")

st.caption(
    "This dataset is almost evenly split between churned and retained customers, "
    "so its churn rate should not be read as a real company's churn rate."
)

# -----------------------------------------
# THE MAIN FINDING
# -----------------------------------------
tenure = (
    df[df["months"] <= 36]
    .groupby("months")["churn"]
    .agg(rate="mean", customers="size")
    .reset_index()
    .assign(rate=lambda frame: frame["rate"] * 100)
)
peak = tenure.loc[tenure["rate"].idxmax()]
before_peak = tenure[tenure["months"] < peak["months"]]
low = before_peak.loc[before_peak["rate"].idxmin()]

with st.container(border=True):
    hero_col, chart_col = st.columns([1, 2.6], gap="large")

    with hero_col:
        st.markdown(f"""
        <div class="hero-block">
            <div class="hero-eyebrow">Sharpest pattern in the data</div>
            <div class="hero-figure">{peak['rate']:.0f}%</div>
            <div class="hero-text">of customers at month {peak['months']:.0f} churned, up from {low['rate']:.0f}% at month {low['months']:.0f}.</div>
            <div class="hero-note">This fits contracts ending near one year, but the data does not record contract terms.</div>
        </div>
        """, unsafe_allow_html=True)

    with chart_col:
        st.markdown("##### Churn by tenure")
        st.caption(f"Month by month for the first three years. The line marks overall churn ({overall:.1f}%).")
        st.altair_chart(tenure_chart(tenure, overall), use_container_width=True, theme=None)

# -----------------------------------------
# WHAT ELSE MOVES CHURN
# -----------------------------------------
st.markdown("### What else moves churn")
st.caption(f"The line marks overall churn ({overall:.1f}%). Bars above it are blue, and the rest are gray.")

handset_age = churn_rate_by_band(
    df, "eqpdays",
    bins=[-10, 90, 180, 270, 365, 730, 4000],
    labels=["0-90", "91-180", "181-270", "271-365", "366-730", "731+"],
)
minutes = churn_rate_by_band(
    df, "mou_Mean",
    bins=[0, 100, 250, 500, 1000, 20000],
    labels=["0-100", "101-250", "251-500", "501-1000", "1001+"],
)
usage_change = churn_rate_by_band(
    df, "change_mou",
    bins=[-5000, -300, -100, -20, 20, 100, 300, 50000],
    labels=["Below -300", "-300 to -100", "-100 to -20", "-20 to 20", "20 to 100", "100 to 300", "Above 300"],
)

col1, col2, col3 = st.columns(3)

with col1, st.container(border=True):
    st.markdown("##### Handset age")
    st.altair_chart(band_chart(handset_age, overall, "Days with current handset"), use_container_width=True, theme=None)

with col2, st.container(border=True):
    st.markdown("##### Monthly minutes")
    st.altair_chart(band_chart(minutes, overall, "Average minutes per month"), use_container_width=True, theme=None)

with col3, st.container(border=True):
    st.markdown("##### Change in usage")
    st.altair_chart(band_chart(usage_change, overall, "Change in monthly minutes"), use_container_width=True, theme=None)

# -----------------------------------------
# DASHBOARD INSIGHT SUMMARY
# -----------------------------------------
st.markdown(f"""
<div class="soft-card">
<h4>📌 What the Data Shows</h4>
<ul>
<li><b>Handset age:</b> churn is {handset_age['181-270']:.0f}% at 181-270 days and {handset_age['271-365']:.0f}% at 271-365 days</li>
<li><b>Usage level:</b> churn is {minutes['0-100']:.0f}% for the lightest users and {minutes['1001+']:.0f}% for the heaviest</li>
<li><b>Falling usage:</b> churn is {usage_change['Below -300']:.0f}% after a large drop in minutes, and {usage_change['20 to 100']:.0f}% after a modest rise</li>
</ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------
# TABLE VIEW
# -----------------------------------------
with st.expander("View the chart data as tables"):
    tenure_table = tenure.rename(columns={"months": "Tenure (months)", "rate": "Churn rate (%)", "customers": "Customers"})
    bands_table = pd.concat(
        rates.rename("Churn rate (%)").rename_axis("Band").reset_index().assign(Chart=name)
        for name, rates in (("Handset age (days)", handset_age), ("Monthly minutes", minutes), ("Change in monthly minutes", usage_change))
    )[["Chart", "Band", "Churn rate (%)"]]

    table_left, table_right = st.columns(2)
    table_left.dataframe(tenure_table.round(1), hide_index=True, use_container_width=True)
    table_right.dataframe(bands_table.round(1), hide_index=True, use_container_width=True)
