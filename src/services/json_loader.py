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
        latitude=_number(_first(data, "latitude", "lat") or _first(location, "latitude", "lat")),
        longitude=_number(_first(data, "longitude", "lng", "lon") or _first(location, "longitude", "lng", "lon")),
        heading=_number(_first(data, "heading") or _first(camera, "heading")),
        pitch=_number(_first(data, "pitch") or _first(camera, "pitch")),
        fov=_number(_first(data, "fov") or _first(camera, "fov")),
        pano_id=_first(data, "panoid", "pano_id", "panoId", "panorama_id"),
        width=_integer(_first(data, "width") or _first(resolution, "width")),
        height=_integer(_first(data, "height") or _first(resolution, "height")),
        source_file=str(path),
    )
