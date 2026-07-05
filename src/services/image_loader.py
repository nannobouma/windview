from pathlib import Path

from PySide6.QtGui import QPixmap


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg"}


def load_image(filename: str) -> QPixmap:
    path = Path(filename)
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError("Only JPEG images are supported in this version.")

    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        raise ValueError(f"Could not load image: {path}")

    return pixmap
