"""Generate `app/assets/icon.ico` from the same R-on-purple design used
for the tray icon.

Uses only PyQt6 (already a Recall dependency) and the standard `struct`
module to write the ICO file format directly — no Pillow required.

Run once before `pyinstaller recall.spec`:

    python scripts/build_icon.py

Output: app/assets/icon.ico  (multi-resolution: 16, 32, 48, 64, 128, 256)
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from PyQt6.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "app" / "assets" / "icon.ico"
SIZES = (16, 32, 48, 64, 128, 256)


def render_png(size: int) -> bytes:
    """Render the icon at `size`×`size` and return its PNG bytes."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded square background in the brand accent.
    p.setBrush(QColor("#7c8cff"))
    p.setPen(Qt.PenStyle.NoPen)
    pad = max(1, size // 16)
    radius = max(2, size // 4)
    p.drawRoundedRect(pad, pad, size - 2 * pad, size - 2 * pad, radius, radius)

    # White "R".
    p.setPen(QColor("#ffffff"))
    font_size = max(7, int(size * 0.46))
    p.setFont(QFont("Segoe UI", font_size, QFont.Weight.Bold))
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "R")
    p.end()

    image = pix.toImage()
    buf = QByteArray()
    qbuf = QBuffer(buf)
    qbuf.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(qbuf, "PNG")
    return bytes(buf)


def write_ico(out_path: Path, sizes=SIZES) -> None:
    """Assemble a multi-resolution ICO file from in-memory PNGs.

    ICO format:
      ICONDIR (6 bytes)            : reserved=0, type=1, count=N
      ICONDIRENTRY (16 bytes × N)  : per-image header
      image data (PNG bytes × N)   : packed sequentially
    """
    pngs = [render_png(s) for s in sizes]
    n = len(pngs)

    out = bytearray()
    out += struct.pack("<HHH", 0, 1, n)  # ICONDIR

    image_offset = 6 + 16 * n
    for size, png in zip(sizes, pngs):
        # In ICO, width/height of 256 is encoded as 0.
        s = 0 if size >= 256 else size
        # B B B B  H H  I I
        # w h ncolors reserved  planes bpp  bytesInRes offset
        out += struct.pack(
            "<BBBBHHII",
            s, s, 0, 0,
            1, 32,
            len(png),
            image_offset,
        )
        image_offset += len(png)

    for png in pngs:
        out += png

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(bytes(out))


def main() -> int:
    # QPixmap requires a QApplication.
    app = QApplication(sys.argv)
    write_ico(OUT_PATH)
    print(f"wrote {OUT_PATH.relative_to(ROOT)}  ({OUT_PATH.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
