from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt, degrees

from models.metadata import Metadata
from models.turbine import Turbine

EARTH_RADIUS_M = 6_371_000


@dataclass
class TurbineAnalysis:
    turbine: Turbine
    distance_m: float
    bearing_deg: float
    relative_heading_deg: float | None
    in_fov: bool | None


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_M * c


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_lambda = radians(lon2 - lon1)

    y = sin(delta_lambda) * cos(phi2)
    x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(delta_lambda)
    return (degrees(atan2(y, x)) + 360) % 360


def relative_angle_deg(target_bearing: float, camera_heading: float | None) -> float | None:
    if camera_heading is None:
        return None
    return ((target_bearing - camera_heading + 540) % 360) - 180


def analyze_turbines(metadata: Metadata | None, turbines: list[Turbine]) -> list[TurbineAnalysis]:
    if metadata is None or not metadata.has_location:
        return []

    results = []
    for turbine in turbines:
        bearing = bearing_deg(metadata.latitude, metadata.longitude, turbine.latitude, turbine.longitude)
        relative = relative_angle_deg(bearing, metadata.heading)
        in_fov = _is_in_fov(relative, metadata.fov)
        results.append(
            TurbineAnalysis(
                turbine=turbine,
                distance_m=distance_m(metadata.latitude, metadata.longitude, turbine.latitude, turbine.longitude),
                bearing_deg=bearing,
                relative_heading_deg=relative,
                in_fov=in_fov,
            )
        )

    return sorted(results, key=lambda item: item.distance_m)


def _is_in_fov(relative: float | None, fov: float | None) -> bool | None:
    if relative is None or fov is None:
        return None
    return abs(relative) <= fov / 2
