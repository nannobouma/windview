from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from models.metadata import Metadata


@dataclass
class StreetViewLocation:
    name: str
    image_path: str | None = None
    metadata: Metadata | None = None

    @classmethod
    def from_image(cls, image_path: str, metadata: Metadata | None = None) -> "StreetViewLocation":
        return cls(name=Path(image_path).stem, image_path=image_path, metadata=metadata)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["metadata"] = self.metadata.to_dict() if self.metadata else None
        return payload

    @classmethod
    def from_dict(cls, data: dict) -> "StreetViewLocation":
        metadata_payload = data.get("metadata")
        metadata = Metadata.from_dict(metadata_payload) if isinstance(metadata_payload, dict) else None
        image_path = data.get("image_path")
        return cls(
            name=str(data.get("name") or _fallback_name(image_path)),
            image_path=image_path,
            metadata=metadata,
        )


def _fallback_name(image_path: str | None) -> str:
    if image_path:
        return Path(image_path).stem
    return "Street View locatie"
