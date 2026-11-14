
"""SEISMOSCOPE | Year-at-a-glance earthquake activity calendar."""

from datetime import date
from math import log1p

import pandas as pd
import plotly.graph_objects as go


CALENDAR_COLORS = [
    [0.00, "#EAF7F4"],
    [0.15, "#CEEAE3"],
    [0.35, "#8CD0C6"],
    [0.55, "#43A9A2"],
    [0.75, "#1B777E"],
    [1.00, "#153D59"],
]


def create_calendar_heatmap(
    df: pd.DataFrame,
    year: int,
    visible_start: date,
    visible_end: date,
    scale_max: int | None = None,
) -> go.Figure:
    """
    Display daily earthquake counts in a calendar layout.

    Days are arranged Monday through Sunday.
    Colors use log(1 + count), while tooltips and
    colorbar labels show the original event counts.
    """

    if "event_date_utc" not in df.columns:
        raise ValueError(
            "Missing required column: event_date_utc"
        )

    if visible_end < visible_start:
        raise ValueError(
            "visible_end must be on or after visible_start"
        )

    event_dates = pd.to_datetime(
        df["event_date_utc"],
        errors="coerce"
    )

    daily_counts = (
        event_dates.dt.date.value_counts().to_dict()
    )

    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)

    first_monday = first_day - pd.Timedelta(
        days=first_day.weekday()
    )

    last_sunday = last_day + pd.Timedelta(
        days=6 - last_day.weekday()
    )

    weeks = (
        (last_sunday - first_monday).days // 7 + 1
    )

    background = [
        [None for _ in range(weeks)]
        for _ in range(7)
    ]

    intensity = [
        [None for _ in range(weeks)]
        for _ in range(7)
    ]

    details = [
        [["", 0] for _ in range(weeks)]
        for _ in range(7)
    ]

    # Build one cell for each day of the selected year.
    for day in pd.date_range(
        first_day,
        last_day,
        freq="D"
    ):

        current_date = day.date()

        week_index = (
            (current_date - first_monday).days // 7
        )

        weekday_index = current_date.weekday()

        # Gray means outside the available/selected period.
        if not (
            visible_start <= current_date <= visible_end
        ):
            background[weekday_index][week_index] = 0
            continue

        count = int(
            daily_counts.get(current_date, 0)
        )

        intensity[weekday_index][week_index] = (
            log1p(count)
        )

        details[weekday_index][week_index] = [
            current_date.strftime("%d %b %Y"),
            count
        ]

    fig = go.Figure()

    # Background layer for unavailable dates.
    fig.add_trace(
        go.Heatmap(
            z=background,
            x=list(range(weeks)),
            y=list(range(7)),
            colorscale=[
                [0, "#E2E8F0"],
                [1, "#E2E8F0"]
            ],
            showscale=False,
            xgap=3,
            ygap=3,
            hoverinfo="skip"
        )
    )

    # Keep colors comparable across years and regions.
    if scale_max is None:
        scale_max = max(
            daily_counts.values(),
            default=1
        )

    scale_max = max(1, int(scale_max))

    ticks = [0, 1, 2, 5, 10, 20, 50, 100, 150]
    ticks = [
        number for number in ticks
        if number <= scale_max
    ]

    # Main calendar heatmap.
    fig.add_trace(
        go.Heatmap(
            z=intensity,
            x=list(range(weeks)),
            y=list(range(7)),
            customdata=details,
            colorscale=CALENDAR_COLORS,
            zmin=0,
            zmax=log1p(scale_max),
            xgap=3,
            ygap=3,
            colorbar=dict(
                title=dict(
                    text="Events / day"
                ),
                thickness=12,
                len=0.86,
                tickvals=[
                    log1p(number)
                    for number in ticks
                ],
                ticktext=[
                    str(number)
                    for number in ticks
                ],
                outlinewidth=0
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]} recorded earthquakes"
                "<extra></extra>"
            ),
            name="Daily earthquake count"
        )
    )

    # Month labels at the top.
    month_starts = [
        date(year, month, 1)
        for month in range(1, 13)
    ]

    month_weeks = [
        (day - first_monday).days // 7
        for day in month_starts
    ]

    month_labels = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    fig.update_xaxes(
        side="top",
        tickmode="array",
        tickvals=month_weeks,
        ticktext=month_labels,
        range=[-0.5, weeks - 0.5],
        showgrid=False,
        showline=False,
        zeroline=False,
        ticks="",
        fixedrange=True
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(7)),
        ticktext=[
            "Mon", "Tue", "Wed", "Thu",
            "Fri", "Sat", "Sun"
        ],
        range=[6.5, -0.5],
        showgrid=False,
        showline=False,
        zeroline=False,
        ticks="",
        fixedrange=True
    )

    # Highlight 6 February 2023 using an amber border.
    feb6 = date(2023, 2, 6)

    if (
        year == 2023
        and visible_start <= feb6 <= visible_end
    ):

        x = (feb6 - first_monday).days // 7
        y = feb6.weekday()

        fig.add_shape(
            type="rect",
            x0=x - 0.5,
            x1=x + 0.5,
            y0=y - 0.5,
            y1=y + 0.5,
            line=dict(
                color="#D97706",
                width=2.5
            ),
            fillcolor="rgba(0,0,0,0)",
            layer="above"
        )

    fig.update_layout(
        height=270,
        margin=dict(
            l=36,
            r=25,
            t=54,
            b=22
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            color="#334155"
        ),
        showlegend=False,
        hovermode="closest"
    )

    return fig
