"""Release readiness engine — Phase 5E.3.

Reads the baked dashboard files in `apps/admin/data/` and returns:

  • a six-dimension breakdown (install / trust / alpha / docs /
    screenshots / release), each scored 0..1;
  • a single 0-100 readiness score (the directive's
    READINESS_SCORE.md);
  • an overall verdict (GREEN / YELLOW / RED);
  • a one-line headline + a short list of blocking items.

This is the *internal* readiness lens — not a marketing number. It
does not leave the machine; the founder CLI is the only consumer.
Reads files only; no network.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Per the directive: six inputs, weighted.
_WEIGHTS = {
    "install":     25,
    "trust":       20,
    "alpha":       20,
    "release":     15,
    "docs":        10,
    "screenshots": 10,
}
assert sum(_WEIGHTS.values()) == 100


@dataclass
class Dimension:
    id: str
    label: str
    score: float        # 0..1
    weight: int         # 0..100
    state: str          # GREEN / YELLOW / RED
    detail: str


@dataclass
class Readiness:
    score: int                       # 0..100
    state: str                       # GREEN / YELLOW / RED
    headline: str
    blockers: list[str]
    dimensions: list[Dimension]


# --------------------------------------------------------------- helpers


def _state(score01: float) -> str:
    if score01 >= 0.75:
        return "GREEN"
    if score01 >= 0.40:
        return "YELLOW"
    return "RED"


def _read(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


# --------------------------------------------------------------- dimensions


def _score_install(release: dict) -> tuple[float, str]:
    installer = release.get("installer", "blocked")
    signing = release.get("signing", "unsigned")
    base = {"ready": 1.0, "partial": 0.5, "blocked": 0.0}.get(installer, 0.0)
    bonus = 0.2 if signing == "signed" else 0.0
    score = min(1.0, base + bonus)
    detail = f"installer={installer}, signing={signing}"
    return score, detail


def _score_trust(trust_cards: list[dict]) -> tuple[float, str]:
    if not trust_cards:
        return 0.0, "no trust data"
    states = [c.get("state", "red") for c in trust_cards]
    g = states.count("green")
    y = states.count("yellow")
    r = states.count("red")
    total = max(1, len(states))
    score = (g + 0.5 * y) / total
    # A single red bad-recoveries kills trust.
    if any(c.get("id") == "bad_recoveries" and c.get("state") == "red"
           for c in trust_cards):
        score = min(score, 0.2)
    return score, f"{g} green / {y} yellow / {r} red across {len(states)} cards"


def _score_alpha(cohorts: list[dict]) -> tuple[float, str]:
    if not cohorts:
        return 0.0, "no cohorts"
    active = [c for c in cohorts if c.get("status") in ("forming", "active")]
    total_devices = sum(int(c.get("devices") or 0) for c in active)
    returning = sum(int(c.get("returning") or 0) for c in active)
    if total_devices == 0:
        return 0.0, "no installed devices yet"
    return_pct = returning / total_devices
    # Two signals: enough devices, and they come back.
    devices_score = min(1.0, total_devices / 20.0)
    return_score = min(1.0, return_pct / 0.5)
    score = 0.5 * devices_score + 0.5 * return_score
    return score, (
        f"{total_devices} devices in {len(active)} cohort(s), "
        f"{int(return_pct * 100)}% returning"
    )


def _score_release(release: dict) -> tuple[float, str]:
    g = {"GO": 1.0, "PARTIAL": 0.5, "NO-GO": 0.0}.get(
        release.get("go_no_go", "NO-GO"), 0.0
    )
    blocked = release.get("blocked") or []
    # A long blocker list shaves off the partial credit.
    penalty = min(0.3, 0.05 * len(blocked))
    score = max(0.0, g - penalty)
    return score, (
        f"{release.get('go_no_go', 'NO-GO')}, "
        f"{len(blocked)} blocker(s)"
    )


def _score_docs(health: list[dict], trust: list[dict],
                feedback: list[dict]) -> tuple[float, str]:
    """`docs` is a proxy: did the baked surfaces fill, did anyone
    flag confusion. We never know "are the docs good" automatically;
    we know "are users still asking questions about basic things"."""
    if not health and not trust:
        return 0.0, "dashboard surfaces empty"
    confusion = sum(1 for f in feedback if f.get("tag") == "confusion")
    # Filled surfaces = 0.7 base; subtract for every confusion entry.
    base = 0.7
    score = max(0.0, base - 0.05 * confusion + 0.3 * (len(health) >= 4))
    return min(1.0, score), (
        f"{len(feedback)} feedback entr{'y' if len(feedback)==1 else 'ies'}, "
        f"{confusion} confusion-tagged"
    )


def _score_screenshots(release: dict) -> tuple[float, str]:
    s = release.get("screenshots", "missing")
    score = {"complete": 1.0, "partial": 0.5, "missing": 0.0}.get(s, 0.0)
    return score, f"screenshots={s}"


# --------------------------------------------------------------- engine


def compute(data_dir: Optional[Path] = None) -> Readiness:
    data = data_dir or (Path(__file__).resolve().parents[2]
                        / "apps" / "admin" / "data")

    release = _read(data / "release.json", {}) or {}
    trust_cards = _read(data / "trust.json", []) or []
    cohorts = _read(data / "cohorts.json", []) or []
    health = _read(data / "health.json", []) or []
    feedback = _read(data / "feedback.json", []) or []

    dims_def = [
        ("install",     "Installer",   *_score_install(release)),
        ("trust",       "Trust",       *_score_trust(trust_cards)),
        ("alpha",       "Alpha",       *_score_alpha(cohorts)),
        ("release",     "Release",     *_score_release(release)),
        ("docs",        "Docs",        *_score_docs(health, trust_cards, feedback)),
        ("screenshots", "Screenshots", *_score_screenshots(release)),
    ]
    dims: list[Dimension] = []
    score_acc = 0.0
    for id_, label, s01, detail in dims_def:
        w = _WEIGHTS[id_]
        dims.append(Dimension(
            id=id_, label=label,
            score=round(s01, 3), weight=w,
            state=_state(s01), detail=detail,
        ))
        score_acc += s01 * w

    score = int(round(score_acc))
    if score >= 80:
        state = "GREEN"
    elif score >= 50:
        state = "YELLOW"
    else:
        state = "RED"

    blockers = list(release.get("blocked") or [])

    if state == "GREEN":
        headline = "Ready to tag the next milestone."
    elif state == "YELLOW":
        headline = "Path is clear; named blockers remain."
    else:
        headline = "Not yet shippable. Start with the named blockers."

    return Readiness(
        score=score, state=state,
        headline=headline, blockers=blockers,
        dimensions=dims,
    )
