from __future__ import annotations

import json
from pathlib import Path

from models.location import StreetViewLocation
from models.metadata import Metadata
from models.turbine import Turbine


PROJECT_VERSION = 3


def save_project(
    filename: str,
    image_path: str | None = None,
    metadata: Metadata | None = None,
    turbines: list[Turbine] | None = None,
    locations: list[StreetViewLocation] | None = None,
    selected_location_index: int | None = None,
) -> None:
    project_locations = locations
    if project_locations is None:
        project_locations = _legacy_location(image_path, metadata)

    payload = {
        "version": PROJECT_VERSION,
        "selected_location_index": selected_location_index,
        "locations": [location.to_dict() for location in project_locations],
        "turbines": [turbine.to_dict() for turbine in turbines or []],
    }

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_project(filename: str) -> tuple[list[StreetViewLocation], int | None, list[Turbine]]:
    path = Path(filename)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    locations = _load_locations(payload)
    selected_location_index = payload.get("selected_location_index")
    if not isinstance(selected_location_index, int) or not 0 <= selected_location_index < len(locations):
        selected_location_index = 0 if locations else None

    turbines_payload = payload.get("turbines")
    turbines = _load_turbines(turbines_payload)
    return locations, selected_location_index, turbines


def _legacy_location(image_path: str | None, metadata: Metadata | None) -> list[StreetViewLocation]:
    if image_path is None and metadata is None:
        return []
    name = Path(image_path).stem if image_path else "Street View locatie"
    return [StreetViewLocation(name=name, image_path=image_path, metadata=metadata)]


def _load_locations(payload: dict) -> list[StreetViewLocation]:
    locations_payload = payload.get("locations")
    if isinstance(locations_payload, list):
        return [StreetViewLocation.from_dict(item) for item in locations_payload if isinstance(item, dict)]

    metadata_payload = payload.get("metadata")
    metadata = Metadata.from_dict(metadata_payload) if isinstance(metadata_payload, dict) else None
    return _legacy_location(payload.get("image_path"), metadata)


def _load_turbines(payload) -> list[Turbine]:
    if not isinstance(payload, list):
        return []

    turbines = []
    for item in payload:
        if isinstance(item, dict):
            turbines.append(Turbine.from_dict(item))
    return turbines
