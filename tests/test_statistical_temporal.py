"""Automated checks for SEISMOSCOPE Member 3 visualizations."""

import unittest
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from charts.statistical.statistical_temporal import (
    create_density_contour_smoothed,
    create_density_contour_binned,
    create_violin_plot,
    create_calendar_heatmap,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "earthquakes_dashboard_ready.csv"


class TestStatisticalTemporal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA_PATH)

    def test_dataset_basics(self):
        self.assertEqual(len(self.df), 9889)
        required = {"id", "mag", "depth", "magType", "magError", "event_date_utc"}
        self.assertTrue(required.issubset(self.df.columns))

    def test_february_6_mainshocks_are_present(self):
        events = self.df.set_index("id")
        self.assertEqual(events.loc["us6000jllz", "event_date_utc"], "2023-02-06")
        self.assertEqual(events.loc["us6000jlqa", "event_date_utc"], "2023-02-06")
        self.assertAlmostEqual(events.loc["us6000jllz", "mag"], 7.8)
        self.assertAlmostEqual(events.loc["us6000jlqa", "mag"], 7.5)

    def test_density_contour_two_versions(self):
        overview = create_density_contour_smoothed(self.df, "Focused View")
        detailed = create_density_contour_binned(self.df, "Full Range")
        self.assertIsInstance(overview, go.Figure)
        self.assertIsInstance(detailed, go.Figure)
        self.assertEqual(overview.data[0].type, "histogram2dcontour")
        self.assertEqual(detailed.data[0].type, "histogram2dcontour")
        self.assertEqual(detailed.data[0].xbins.size, 0.05)
        self.assertEqual(list(detailed.layout.yaxis.range), [-10, 750])

    def test_density_contour_empty_data(self):
        empty = self.df.iloc[0:0]
        fig = create_density_contour_smoothed(empty)
        self.assertEqual(len(fig.data), 0)
        self.assertIn("No records", fig.layout.annotations[0].text)

    def test_violin_plot_and_empty_selection(self):
        fig = create_violin_plot(self.df, ["mb", "mww", "mwr"])
        self.assertEqual(len(fig.data), 3)
        self.assertTrue(all(trace.type == "violin" for trace in fig.data))
        self.assertEqual(sum(len(trace.y) for trace in fig.data), 9772)

        empty_fig = create_violin_plot(self.df, [])
        self.assertEqual(len(empty_fig.data), 0)
        self.assertIn("No valid measurements", empty_fig.layout.annotations[0].text)

    def test_calendar_heatmap_february_6(self):
        fig = create_calendar_heatmap(
            self.df, 2023, date(2023, 2, 1), date(2023, 12, 31)
        )
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(fig.data[1].type, "heatmap")
        self.assertEqual(len(fig.layout.shapes), 1)  # 6 February outline

        daily_counts = {
            entry[0]: entry[1]
            for row in fig.data[1].customdata
            for entry in row
            if entry[0]
        }
        self.assertEqual(daily_counts["06 Feb 2023"], 127)

    def test_calendar_heatmap_excluded_date(self):
        fig = create_calendar_heatmap(
            self.df, 2023, date(2023, 2, 1), date(2023, 2, 5)
        )
        self.assertEqual(len(fig.layout.shapes), 0)
        fig_2024 = create_calendar_heatmap(
            self.df, 2024, date(2024, 1, 1), date(2024, 5, 31)
        )
        self.assertEqual(len(fig_2024.layout.shapes), 0)


if __name__ == "__main__":
    unittest.main()
