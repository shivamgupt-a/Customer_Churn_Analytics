# ===============================
# Home.py — Landing Page
# ===============================

import json

import streamlit as st

from src import PROJECT_ROOT
from src.schema import MODEL_FEATURES
from src.ui import apply_page_style, top_decile_stats

# -------------------------------
# 1️⃣ PAGE CONFIG & STYLE (MUST BE FIRST)
# -------------------------------
apply_page_style()

# --------------------------------
# 2️⃣ WHAT THIS IS
# --------------------------------
st.title("📊 Customer Churn Analytics")
st.markdown(
    "Predicts which telecom customers are likely to leave, and explains why. "
    "A two-person portfolio project, trained on 100,000 records from a public dataset."
)

st.page_link("pages/2_Predict_Churn.py", label="Try a prediction", icon="🔮")

st.markdown("---")


# --------------------------------
# 3️⃣ RESULTS
# --------------------------------
@st.cache_data
def load_metrics():
    with open(PROJECT_ROOT / "models" / "metrics.json", "r") as f:
        return json.load(f)


metrics = load_metrics()
flagged, flagged_rate, overall_rate = top_decile_stats(metrics)

st.markdown("### 📈 Results on Unseen Customers")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Test AUC", f"{metrics['auc']:.3f}")
col2.metric("Top 10% Who Churned", f"{flagged_rate:.1f}%")
col3.metric("Churn Across All Customers", f"{overall_rate:.1f}%")
col4.metric("Model Inputs", len(MODEL_FEATURES))

st.caption(
    f"Measured on {metrics['test_support_0'] + metrics['test_support_1']:,} customers the model never saw. "
    "This dataset is evenly split between churned and retained customers, so its churn rate is not a real company's."
)

st.markdown("---")

# --------------------------------
# 4️⃣ WHERE TO GO
# --------------------------------
st.markdown("### 🧭 Explore")

left, right = st.columns(2)

with left:
    st.page_link("pages/2_Predict_Churn.py", label="Predict Churn", icon="🔮")
    st.caption("Score a customer and see which factors drove the result.")
    st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
    st.caption("Churn by tenure, handset age and usage.")
    st.page_link("pages/3_Insights.py", label="Insights", icon="🔎")
    st.caption("The patterns that stand out, including a sharp jump near one year.")

with right:
    st.page_link("pages/4_Model_Info.py", label="Model Info", icon="🎯")
    st.caption("Test results, risk cutoffs and which inputs matter most.")
    st.page_link("pages/6_Monitoring.py", label="Monitoring", icon="📡")
    st.caption("Checks whether new customers still resemble the training data.")
    st.page_link("pages/5_About.py", label="About", icon="ℹ️")
    st.caption("How the project was built, and what was learned.")

# --------------------------------
# 5️⃣ FOOTER
# --------------------------------
st.markdown(
    """
    <div style="
        margin-top:40px;
        padding:20px;
        border-radius:14px;
        background:linear-gradient(135deg,#0F172A,#1E293B);
        color:#E5E7EB;
        text-align:center;
    ">
        <small>
        © 2026 Customer Churn Analytics • Portfolio Project
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
