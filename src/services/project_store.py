from __future__ import annotations

import json
from pathlib import Path

from models.metadata import Metadata
from models.turbine import Turbine


PROJECT_VERSION = 2


def save_project(
    filename: str,
    image_path: str | None,
    metadata: Metadata | None,
    turbines: list[Turbine] | None = None,
) -> None:
    payload = {
        "version": PROJECT_VERSION,
        "image_path": image_path,
        "metadata": metadata.to_dict() if metadata else None,
        "turbines": [turbine.to_dict() for turbine in turbines or []],
    }

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_project(filename: str) -> tuple[str | None, Metadata | None, list[Turbine]]:
    path = Path(filename)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    metadata_payload = payload.get("metadata")
    metadata = Metadata.from_dict(metadata_payload) if isinstance(metadata_payload, dict) else None
    turbines_payload = payload.get("turbines")
    turbines = _load_turbines(turbines_payload)
    return payload.get("image_path"), metadata, turbines


def _load_turbines(payload) -> list[Turbine]:
    if not isinstance(payload, list):
        return []

    turbines = []
    for item in payload:
        if isinstance(item, dict):
            turbines.append(Turbine.from_dict(item))
    return turbines
