"""
Interactive Altair charts for the analytics pages.
ACCENT passes the dataviz palette validator on the page surface. The theme's teal fails its brightness check.
"""

import altair as alt
import pandas as pd

ACCENT = "#3987e5"
MUTED = "#64748B"
REFERENCE = "#94A3B8"
AXIS_TEXT = "#CBD5E1"
INK = "#E2E8F0"
GRID = "#233554"
SURFACE = "#0A192F"


def _style(chart: alt.LayerChart, height: int) -> alt.LayerChart:
    return (
        chart.properties(height=height, background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=AXIS_TEXT,
            titleColor=AXIS_TEXT,
            gridColor=GRID,
            domainColor=GRID,
            tickColor=GRID,
            labelFontSize=12,
            titleFontSize=12,
            titleFontWeight="normal",
        )
    )


def band_chart(rates: pd.Series, overall: float, axis_title: str, height: int = 260) -> alt.LayerChart:
    """Churn rate per ordered band, first band on top. Bars above the overall rate take the accent, and only the highest is labelled."""
    data = rates.dropna().rename_axis("band").reset_index(name="rate")
    data["band"] = data["band"].astype(str)
    order = data["band"].tolist()
    data["label"] = data["rate"].map("{:.0f}%".format)

    category_axis = alt.Axis(grid=False, labelLimit=120, ticks=False)
    value_axis = alt.Axis(tickCount=5, domain=False, ticks=False)
    value_scale = alt.Scale(domain=[0, data["rate"].max() + 10])
    tooltip = [alt.Tooltip("band:N", title=axis_title), alt.Tooltip("rate:Q", title="Churn rate (%)", format=".1f")]

    position = {
        "y": alt.Y("band:N", sort=order, title=axis_title, axis=category_axis),
        "x": alt.X("rate:Q", title="Churn rate (%)", scale=value_scale, axis=value_axis),
    }

    base = alt.Chart(data)
    bars = base.mark_bar(size=14, cornerRadiusEnd=4).encode(
        color=alt.condition(alt.datum.rate > overall, alt.value(ACCENT), alt.value(MUTED)),
        tooltip=tooltip,
        **position,
    )
    rule = alt.Chart(pd.DataFrame({"unused": [0]})).mark_rule(color=REFERENCE, strokeWidth=1).encode(x=alt.datum(overall))
    peak = (
        base.transform_filter(alt.datum.rate == float(data["rate"].max()))
        .mark_text(color=INK, fontSize=13, fontWeight="bold", align="left", dx=6)
        .encode(text="label:N", **position)
    )
    return _style(alt.layer(bars, rule, peak), height)


def tenure_chart(tenure: pd.DataFrame, overall: float, height: int = 330) -> alt.LayerChart:
    """Churn by month of tenure, with a hover crosshair and the peak labelled. Needs months, rate and customers columns."""
    first, last = int(tenure["months"].min()), int(tenure["months"].max())
    x = alt.X(
        "months:Q",
        title="Tenure (months)",
        scale=alt.Scale(domain=[first, last], nice=False),
        axis=alt.Axis(values=list(range(first, last + 1, 3)), format="d", grid=False, ticks=False),
    )
    y = alt.Y(
        "rate:Q",
        title="Churn rate (%)",
        scale=alt.Scale(domain=[0, tenure["rate"].max() + 12]),
        axis=alt.Axis(tickCount=5, domain=False, ticks=False),
    )
    tooltip = [
        alt.Tooltip("months:Q", title="Tenure (months)"),
        alt.Tooltip("rate:Q", title="Churn rate (%)", format=".1f"),
        alt.Tooltip("customers:Q", title="Customers", format=","),
    ]
    hover = alt.selection_point(fields=["months"], nearest=True, on="mouseover", empty=False, clear="mouseout")

    peak_row = tenure.loc[tenure["rate"].idxmax()]
    peak_data = pd.DataFrame([{**peak_row.to_dict(), "label": f"Month {int(peak_row['months'])}: {peak_row['rate']:.0f}%"}])

    base = alt.Chart(tenure)
    area = base.mark_area(color=ACCENT, opacity=0.10).encode(x=x, y=y)
    line = base.mark_line(color=ACCENT, strokeWidth=2, strokeCap="round", strokeJoin="round").encode(x=x, y=y)
    overall_rule = alt.Chart(pd.DataFrame({"unused": [0]})).mark_rule(color=REFERENCE, strokeWidth=1).encode(y=alt.datum(overall))
    crosshair = base.mark_rule(color=REFERENCE, strokeWidth=1).encode(
        x=x, opacity=alt.condition(hover, alt.value(0.8), alt.value(0))
    )
    # Wider than the visible line, so hovering anywhere near a month finds it
    hit_area = base.mark_rule(strokeWidth=24, opacity=0).encode(x=x, tooltip=tooltip).add_params(hover)
    hover_dot = base.mark_point(filled=True, size=90, color=ACCENT, stroke=SURFACE, strokeWidth=2, opacity=1).encode(
        x=x, y=y, opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )
    peak_dot = alt.Chart(peak_data).mark_point(filled=True, size=90, color=ACCENT, stroke=SURFACE, strokeWidth=2, opacity=1).encode(x=x, y=y)
    peak_label = alt.Chart(peak_data).mark_text(
        color=INK, fontSize=13, fontWeight="bold", align="left", dx=10, dy=-4
    ).encode(x=x, y=y, text="label:N")

    return _style(alt.layer(area, overall_rule, line, crosshair, hit_area, hover_dot, peak_dot, peak_label), height)
