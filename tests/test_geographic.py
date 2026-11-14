"""Smoke tests for Member 1's chart functions. Run: python -m unittest discover -s tests -v"""
import unittest
from pathlib import Path
import pandas as pd
from charts.geographic.geographic_categorical import create_geographic_map, create_sankey_diagram, create_sunburst

DATA=Path(__file__).resolve().parents[1]/"data"/"earthquakes_dashboard_ready.csv"

class GeographicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=pd.read_csv(DATA)
    def test_map_2d_and_globe(self):
        subset=self.df.head(100)
        for mode in ["2D Map","Orthographic Globe","Monthly Animation"]:
            fig=create_geographic_map(subset, mode)
            self.assertGreater(len(fig.data),0)
    def test_sankey_counts(self):
        subset=self.df.head(100)
        fig=create_sankey_diagram(subset)
        self.assertEqual(sum(fig.data[0].link.value), 2*len(subset))
    def test_sunburst(self):
        self.assertGreater(len(create_sunburst(self.df.head(100)).data),0)
    def test_empty(self):
        for make in [create_geographic_map,create_sankey_diagram,create_sunburst]:
            self.assertIsNotNone(make(self.df.iloc[0:0]))

if __name__ == "__main__": unittest.main()
