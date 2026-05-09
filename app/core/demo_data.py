"""Curated sample memories for demo mode.

When `RECALL_DEMO=1` (or `--demo` is passed), the launcher uses
`DemoSearchEngine` instead of the real one — so the product is
demonstrable in screenshots and recordings without ever indexing real
files. The data tells four small overlapping stories so a wide range
of natural-language queries land somewhere believable:

  * a healthcare-startup thread (pitch deck + agent code + onboarding)
  * RL paper notes + reward-shaping experiments
  * production websocket retry / debug log (recent work)
  * project pitch / market sizing / whiteboard photo

Each memory carries a `keywords` list used for cheap substring scoring
in `DemoSearchEngine.search` — no embedding model is loaded.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List

from .search import SearchResult


@dataclass
class _DemoMemory:
    path: str
    name: str
    ext: str
    chunk: str
    snippet: str
    mtime_days_ago: int
    keywords: List[str] = field(default_factory=list)


# Story 1 — healthcare-agents startup thread (older, the resurrection
# story for "that healthcare startup idea from last winter")
_HEALTHCARE = [
    _DemoMemory(
        path="~/Documents/healthcare-startup/pitch_deck_v3.pdf",
        name="pitch_deck_v3.pdf",
        ext=".pdf",
        chunk=(
            "Healthcare agents pitch deck v3.\n\n"
            "Core thesis: pediatric triage routing via natural-language "
            "intake. The agent classifies urgency and matches to "
            "specialists, with a human reviewer in the loop for the first "
            "thousand episodes. Market: pediatric clinics in tier-2 US "
            "cities; initial wedge is the after-hours triage pager. "
            "Reimbursement model: per-episode flat fee, billed to the "
            "clinic, not the patient."
        ),
        snippet=(
            "…pediatric triage routing via natural-language intake. The "
            "agent classifies urgency and matches to specialists…"
        ),
        mtime_days_ago=118,
        keywords=[
            "healthcare", "startup", "pitch", "deck", "agents", "agent",
            "triage", "pediatric", "clinic", "winter",
        ],
    ),
    _DemoMemory(
        path="~/Documents/healthcare-startup/agent.py",
        name="agent.py",
        ext=".py",
        chunk=(
            "class TriageAgent:\n"
            '    """Routes pediatric intake messages to a specialist queue."""\n\n'
            "    def __init__(self, model, specialists):\n"
            "        self.model = model\n"
            "        self.specialists = specialists\n\n"
            "    def classify(self, message: str) -> Urgency:\n"
            "        # Three-bucket urgency: emergency, same-day, routine.\n"
            "        ..."
        ),
        snippet="class TriageAgent: routes pediatric intake messages to a specialist queue.",
        mtime_days_ago=110,
        keywords=[
            "healthcare", "agent", "agents", "triage", "code", "python",
            "class", "specialist",
        ],
    ),
    _DemoMemory(
        path="~/Documents/healthcare-startup/founders.md",
        name="founders.md",
        ext=".md",
        chunk=(
            "# Onboarding flow notes\n\n"
            "First-call script for the after-hours pager. We talk to the "
            "parent for ninety seconds, then the agent makes the routing "
            "decision. If urgency is emergency, we skip the queue and "
            "page the on-call MD directly.\n\n"
            "Aditi flagged that we need a fallback when the model is "
            "uncertain — default to human triage with a soft note."
        ),
        snippet=(
            "First-call script for the after-hours pager. The agent makes "
            "the routing decision after ninety seconds…"
        ),
        mtime_days_ago=105,
        keywords=[
            "healthcare", "onboarding", "founders", "startup", "agent",
            "triage", "notes",
        ],
    ),
    _DemoMemory(
        path="~/Documents/healthcare-startup/market_sizing.txt",
        name="market_sizing.txt",
        ext=".txt",
        chunk=(
            "Market sizing draft.\n\n"
            "There are ~17,000 pediatric primary-care clinics in the US. "
            "Roughly 30% have an after-hours triage pager service, "
            "currently mostly outsourced to nursing call centers. "
            "ARPU target: $4,800/yr. Wedge of 1% in three years = $20M ARR."
        ),
        snippet="Market sizing draft. ~17,000 pediatric clinics in the US…",
        mtime_days_ago=100,
        keywords=[
            "healthcare", "market", "sizing", "startup", "draft",
            "pediatric", "winter",
        ],
    ),
]

# Story 2 — RL research notes
_RL = [
    _DemoMemory(
        path="~/Notes/papers/rl_grading_notes.md",
        name="rl_grading_notes.md",
        ext=".md",
        chunk=(
            "# RL grading paper notes\n\n"
            "The paper proposes a learned reward model trained on pairwise "
            "human preferences over agent rollouts. Headline result: 8% "
            "improvement on HumanEval-style tasks vs hand-tuned shaping. "
            "Open question: how brittle is the reward model under "
            "distribution shift?"
        ),
        snippet=(
            "Learned reward model trained on pairwise human preferences over "
            "agent rollouts…"
        ),
        mtime_days_ago=62,
        keywords=[
            "rl", "paper", "grading", "reward", "notes", "agents",
            "research", "evaluation",
        ],
    ),
    _DemoMemory(
        path="~/Code/rl-experiments/reward_shaping.py",
        name="reward_shaping.py",
        ext=".py",
        chunk=(
            "def shape_reward(trajectory, baseline=0.0):\n"
            '    """Apply potential-based reward shaping.\n\n'
            "    Idea from Ng et al — adding a potential function to the\n"
            "    reward keeps the optimal policy invariant while accelerating\n"
            '    convergence."""\n'
            "    ..."
        ),
        snippet="Potential-based reward shaping — keeps optimal policy invariant…",
        mtime_days_ago=55,
        keywords=["rl", "reward", "shaping", "code", "python", "research"],
    ),
]

