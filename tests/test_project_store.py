from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from models.location import StreetViewLocation
from models.metadata import Metadata
from models.turbine import Turbine
from services.project_store import load_project, save_project


class ProjectStoreTest(unittest.TestCase):
    def test_saves_and_loads_multiple_locations(self) -> None:
        locations = [
            StreetViewLocation("Locatie 1", "one.jpg", Metadata(latitude=52.1, longitude=5.1)),
            StreetViewLocation("Locatie 2", "two.jpg", Metadata(latitude=52.2, longitude=5.2)),
        ]
        turbines = [Turbine("WTG-01", 52.15, 5.15)]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "project.windview"
            save_project(
                str(path),
                turbines=turbines,
                locations=locations,
                selected_location_index=1,
            )

            loaded_locations, selected_index, loaded_turbines = load_project(str(path))

        self.assertEqual(selected_index, 1)
        self.assertEqual(len(loaded_locations), 2)
        self.assertEqual(loaded_locations[1].name, "Locatie 2")
        self.assertEqual(loaded_locations[1].metadata.latitude, 52.2)
        self.assertEqual(len(loaded_turbines), 1)
        self.assertEqual(loaded_turbines[0].name, "WTG-01")

    def test_loads_legacy_single_location_project(self) -> None:
        payload = {
            "version": 2,
            "image_path": "legacy.jpg",
            "metadata": {"latitude": 52.1, "longitude": 5.1},
            "turbines": [{"name": "WTG-01", "latitude": 52.2, "longitude": 5.2}],
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.windview"
            with path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            locations, selected_index, turbines = load_project(str(path))

        self.assertEqual(selected_index, 0)
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0].name, "legacy")
        self.assertEqual(locations[0].image_path, "legacy.jpg")
        self.assertEqual(locations[0].metadata.longitude, 5.1)
        self.assertEqual(turbines[0].name, "WTG-01")


if __name__ == "__main__":
    unittest.main()
