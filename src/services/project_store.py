from __future__ import annotations

import json
from pathlib import Path

from models.metadata import Metadata


PROJECT_VERSION = 1


def save_project(filename: str, image_path: str | None, metadata: Metadata | None) -> None:
    payload = {
        "version": PROJECT_VERSION,
        "image_path": image_path,
        "metadata": metadata.to_dict() if metadata else None,
    }

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_project(filename: str) -> tuple[str | None, Metadata | None]:
    path = Path(filename)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    metadata_payload = payload.get("metadata")
    metadata = Metadata.from_dict(metadata_payload) if isinstance(metadata_payload, dict) else None
    return payload.get("image_path"), metadata