# Story 3 — recent production work (websocket retry)
_WEBSOCKETS = [
    _DemoMemory(
        path="~/Code/server/transport/client.py",
        name="client.py",
        ext=".py",
        chunk=(
            "def reconnect_with_backoff(client, base=0.5, cap=30.0):\n"
            '    """Exponential backoff with jitter on websocket reconnect.\n\n'
            "    The retry budget resets after the first frame is "
            "successfully\n"
            '    received from the server."""\n'
            "    delay = base\n"
            "    while not client.connected:\n"
            "        time.sleep(min(delay, cap) + random.uniform(0, 0.4))\n"
            "        delay *= 2"
        ),
        snippet=(
            "Exponential backoff with jitter on websocket reconnect. Retry "
            "budget resets after first frame received…"
        ),
        mtime_days_ago=18,
        keywords=[
            "websocket", "retry", "reconnect", "backoff", "client", "code",
            "server", "logic",
        ],
    ),
    _DemoMemory(
        path="~/Code/server/logs/2026-04-22-outage.log",
        name="2026-04-22-outage.log",
        ext=".log",
        chunk=(
            "[14:02:11] WARN  websocket: connection closed by remote\n"
            "[14:02:11] INFO  reconnecting (attempt 1) in 0.5s\n"
            "[14:02:12] WARN  websocket: handshake refused (HTTP 503)\n"
            "[14:02:13] INFO  reconnecting (attempt 2) in 1.2s\n"
            "[14:02:15] INFO  reconnecting (attempt 3) in 2.4s\n"
            "[14:02:21] INFO  reconnected; retry budget reset"
        ),
        snippet=(
            "websocket: connection closed by remote — reconnecting (attempt "
            "1) in 0.5s…"
        ),
        mtime_days_ago=18,
        keywords=["websocket", "log", "outage", "retry", "reconnect", "debug"],
    ),
]

