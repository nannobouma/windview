# WindView

WindView is a PySide6 desktop application for inspecting Street View imagery and metadata for wind park visual impact research.

## Current version

This first working version provides:

- JPEG import
- JSON metadata import
- automatic JSON pairing when a JPEG has a matching file name
- photo preview
- metadata side panel
- OpenStreetMap location view based on latitude and longitude
- project save and open as `.windview` JSON files

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python src/main.py
```

## Expected JSON fields

WindView accepts common Street View metadata keys such as:

```json
{
  "latitude": 52.123,
  "longitude": 5.123,
  "heading": 180,
  "pitch": 0,
  "fov": 90,
  "panoid": "example",
  "resolution": {
    "width": 13312,
    "height": 6656
  }
}
```

Alternative keys such as `lat`, `lng`, `lon`, `pano_id`, `panoId`, `width`, and `height` are also handled.
