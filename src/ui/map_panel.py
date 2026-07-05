from __future__ import annotations

import html

import folium
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - depends on local Qt installation
    QWebEngineView = None

from models.metadata import Metadata


class MapPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(320)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if QWebEngineView is None:
            self._view = QLabel("Kaartweergave vereist QtWebEngine. Installeer PySide6 met WebEngine ondersteuning.")
            self._view.setWordWrap(True)
        else:
            self._view = QWebEngineView()

        self._layout.addWidget(self._view)
        self.show_metadata(None)

    def show_metadata(self, metadata: Metadata | None) -> None:
        if metadata is None or not metadata.has_location:
            self._set_html(self._empty_map_html())
            return

        lat = float(metadata.latitude)
        lon = float(metadata.longitude)
        street_map = folium.Map(location=[lat, lon], zoom_start=16, control_scale=True)
        folium.Marker(
            [lat, lon],
            tooltip="Street View locatie",
            popup=self._popup_text(metadata),
            icon=folium.Icon(color="blue", icon="camera"),
        ).add_to(street_map)
        folium.Circle([lat, lon], radius=800, color="#2b7cff", fill=False, weight=2).add_to(street_map)
        folium.Circle([lat, lon], radius=1500, color="#f08a24", fill=False, weight=2).add_to(street_map)
        folium.Circle([lat, lon], radius=2700, color="#d94b4b", fill=False, weight=2).add_to(street_map)
        self._set_html(street_map.get_root().render())

    def _set_html(self, content: str) -> None:
        if QWebEngineView is None:
            self._view.setText("Kaart niet beschikbaar in deze PySide6-installatie.")
        else:
            self._view.setHtml(content)

    def _popup_text(self, metadata: Metadata) -> str:
        parts = [
            f"Lat: {metadata.latitude}",
            f"Lon: {metadata.longitude}",
            f"Heading: {metadata.heading}",
            f"Pitch: {metadata.pitch}",
            f"FOV: {metadata.fov}",
            f"Pano: {html.escape(str(metadata.pano_id))}",
        ]
        return "<br>".join(parts)

    def _empty_map_html(self) -> str:
        street_map = folium.Map(location=[52.1, 5.1], zoom_start=7, control_scale=True)
        return street_map.get_root().render()
