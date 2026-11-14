"""Smoke tests for Member 2's chart functions. Run: python -m unittest discover -s tests -v"""
import unittest
from pathlib import Path
import pandas as pd
from charts.multidimensional.multidimensional import (create_treemap, summarize_locations,
    create_parallel_coordinates, complete_measurements, create_scatter_3d, prepare_3d_data)

DATA=Path(__file__).resolve().parents[1]/"data"/"earthquakes_dashboard_ready.csv"

class MultidimensionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=pd.read_csv(DATA)
    def test_treemap_top_15(self):
        self.assertLessEqual(len(summarize_locations(self.df,15)),15)
        self.assertGreater(len(create_treemap(self.df).data),0)
    def test_parallel_complete_records(self):
        self.assertLessEqual(len(complete_measurements(self.df)),len(self.df))
        self.assertGreater(len(create_parallel_coordinates(self.df).data),0)
    def test_3d_exact_10km_filter(self):
        all_rows=prepare_3d_data(self.df,True)
        limited=prepare_3d_data(self.df,False)
        self.assertGreater(len(all_rows),len(limited))
        self.assertGreater(len(create_scatter_3d(self.df.head(100)).data),0)
    def test_empty(self):
        subset=self.df.iloc[0:0]
        for make in [create_treemap,create_parallel_coordinates,create_scatter_3d]:
            self.assertIsNotNone(make(subset))

if __name__ == "__main__": unittest.main()
