from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy


class PhotoPanel(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(640, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText("Geen foto geladen")
        self.setStyleSheet("background: #20242a; color: #d9dee7; border: 1px solid #3a404a;")

    def set_photo(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self._render_scaled_photo()

    def clear_photo(self) -> None:
        self._pixmap = None
        self.clear()
        self.setText("Geen foto geladen")

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override name
        super().resizeEvent(event)
        self._render_scaled_photo()

    def _render_scaled_photo(self) -> None:
        if self._pixmap is None:
            return

        self.setPixmap(
            self._pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
