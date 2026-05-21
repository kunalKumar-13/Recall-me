"""Generate the Phase 5H proof GIFs from existing static captures.

The directive lists five GIFs: install, launcher, recovery, extension,
control room. Three are derivable deterministically from PNG state
cycles already on disk (launcher, recovery, extension); two need a
live screen recording (install, control room) - those are documented
in `docs/release/RECORDING_PROTOCOL.md`.

Each generated GIF cycles through the input PNGs with a per-frame
hold. The output is a real motion artifact (same pixels every run),
not a placeholder - it shows the surface evolving through its real
states.

    python infra/scripts/capture/generate_demo_gifs.py
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "assets" / "screenshots"
OUT = ROOT / "assets" / "demos"
OUT.mkdir(parents=True, exist_ok=True)

# (output name, frame list, per-frame ms, loop). Order = visual story.
# Frame paths are relative to SRC.
GIFS: list[tuple[str, list[str], int, int]] = [
    # launcher: shows the popup growing from blank to a populated digest.
    (
        "launcher.gif",
        [
            "launcher-loading.png",
            "launcher-empty.png",
            "launcher-first-week.png",
            "launcher-digest.png",
        ],
        1400,  # hold each frame ~1.4 s
        0,
    ),
    # recovery: the two-state focus animation (resting -> keyboard focus).
    (
        "recovery.gif",
        [
            "recovery-card.png",
            "recovery-card-focused.png",
        ],
        1000,
        0,
    ),
    # extension: the popup state cycle a tester experiences in week one.
    (
        "extension.gif",
        [
            "extension-loading.png",
            "extension-empty.png",
            "extension-capturing.png",
            "extension-connected.png",
        ],
        1400,
        0,
    ),
]


def _pad_to_max(frames: list[Image.Image]) -> list[Image.Image]:
    """All frames in a GIF must share a canvas. Source PNGs vary in
    height (launcher-digest is tall, launcher-empty short); pad shorter
    frames to the max with a transparent strip so the GIF doesn't
    stretch."""
    max_w = max(f.width for f in frames)
    max_h = max(f.height for f in frames)
    out: list[Image.Image] = []
    for f in frames:
        if f.size == (max_w, max_h):
            out.append(f.convert("RGBA"))
            continue
        canvas = Image.new("RGBA", (max_w, max_h), (255, 255, 255, 255))
        # top-anchor; the surface visually grows downward.
        canvas.paste(f.convert("RGBA"), (0, 0))
        out.append(canvas)
    return out


def _build(name: str, frame_files: list[str], hold_ms: int, loop: int) -> Path:
    frames = [Image.open(SRC / f) for f in frame_files]
    padded = _pad_to_max(frames)
    out_path = OUT / name
    padded[0].save(
        out_path,
        save_all=True,
        append_images=padded[1:],
        duration=hold_ms,
        loop=loop,
        disposal=2,
        optimize=True,
    )
    return out_path


def main() -> None:
    for name, files, hold, loop in GIFS:
        missing = [f for f in files if not (SRC / f).exists()]
        if missing:
            print(f"  skip {name}: missing {missing}")
            continue
        out = _build(name, files, hold, loop)
        size_kb = out.stat().st_size / 1024
        print(f"  wrote {out.relative_to(ROOT)}  ({size_kb:,.1f} kB, {len(files)} frames)")
    print()
    print("Deferred (need live screen recording, see docs/release/RECORDING_PROTOCOL.md):")
    print("  - install.gif      (Recall-Setup.exe wizard, ~60 s)")
    print("  - control-room.gif (apps/admin/web at localhost:3000)")


if __name__ == "__main__":
    main()
