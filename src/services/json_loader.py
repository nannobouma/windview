from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.metadata import Metadata


def _first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def _first_from_sources(keys: tuple[str, ...], *sources: dict[str, Any]) -> Any:
    for source in sources:
        value = _first(source, *keys)
        if value is not None:
            return value
    return None


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _integer(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


def load_json(filename: str) -> Metadata:
    path = Path(filename)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("Metadata JSON must contain an object at the top level.")

    location = data.get("location") if isinstance(data.get("location"), dict) else {}
    resolution = data.get("resolution") if isinstance(data.get("resolution"), dict) else {}
    camera = data.get("camera") if isinstance(data.get("camera"), dict) else {}

    return Metadata(
        latitude=_number(_first_from_sources(("latitude", "lat"), data, location)),
        longitude=_number(_first_from_sources(("longitude", "lng", "lon"), data, location)),
        heading=_number(_first_from_sources(("heading",), data, camera)),
        pitch=_number(_first_from_sources(("pitch",), data, camera)),
        fov=_number(_first_from_sources(("fov",), data, camera)),
        pano_id=_first(data, "panoid", "pano_id", "panoId", "panorama_id"),
        width=_integer(_first_from_sources(("width",), data, resolution)),
        height=_integer(_first_from_sources(("height",), data, resolution)),
        source_file=str(path),
    )