# Story 4 — older pitch & whiteboard
_PITCH = [
    _DemoMemory(
        path="~/Documents/decks/project_pitch_v2.docx",
        name="project_pitch_v2.docx",
        ext=".docx",
        chunk=(
            "Project pitch v2 — for the Wednesday partner meeting. "
            "Highlights: agent-based triage, $20M ARR target, two-year "
            "runway with current burn. Risks: regulation, model "
            "calibration, channel access into clinics."
        ),
        snippet="Project pitch v2 — agent-based triage, $20M ARR target…",
        mtime_days_ago=92,
        keywords=["pitch", "deck", "project", "startup", "winter"],
    ),
    _DemoMemory(
        path="~/Documents/healthcare-startup/whiteboard_2026_01_28.jpg",
        name="whiteboard_2026_01_28.jpg",
        ext=".jpg",
        chunk=(
            "Photo of the whiteboard from the Jan 28 working session — "
            "system diagram of the triage agent: intake → classifier → "
            "specialist matcher → human-in-the-loop reviewer."
        ),
        snippet="Whiteboard from Jan 28 — triage agent system diagram.",
        mtime_days_ago=95,
        keywords=["whiteboard", "photo", "agent", "triage", "diagram"],
    ),
]


_DEMO_MEMORIES: List[_DemoMemory] = (
    _HEALTHCARE + _RL + _WEBSOCKETS + _PITCH
)


# ----------------------------------------------------------------- engine


class _DemoStore:
    """Drop-in replacement for VectorStore in demo mode.

    Provides exactly the surface the launcher reads: `count()` and
    `get_indexed_files()`. Both are derived from the in-memory demo
    dataset, so the digest panel renders without ever touching ChromaDB.
    """

    def __init__(self, memories: List[_DemoMemory]) -> None:
        self._memories = memories

    def count(self) -> int:
        # Pretend each memory contributed ~6 chunks to the index, just so
        # the settings status line ("Remembering N passages") looks plausible.
        return len(self._memories) * 6

    def get_indexed_files(self) -> Dict[str, float]:
        now = time.time()
        return {
            m.path: now - (m.mtime_days_ago * 86400.0)
            for m in self._memories
        }


class DemoSearchEngine:
    """In-memory keyword scorer that returns SearchResult objects.

    Same interface as `SearchEngine.search` — the launcher cannot tell
    the difference. No model load, no Chroma client, no I/O. Activated
    by the `RECALL_DEMO` env var or `--demo` CLI flag at app boot.
    """

    def __init__(self) -> None:
        self._memories = _DEMO_MEMORIES
        self.store = _DemoStore(self._memories)

    def search(
        self,
        query: str,
        top_k: int = 8,
        min_score: float | None = None,
        dedupe_by_file: bool = True,
    ) -> List[SearchResult]:
        q = (query or "").strip().lower()
        if not q:
            return []

        # Tokenize: words of length >= 3.
        tokens = [t for t in q.replace("'", " ").split() if len(t) >= 3]
        if not tokens:
            return []

        floor = 0.10 if min_score is None else float(min_score)
        now = time.time()

        scored: List[tuple[float, _DemoMemory]] = []
        for mem in self._memories:
            score = 0.0
            lname = mem.name.lower()
            lchunk = mem.chunk.lower()
            keywords = {k.lower() for k in mem.keywords}

            for tok in tokens:
                if tok in lname:
                    score += 0.30
                if tok in lchunk:
                    score += 0.20
                # Keyword set hit (catches morphological variants we curated)
                for kw in keywords:
                    if tok == kw or (len(tok) >= 4 and tok in kw):
                        score += 0.18
                        break

            # Exact-phrase boost (multi-word query)
            if " " in q and q in lchunk:
                score += 0.10

            # Mild recency boost so newer items win on ties.
            if mem.mtime_days_ago < 30:
                score += 0.04
            elif mem.mtime_days_ago < 90:
                score += 0.02

            if score >= floor:
                # Compress to a 0..1 range that visually matches real
                # similarity scores (the relevance pill uses 0.65 / 0.45).
                scored.append((min(1.0, score / 1.5), mem))

        scored.sort(key=lambda kv: kv[0], reverse=True)
        return [
            SearchResult(
                path=m.path,
                name=m.name,
                snippet=m.snippet,
                chunk=m.chunk,
                score=s,
                ext=m.ext,
                chunk_index=0,
            )
            for s, m in scored[:top_k]
        ]
