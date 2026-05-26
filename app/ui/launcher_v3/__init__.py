"""Phase 6O — launcher v3 package (reset).

The launcher overbuilt; this package was reset to a single
calm surface. Search, CONTINUE (HIGH recovery only), OTHER
WORK (max three titles), or empty. Nothing else.

What stays:

  - ``theme``                  colour / radius / shadow / spacing tokens
  - ``motion``                 timing constants (unused in the reset
                               but kept for downstream callers)
  - ``surfaces``               GlassCard + a few primitives — the
                               minimal layout doesn't import most
                               of them, but they're available for
                               capture scripts.
  - ``recovery_panel``         ``RecoveryCardV3`` — single fixed
                               100 px hero. No signal variants.
  - ``investigation_panel``    ``InvestigationCardV3`` (bare-text
                               title) + ``InvestigationRow``
                               (max-3 equal-width row).
  - ``minimal``                ``MinimalSearchBar`` ·
                               ``MinimalDigest`` · ``MinimalEmpty`` ·
                               ``MinimalShell`` · ``MinimalWindow``.
                               680 × 460. Paper white.
  - ``live``                   ``LiveLauncher`` — gates the hero on
                               ``confidence == "high"``; otherwise
                               shows the empty surface.
  - ``search_panel``           inline search results (unchanged
                               from 6I; still optional).
  - ``digest``                 the legacy `DigestColumn`/`EmptyDigest`
                               from 6I — preserved for backwards
                               compatibility with the launcher_legacy
                               escape hatch only. **Not used by the
                               reset launcher.**
  - ``trust_panel``            the legacy three-row trust panel —
                               preserved for the legacy escape
                               hatch only. **Not used by the reset
                               launcher.**

What moved to ``archive/launcher-overbuild/``:

  - the pre-reset ``minimal.py`` (preview card, returns row,
    overflow chip, trust line, dividers)
  - the pre-reset ``recovery_panel.py`` (signal variants,
    confidence sentence, chip cap)
  - the pre-reset ``investigation_panel.py`` (status dots,
    pill chrome, ``sort_for_digest``)
  - the pre-reset capture scripts (``capture_launcher_compact``,
    ``capture_launcher_recovery``)

Nothing in ``app/``, ``infra/``, or ``apps/`` imports from the
archive; the files are reference, not a code path.
"""

from .investigation_panel import (
    InvestigationCardV3,
    InvestigationList,
    InvestigationRow,
)
from .live import LiveLauncher
from .minimal import (
    MinimalDigest,
    MinimalEmpty,
    MinimalSearchBar,
    MinimalShell,
    MinimalWindow,
    TrustRow,
)
from .recent_memory import MemoryRow, RecentMemoryList
from .recovery_panel import RecoveryCardV3
from .restore_toast import RestoreToast
from .resume_preview import ResumePreview
from .search_panel import SearchPanel, SearchResult
from .surfaces import (
    ConfidenceBadge,
    FloatingPanel,
    GlassCard,
    Pill,
    SoftDivider,
    StatusDot,
    TimelineChip,
    section_label,
)
from .trust_panel import TrustPanel

__all__ = [
    "ConfidenceBadge",
    "FloatingPanel",
    "GlassCard",
    "InvestigationCardV3",
    "InvestigationList",
    "InvestigationRow",
    "LiveLauncher",
    "MemoryRow",
    "MinimalDigest",
    "MinimalEmpty",
    "MinimalSearchBar",
    "MinimalShell",
    "MinimalWindow",
    "Pill",
    "RecentMemoryList",
    "RecoveryCardV3",
    "RestoreToast",
    "TrustRow",
    "ResumePreview",
    "SearchPanel",
    "SearchResult",
    "SoftDivider",
    "StatusDot",
    "TimelineChip",
    "TrustPanel",
    "section_label",
]
