from __future__ import annotations

from PySide6.QtWidgets import QListWidget

from models.location import StreetViewLocation


class LocationPanel(QListWidget):
    def show_locations(self, locations: list[StreetViewLocation], selected_index: int | None) -> None:
        self.blockSignals(True)
        self.clear()
        for location in locations:
            self.addItem(location.name)
        if selected_index is not None and 0 <= selected_index < len(locations):
            self.setCurrentRow(selected_index)
        self.blockSignals(False)
