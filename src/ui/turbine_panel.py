from __future__ import annotations

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from models.metadata import Metadata
from models.turbine import Turbine
from services.geo import TurbineAnalysis, analyze_turbines


class TurbinePanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Turbine", "Lat", "Lon", "Afstand", "Richting", "Rel. hoek", "In beeld"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)

    def show_turbines(self, metadata: Metadata | None, turbines: list[Turbine]) -> None:
        analyses = analyze_turbines(metadata, turbines)
        if analyses:
            self._show_analyses(analyses)
            return

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(turbines))
        for row, turbine in enumerate(turbines):
            self._set(row, 0, turbine.name)
            self._set(row, 1, f"{turbine.latitude:.6f}")
            self._set(row, 2, f"{turbine.longitude:.6f}")
            self._set(row, 3, "-")
            self._set(row, 4, "-")
            self._set(row, 5, "-")
            self._set(row, 6, "-")
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

    def _show_analyses(self, analyses: list[TurbineAnalysis]) -> None:
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(analyses))
        for row, analysis in enumerate(analyses):
            turbine = analysis.turbine
            self._set(row, 0, turbine.name)
            self._set(row, 1, f"{turbine.latitude:.6f}")
            self._set(row, 2, f"{turbine.longitude:.6f}")
            self._set(row, 3, f"{analysis.distance_m:,.0f} m")
            self._set(row, 4, f"{analysis.bearing_deg:.1f} deg")
            self._set(row, 5, _format_optional_angle(analysis.relative_heading_deg))
            self._set(row, 6, _format_optional_bool(analysis.in_fov))
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

    def _set(self, row: int, column: int, value: str) -> None:
        self.table.setItem(row, column, QTableWidgetItem(value))


def _format_optional_angle(value: float | None) -> str:
    return "-" if value is None else f"{value:+.1f} deg"


def _format_optional_bool(value: bool | None) -> str:
    if value is None:
        return "onbekend"
    return "ja" if value else "nee"
