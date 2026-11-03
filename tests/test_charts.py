"""
Tests for the Altair charts: the numbers and highlights they carry, not how they look.
"""

import json

import pandas as pd

from src.charts import ACCENT, MUTED, band_chart, tenure_chart

RATES = pd.Series({"Low": 40.0, "Mid": 55.0, "High": 60.0})


def _spec(chart):
    return json.dumps(chart.to_dict())


def test_band_chart_keeps_band_order_and_highlights_above_overall():
    encoding = band_chart(RATES, overall=50.0, axis_title="Band").to_dict()["layer"][0]["encoding"]

    assert encoding["y"]["sort"] == ["Low", "Mid", "High"]
    assert encoding["color"]["condition"]["value"] == ACCENT
    assert encoding["color"]["value"] == MUTED
    assert "datum.rate > 50.0" in encoding["color"]["condition"]["test"]


def test_band_chart_draws_the_overall_line_and_labels_only_the_highest_band():
    spec = band_chart(RATES, overall=50.0, axis_title="Band").to_dict()

    assert spec["layer"][1]["encoding"]["x"]["datum"] == 50.0
    assert "datum.rate === 60.0" in json.dumps(spec["layer"][2]["transform"])


def test_band_chart_leaves_out_empty_bands():
    chart = band_chart(pd.Series({"Low": 40.0, "Empty": None, "High": 60.0}), overall=50.0, axis_title="Band")
    assert '"Empty"' not in _spec(chart)


def test_tenure_chart_labels_the_peak_month():
    tenure = pd.DataFrame({"months": [9, 10, 11, 12], "rate": [29.0, 40.0, 65.1, 61.0], "customers": [10, 20, 30, 40]})
    assert "Month 11: 65%" in _spec(tenure_chart(tenure, overall=50.0))
