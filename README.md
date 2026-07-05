# WindView

WindView is a PySide6 desktop application for inspecting Street View imagery and metadata for wind park visual impact research.

## Current version

This working version provides:

- JPEG import
- JSON metadata import
- automatic JSON pairing when a JPEG has a matching file name
- multiple Street View locations in one project
- location list with selectable photo/metadata analysis
- photo preview
- metadata side panel
- OpenStreetMap location view based on latitude and longitude
- turbine CSV import
- turbine markers and sight lines on the map
- distance, bearing, relative viewing angle, and in-FOV checks
- turbine analysis export to CSV and GeoJSON
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

## Test

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Expected Street View JSON fields

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

## Expected turbine CSV fields

WindView accepts comma, semicolon, or tab separated CSV files with a header row.

Minimal example:

```csv
name,latitude,longitude
WTG-01,52.1234,5.1234
WTG-02,52.1301,5.1402
```

Supported column names:

- turbine name: `name`, `naam`, `id`, `turbine`, `turbine_id`, `label`
- latitude: `latitude`, `lat`, `y`
- longitude: `longitude`, `lon`, `lng`, `x`
- hub height: `hub_height`, `ashoogte`, `as_hoogte`, `height`, `hoogte`
- rotor diameter: `rotor_diameter`, `rotordiameter`, `diameter`

After loading Street View metadata and turbines, WindView calculates:

- distance from camera to turbine
- compass bearing to the turbine
- relative angle compared with the camera heading
- whether the turbine lies inside the Street View field of view when heading and FOV are known

## Export

Use `Export CSV` or `Export GeoJSON` after selecting a Street View location and loading a turbine CSV.

Each exported turbine analysis contains:

- `name`
- `latitude`
- `longitude`
- `distance_m`
- `bearing_deg`
- `relative_heading_deg`
- `in_fov`

The GeoJSON export writes one point feature per turbine. Coordinates use standard GeoJSON order: `[longitude, latitude]`.

## Multi-location projects

Use `Add JPEG` to add a Street View image as a new location. If a JSON file with the same base name exists next to the JPEG, WindView links it automatically.

Use `Attach JSON` to attach or replace metadata for the selected location.

The `.windview` project file stores:

- all Street View locations
- each location's image path and metadata
- the selected location
- loaded turbines

The map, metadata panel, turbine table, and export buttons always use the selected location.
