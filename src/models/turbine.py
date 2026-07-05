from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Turbine:
    name: str
    latitude: float
    longitude: float
    hub_height: float | None = None
    rotor_diameter: float | None = None
    source_file: str | None = None

    @property
    def has_location(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Turbine":
        return cls(
            name=str(data.get("name") or "Turbine"),
            latitude=float(data.get("latitude")),
            longitude=float(data.get("longitude")),
            hub_height=_optional_float(data.get("hub_height")),
            rotor_diameter=_optional_float(data.get("rotor_diameter")),
            source_file=data.get("source_file"),
        )


def _optional_float(value) -> float | None:
    if value is None or value == "":
        return None
    return float(value)
