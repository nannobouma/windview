from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from models.metadata import Metadata
from models.turbine import Turbine
from services.geo import TurbineAnalysis, analyze_turbines


def export_analysis_csv(filename: str, metadata: Metadata | None, turbines: list[Turbine]) -> int:
    analyses = _require_analysis(metadata, turbines)
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(_analysis_row(analyses[0]).keys()))
        writer.writeheader()
        for analysis in analyses:
            writer.writerow(_analysis_row(analysis))

    return len(analyses)


def export_analysis_geojson(filename: str, metadata: Metadata | None, turbines: list[Turbine]) -> int:
    analyses = _require_analysis(metadata, turbines)
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    feature_collection = {
        "type": "FeatureCollection",
        "features": [_analysis_feature(analysis) for analysis in analyses],
    }

    with path.open("w", encoding="utf-8") as handle:
        json.dump(feature_collection, handle, indent=2)

    return len(analyses)


def _require_analysis(metadata: Metadata | None, turbines: list[Turbine]) -> list[TurbineAnalysis]:
    analyses = analyze_turbines(metadata, turbines)
    if not analyses:
        raise ValueError("Load Street View metadata with latitude/longitude and at least one turbine first.")
    return analyses


def _analysis_row(analysis: TurbineAnalysis) -> dict[str, Any]:
    turbine = analysis.turbine
    return {
        "name": turbine.name,
        "latitude": turbine.latitude,
        "longitude": turbine.longitude,
        "distance_m": round(analysis.distance_m, 3),
        "bearing_deg": round(analysis.bearing_deg, 6),
        "relative_heading_deg": _round_optional(analysis.relative_heading_deg),
        "in_fov": analysis.in_fov,
    }


def _analysis_feature(analysis: TurbineAnalysis) -> dict[str, Any]:
    turbine = analysis.turbine
    properties = _analysis_row(analysis)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [turbine.longitude, turbine.latitude],
        },
        "properties": properties,
    }


def _round_optional(value: float | None) -> float | None:
    return None if value is None else round(value, 6)
