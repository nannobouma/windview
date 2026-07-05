from __future__ import annotations

from pathlib import Path

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
from PySide6.QtCore import Qt

from models.metadata import Metadata
from services.image_loader import load_image
from services.json_loader import load_json
from services.project_store import load_project, save_project
from ui.map_panel import MapPanel
from ui.metadata_panel import MetadataPanel
from ui.photo_panel import PhotoPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WindView")
        self.resize(1500, 900)

        self.current_image_path: str | None = None
        self.current_metadata: Metadata | None = None

        self.photo = PhotoPanel()
        self.metadata_panel = MetadataPanel()
        self.map_panel = MapPanel()

        self._build_toolbar()
        self._build_layout()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Bestand")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_photo = QPushButton("Open JPEG")
        open_json = QPushButton("Open JSON")
        open_project = QPushButton("Open project")
        save_project_button = QPushButton("Save project")

        open_photo.clicked.connect(self.open_photo)
        open_json.clicked.connect(self.open_json)
        open_project.clicked.connect(self.open_project)
        save_project_button.clicked.connect(self.save_project)

        toolbar.addWidget(open_photo)
        toolbar.addWidget(open_json)
        toolbar.addSeparator()
        toolbar.addWidget(open_project)
        toolbar.addWidget(save_project_button)

    def _build_layout(self) -> None:
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.addWidget(self.metadata_panel, 2)
        right_layout.addWidget(self.map_panel, 3)

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
            image_path, metadata = load_project(filename)
            if image_path:
                self._load_photo(image_path)
            self._set_metadata(metadata)
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
            save_project(filename, self.current_image_path, self.current_metadata)
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
        self.map_panel.show_metadata(metadata)

    def _show_error(self, title: str, exc: Exception) -> None:
        QMessageBox.critical(self, title, str(exc))
