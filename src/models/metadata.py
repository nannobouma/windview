from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Metadata:
    latitude: float | None = None
    longitude: float | None = None
    heading: float | None = None
    pitch: float | None = None
    fov: float | None = None
    pano_id: str | None = None
    width: int | None = None
    height: int | None = None
    source_file: str | None = None

    @property
    def has_location(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Metadata":
        return cls(**{key: data.get(key) for key in cls.__dataclass_fields__})
