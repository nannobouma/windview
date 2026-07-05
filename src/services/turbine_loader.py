from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from models.turbine import Turbine


NAME_KEYS = ("name", "naam", "id", "turbine", "turbine_id", "label")
LATITUDE_KEYS = ("latitude", "lat", "y")
LONGITUDE_KEYS = ("longitude", "lon", "lng", "x")
HUB_HEIGHT_KEYS = ("hub_height", "ashoogte", "as_hoogte", "height", "hoogte")
ROTOR_DIAMETER_KEYS = ("rotor_diameter", "rotordiameter", "diameter")


def load_turbines_csv(filename: str) -> list[Turbine]:
    path = Path(filename)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample.strip() else csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        if reader.fieldnames is None:
            raise ValueError("CSV must contain a header row.")

        turbines = []
        for index, row in enumerate(reader, start=1):
            normalized = _normalize_row(row)
            latitude = _number(_first(normalized, LATITUDE_KEYS))
            longitude = _number(_first(normalized, LONGITUDE_KEYS))
            if latitude is None or longitude is None:
                continue

            name = _first(normalized, NAME_KEYS) or f"Turbine {index}"
            turbines.append(
                Turbine(
                    name=str(name),
                    latitude=latitude,
                    longitude=longitude,
                    hub_height=_number(_first(normalized, HUB_HEIGHT_KEYS)),
                    rotor_diameter=_number(_first(normalized, ROTOR_DIAMETER_KEYS)),
                    source_file=str(path),
                )
            )

    if not turbines:
        raise ValueError("No turbines with latitude and longitude were found in the CSV.")

    return turbines


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip().lower(): value for key, value in row.items() if key is not None}


def _first(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = row.get(key)
        if value is not None and value != "":
            return value
    return None


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
