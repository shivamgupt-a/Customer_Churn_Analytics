"""
Integration and UI tests for Streamlit application pages using streamlit.testing.v1.AppTest.
Verifies all pages load without exceptions and the Predict page submits default values to return probabilities.
"""

import re

import pytest
from streamlit.testing.v1 import AppTest

from src.schema import EXAMPLE_HIGH_RISK, EXAMPLE_LOW_RISK, NUMERIC_FIELDS


@pytest.fixture
def default_timeout():
    return 30


def _submit(at):
    next(b for b in at.button if b.label.endswith("Predict Churn Risk")).click().run()


def test_app_shell_loads(default_timeout):
    """Verifies that the landing page loads and shows the measured results."""
    at = AppTest.from_file("Home.py", default_timeout=default_timeout).run()
    assert not at.exception, f"Home.py raised exception: {at.exception}"

    results = {m.label: m.value for m in at.metric}
    assert results["Test AUC"] == "0.683"
    assert results["Top 10% Who Churned"] == "77.5%"
    assert results["Churn Across All Customers"] == "49.6%"
    assert results["Model Inputs"] == "15"


def test_dashboard_page_loads(default_timeout):
    """Verifies that pages/1_Dashboard.py loads and computes executive KPIs without exceptions."""
    at = AppTest.from_file("pages/1_Dashboard.py", default_timeout=default_timeout).run()
    assert not at.exception, f"Dashboard page raised exception: {at.exception}"

    assert {m.label: m.value for m in at.metric}["Churn in sample"] == "49.6%"
    text_content = " ".join(m.value for m in at.markdown)
    assert "of customers at month 11 churned, up from 29% at month 9." in text_content


def test_predict_churn_page_loads_and_submits(default_timeout):
    """
    Verifies that pages/2_Predict_Churn.py:
    1. Loads cleanly without exceptions.
    2. Submits default customer input values via the predict button.
    3. Successfully calculates and renders a churn probability without exceptions.
    """
    at = AppTest.from_file("pages/2_Predict_Churn.py", default_timeout=default_timeout).run()
    assert not at.exception, f"Predict page failed to load: {at.exception}"

    # Click the form submission button with defaults
    _submit(at)

    assert not at.exception, f"Predict page raised exception on submit: {at.exception}"

    # Verify that prediction output rendered
    text_content = " ".join([m.value for m in at.markdown])
    assert "%" in text_content or "Risk" in text_content or "Score" in text_content, (
        "Expected churn probability or risk assessment in page output after submission."
    )


@pytest.mark.parametrize("customer, expected", [(EXAMPLE_HIGH_RISK, "High Risk"), (EXAMPLE_LOW_RISK, "Lower Priority")])
def test_predict_form_uses_the_entered_values(default_timeout, customer, expected):
    """Values typed into every field must reach the model and change the result."""
    at = AppTest.from_file("pages/2_Predict_Churn.py", default_timeout=default_timeout).run()
    inputs = {n.label: n for n in at.number_input}
    assert len(inputs) == len(NUMERIC_FIELDS)
    for name, spec in NUMERIC_FIELDS.items():
        inputs[spec["label"]].set_value(customer[name])
    at.selectbox[0].set_value(customer["asl_flag"])
    _submit(at)

    assert not at.exception, f"Predict page raised exception on submit: {at.exception}"
    assert expected in " ".join(m.value for m in at.markdown)


@pytest.mark.parametrize("label, customer, expected", [
    ("high-risk", EXAMPLE_HIGH_RISK, "High Risk"),
    ("lower-priority", EXAMPLE_LOW_RISK, "Lower Priority"),
])
def test_example_buttons_fill_the_form_and_score_it(default_timeout, label, customer, expected):
    """One click must show a recruiter a full result, with the form showing the values used."""
    at = AppTest.from_file("pages/2_Predict_Churn.py", default_timeout=default_timeout).run()
    next(b for b in at.button if label in b.label).click().run()

    assert not at.exception, f"Example button raised exception: {at.exception}"
    assert expected in " ".join(m.value for m in at.markdown)
    fields = {n.label: n.value for n in at.number_input}
    for name, spec in NUMERIC_FIELDS.items():
        assert fields[spec["label"]] == customer[name], name
    assert at.selectbox[0].value == customer["asl_flag"]


def test_predict_does_not_show_score_as_percent(default_timeout):
    """Scores are uncalibrated, so they must not read like a percent chance of churning."""
    at = AppTest.from_file("pages/2_Predict_Churn.py", default_timeout=default_timeout).run()
    _submit(at)

    assert not at.exception, f"Predict page raised exception on submit: {at.exception}"
    text_content = " ".join(m.value for m in at.markdown)
    assert "Churn Risk Score" in text_content
    assert not re.search(r"\d\.\d%", text_content), "Score or cutoff shown as a percentage"


def test_insights_page_loads(default_timeout):
    """Verifies that pages/3_Insights.py loads and displays risk factor analyses without exceptions."""
    at = AppTest.from_file("pages/3_Insights.py", default_timeout=default_timeout).run()
    assert not at.exception, f"Insights page raised exception: {at.exception}"


def test_model_info_page_loads(default_timeout):
    """Verifies that pages/4_Model_Info.py loads and displays model architecture and metrics without exceptions."""
    at = AppTest.from_file("pages/4_Model_Info.py", default_timeout=default_timeout).run()
    assert not at.exception, f"Model Info page raised exception: {at.exception}"


def test_monitoring_page_separates_healthy_data_from_drift():
    """It opens on the healthy baseline, simulated drift alerts, and an empty log asks for more data."""
    at = AppTest.from_file("pages/6_Monitoring.py", default_timeout=120).run()
    assert not at.exception, f"Monitoring page failed to load: {at.exception}"
    assert len(at.success) == 1 and not at.error

    at.radio[0].set_value("Simulated drift (demo)").run()
    assert not at.exception, f"Monitoring page raised exception: {at.exception}"
    assert len(at.error) == 1 and "mou_Mean" in at.error[0].value

    at.radio[0].set_value("Logged predictions").run()
    assert not at.exception, f"Monitoring page raised exception: {at.exception}"
    assert len(at.info) == 1 and not at.error


def test_about_page_loads(default_timeout):
    """Verifies that pages/5_About.py loads documentation without exceptions."""
    at = AppTest.from_file("pages/5_About.py", default_timeout=default_timeout).run()
    assert not at.exception, f"About page raised exception: {at.exception}"
