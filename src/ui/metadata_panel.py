from PySide6.QtWidgets import QTextEdit

from models.metadata import Metadata


class MetadataPanel(QTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumWidth(320)
        self.setPlaceholderText("Geen metadata geladen")

    def show_metadata(self, metadata: Metadata | None) -> None:
        if metadata is None:
            self.clear()
            return

        self.setPlainText(
            "\n".join(
                [
                    f"Latitude : {metadata.latitude}",
                    f"Longitude: {metadata.longitude}",
                    "",
                    f"Heading  : {metadata.heading}",
                    f"Pitch    : {metadata.pitch}",
                    f"FOV      : {metadata.fov}",
                    "",
                    f"Panorama : {metadata.pano_id}",
                    "",
                    f"Breedte  : {metadata.width}",
                    f"Hoogte   : {metadata.height}",
                    "",
                    f"Bron     : {metadata.source_file}",
                ]
            )
        )
