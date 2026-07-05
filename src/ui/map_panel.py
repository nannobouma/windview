from __future__ import annotations

import html

import folium
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - depends on local Qt installation
    QWebEngineView = None

from models.metadata import Metadata
from models.turbine import Turbine
from services.geo import analyze_turbines


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
        self.show_data(None, [])

    def show_metadata(self, metadata: Metadata | None) -> None:
        self.show_data(metadata, [])

    def show_data(self, metadata: Metadata | None, turbines: list[Turbine]) -> None:
        if metadata is None or not metadata.has_location:
            self._set_html(self._empty_map_html(turbines))
            return

        lat = float(metadata.latitude)
        lon = float(metadata.longitude)
        street_map = folium.Map(location=[lat, lon], zoom_start=16, control_scale=True)
        folium.Marker(
            [lat, lon],
            tooltip="Street View locatie",
            popup=self._streetview_popup_text(metadata),
            icon=folium.Icon(color="blue", icon="camera"),
        ).add_to(street_map)
        folium.Circle([lat, lon], radius=800, color="#2b7cff", fill=False, weight=2).add_to(street_map)
        folium.Circle([lat, lon], radius=1500, color="#f08a24", fill=False, weight=2).add_to(street_map)
        folium.Circle([lat, lon], radius=2700, color="#d94b4b", fill=False, weight=2).add_to(street_map)

        for analysis in analyze_turbines(metadata, turbines):
            turbine = analysis.turbine
            color = "green" if analysis.in_fov else "red"
            folium.Marker(
                [turbine.latitude, turbine.longitude],
                tooltip=turbine.name,
                popup=self._turbine_popup_text(analysis),
                icon=folium.Icon(color=color, icon="flash"),
            ).add_to(street_map)
            folium.PolyLine(
                [[lat, lon], [turbine.latitude, turbine.longitude]],
                color=color,
                weight=2,
                opacity=0.75,
            ).add_to(street_map)

        self._set_html(street_map.get_root().render())

    def _set_html(self, content: str) -> None:
        if QWebEngineView is None:
            self._view.setText("Kaart niet beschikbaar in deze PySide6-installatie.")
        else:
            self._view.setHtml(content)

    def _streetview_popup_text(self, metadata: Metadata) -> str:
        parts = [
            f"Lat: {metadata.latitude}",
            f"Lon: {metadata.longitude}",
            f"Heading: {metadata.heading}",
            f"Pitch: {metadata.pitch}",
            f"FOV: {metadata.fov}",
            f"Pano: {html.escape(str(metadata.pano_id))}",
        ]
        return "<br>".join(parts)

    def _turbine_popup_text(self, analysis) -> str:
        turbine = analysis.turbine
        relative = "onbekend" if analysis.relative_heading_deg is None else f"{analysis.relative_heading_deg:+.1f} deg"
        in_fov = "onbekend" if analysis.in_fov is None else ("ja" if analysis.in_fov else "nee")
        parts = [
            html.escape(turbine.name),
            f"Afstand: {analysis.distance_m:,.0f} m",
            f"Richting: {analysis.bearing_deg:.1f} deg",
            f"Relatieve hoek: {relative}",
            f"In beeld: {in_fov}",
        ]
        return "<br>".join(parts)

    def _empty_map_html(self, turbines: list[Turbine]) -> str:
        street_map = folium.Map(location=[52.1, 5.1], zoom_start=7, control_scale=True)
        for turbine in turbines:
            folium.Marker(
                [turbine.latitude, turbine.longitude],
                tooltip=turbine.name,
                popup=html.escape(turbine.name),
                icon=folium.Icon(color="red", icon="flash"),
            ).add_to(street_map)
        return street_map.get_root().render()
