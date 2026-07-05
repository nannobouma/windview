from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from models.metadata import Metadata
from models.turbine import Turbine
from services.analysis_exporter import export_analysis_csv, export_analysis_geojson
from services.image_loader import load_image
from services.json_loader import load_json
from services.project_store import load_project, save_project
from services.turbine_loader import load_turbines_csv
from ui.map_panel import MapPanel
from ui.metadata_panel import MetadataPanel
from ui.photo_panel import PhotoPanel
from ui.turbine_panel import TurbinePanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WindView")
        self.resize(1500, 900)

        self.current_image_path: str | None = None
        self.current_metadata: Metadata | None = None
        self.current_turbines: list[Turbine] = []

        self.photo = PhotoPanel()
        self.metadata_panel = MetadataPanel()
        self.turbine_panel = TurbinePanel()
        self.map_panel = MapPanel()

        self._build_toolbar()
        self._build_layout()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Bestand")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_photo = QPushButton("Open JPEG")
        open_json = QPushButton("Open JSON")
        open_turbines = QPushButton("Open turbines CSV")
        export_csv = QPushButton("Export CSV")
        export_geojson = QPushButton("Export GeoJSON")
        open_project = QPushButton("Open project")
        save_project_button = QPushButton("Save project")

        open_photo.clicked.connect(self.open_photo)
        open_json.clicked.connect(self.open_json)
        open_turbines.clicked.connect(self.open_turbines)
        export_csv.clicked.connect(self.export_csv)
        export_geojson.clicked.connect(self.export_geojson)
        open_project.clicked.connect(self.open_project)
        save_project_button.clicked.connect(self.save_project)

        toolbar.addWidget(open_photo)
        toolbar.addWidget(open_json)
        toolbar.addWidget(open_turbines)
        toolbar.addSeparator()
        toolbar.addWidget(export_csv)
        toolbar.addWidget(export_geojson)
        toolbar.addSeparator()
        toolbar.addWidget(open_project)
        toolbar.addWidget(save_project_button)

    def _build_layout(self) -> None:
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.addWidget(self.metadata_panel, 2)
        right_layout.addWidget(self.turbine_panel, 2)
        right_layout.addWidget(self.map_panel, 4)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.photo)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

    def open_photo(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open JPEG",
            "",
            "JPEG (*.jpg *.jpeg)",
        )
        if not filename:
            return

        self._load_photo(filename)
        matching_json = Path(filename).with_suffix(".json")
        if matching_json.exists():
            self._load_metadata(str(matching_json))

    def open_json(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open JSON",
            "",
            "JSON (*.json)",
        )
        if filename:
            self._load_metadata(filename)

    def open_turbines(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open turbine CSV",
            "",
            "CSV (*.csv);;Text (*.txt);;All files (*.*)",
        )
        if not filename:
            return

        try:
            self.current_turbines = load_turbines_csv(filename)
            self._refresh_turbine_views()
            self.statusBar().showMessage(f"{len(self.current_turbines)} turbines geladen: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("Turbines laden mislukt", exc)

    def export_csv(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export turbine analysis CSV",
            "",
            "CSV (*.csv)",
        )
        if not filename:
            return

        if not filename.lower().endswith(".csv"):
            filename = f"{filename}.csv"

        try:
            count = export_analysis_csv(filename, self.current_metadata, self.current_turbines)
            self.statusBar().showMessage(f"{count} turbine-analyses geexporteerd: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("CSV export mislukt", exc)

    def export_geojson(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export turbine analysis GeoJSON",
            "",
            "GeoJSON (*.geojson);;JSON (*.json)",
        )
        if not filename:
            return

        if not filename.lower().endswith((".geojson", ".json")):
            filename = f"{filename}.geojson"

        try:
            count = export_analysis_geojson(filename, self.current_metadata, self.current_turbines)
            self.statusBar().showMessage(f"{count} turbine-analyses geexporteerd: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("GeoJSON export mislukt", exc)

    def open_project(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open WindView project",
            "",
            "WindView project (*.windview);;JSON (*.json)",
        )
        if not filename:
            return

        try:
            image_path, metadata, turbines = load_project(filename)
            self.current_turbines = turbines
            if image_path:
                self._load_photo(image_path)
            self._set_metadata(metadata)
            self._refresh_turbine_views()
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("Project openen mislukt", exc)

    def save_project(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save WindView project",
            "",
            "WindView project (*.windview)",
        )
        if not filename:
            return

        if not filename.lower().endswith(".windview"):
            filename = f"{filename}.windview"

        try:
            save_project(filename, self.current_image_path, self.current_metadata, self.current_turbines)
            self.statusBar().showMessage(f"Project opgeslagen: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("Project opslaan mislukt", exc)

    def _load_photo(self, filename: str) -> None:
        try:
            self.photo.set_photo(load_image(filename))
            self.current_image_path = filename
            self.statusBar().showMessage(f"Foto geladen: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("Foto laden mislukt", exc)

    def _load_metadata(self, filename: str) -> None:
        try:
            self._set_metadata(load_json(filename))
            self.statusBar().showMessage(f"Metadata geladen: {filename}")
        except Exception as exc:  # noqa: BLE001 - UI boundary shows the error
            self._show_error("JSON laden mislukt", exc)

    def _set_metadata(self, metadata: Metadata | None) -> None:
        self.current_metadata = metadata
        self.metadata_panel.show_metadata(metadata)
        self._refresh_turbine_views()

    def _refresh_turbine_views(self) -> None:
        self.turbine_panel.show_turbines(self.current_metadata, self.current_turbines)
        self.map_panel.show_data(self.current_metadata, self.current_turbines)

    def _show_error(self, title: str, exc: Exception) -> None:
        QMessageBox.critical(self, title, str(exc))
