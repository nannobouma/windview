from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from models.metadata import Metadata
from models.turbine import Turbine
from services.analysis_exporter import export_analysis_csv, export_analysis_geojson


class AnalysisExporterTest(unittest.TestCase):
    def test_exports_turbine_analysis_to_csv_and_geojson(self) -> None:
        metadata = Metadata(latitude=52.1, longitude=5.1, heading=90, fov=90)
        turbines = [
            Turbine("WTG-01", 52.1, 5.11),
            Turbine("WTG-02", 52.2, 5.2),
        ]

        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "analysis.csv"
            geojson_path = Path(directory) / "analysis.geojson"

            csv_count = export_analysis_csv(str(csv_path), metadata, turbines)
            geojson_count = export_analysis_geojson(str(geojson_path), metadata, turbines)

            self.assertEqual(csv_count, 2)
            self.assertEqual(geojson_count, 2)

            with csv_path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["name"], "WTG-01")
            self.assertEqual(rows[0]["in_fov"], "True")
            self.assertEqual(round(float(rows[0]["distance_m"])), 683)
            self.assertIn("bearing_deg", rows[0])
            self.assertIn("relative_heading_deg", rows[0])

            with geojson_path.open(encoding="utf-8") as handle:
                geojson = json.load(handle)
            self.assertEqual(geojson["type"], "FeatureCollection")
            self.assertEqual(len(geojson["features"]), 2)
            self.assertEqual(geojson["features"][0]["geometry"]["coordinates"], [5.11, 52.1])
            self.assertEqual(geojson["features"][0]["properties"]["name"], "WTG-01")


if __name__ == "__main__":
    unittest.main()
