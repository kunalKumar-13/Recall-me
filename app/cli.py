"""Command-line interface for the retrieval engine.

Used to validate retrieval quality before any UI exists. Run as:

    python -m app.cli add /path/to/notes
    python -m app.cli index
    python -m app.cli search "websocket retry"
    python -m app.cli repl                 # interactive — model loads ONCE
    python -m app.cli stats

Note: each one-shot CLI invocation is a fresh Python process and reloads
the embedding model. Use `repl` for sub-100ms iteration on queries while
testing retrieval quality. The eventual launcher is tray-resident, so
this is purely a Phase 1A testing concern.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import Recall
from .core.indexer import IndexProgress


def _truncate(text: str, n: int) -> str:
    s = " ".join((text or "").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def cmd_add(args: argparse.Namespace) -> int:
    r = Recall()
    if r.add_folder(args.path):
        print(f"Added: {Path(args.path).expanduser().resolve()}")
    else:
        print(f"Skipped (missing or already added): {args.path}", file=sys.stderr)
    print(f"Folders ({len(r.folders)}):")
    for f in r.folders:
        print(f"  {f}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    r = Recall()
    print("Removed." if r.remove_folder(args.path) else "Not in folder list.")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    r = Recall()
    if not r.folders:
        print("No folders configured. Use `add` first.", file=sys.stderr)
        return 1

    last = [0.0]

    def cb(p: IndexProgress) -> None:
        now = time.time()
        if now - last[0] < 0.2 and p.files_done < p.files_total:
            return
        last[0] = now
        line = (
            f"\r{p.files_done}/{p.files_total} files · "
            f"{p.chunks_added} chunks · {_truncate(p.current_file, 40):<40s}"
        )
        sys.stderr.write(line)
        sys.stderr.flush()

    print("Indexing… (first run downloads the embedding model, ~80MB)")
    result = r.index(on_progress=cb)
    sys.stderr.write("\n")
    new_files = result.files_done - result.files_skipped
    print(
        f"Done. {new_files} file(s) embedded, "
        f"{result.files_skipped} skipped (unchanged or unsupported), "
        f"{result.chunks_added} chunks added."
    )
    return 0


def _print_results(query: str, results, elapsed_ms: int) -> None:
    if not results:
        print(f"No results above floor.  ({elapsed_ms}ms)")
        return
    print(f"Top {len(results)} for: {query!r}   ({elapsed_ms}ms)")
    print()
    for i, hit in enumerate(results, 1):
        print(f"{i}. {hit.score:>5.0%}  {hit.name}")
        print(f"      {hit.path}")
        print(f"      {_truncate(hit.snippet, 220)}")
        print()


def cmd_search(args: argparse.Namespace) -> int:
    r = Recall()
    if r.store.count() == 0:
        print("Index is empty. Run `add` then `index` first.", file=sys.stderr)
        return 1

    t0 = time.time()
    results = r.search(args.query, k=args.k, min_score=args.min)
    elapsed_ms = int((time.time() - t0) * 1000)
    _print_results(args.query, results, elapsed_ms)
    return 0


def cmd_repl(args: argparse.Namespace) -> int:
    """Persistent-process REPL — model loads once, queries are sub-100ms."""
    r = Recall()
    if r.store.count() == 0:
        print("Index is empty. Run `add` then `index` first.", file=sys.stderr)
        return 1

    print("Recall REPL — type a query, blank line or Ctrl+D to quit.")
    sys.stdout.write("Loading model… ")
    sys.stdout.flush()
    t0 = time.time()
    r.model.encode_one("warmup")  # one-time load on this process
    print(f"ready ({int((time.time() - t0) * 1000)}ms).\n")

    while True:
        try:
            query = input("recall> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            break
        t0 = time.time()
        results = r.search(query, k=args.k, min_score=args.min)
        elapsed_ms = int((time.time() - t0) * 1000)
        _print_results(query, results, elapsed_ms)
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    r = Recall()
    s = r.stats()
    print(f"Model:       {s['model']}")
    print(f"Chunks:      {s['chunks']}")
    print(f"Folders ({len(s['folders'])}):")
    for f in s["folders"]:
        print(f"  {f}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.yes:
        confirm = input("Delete all embeddings? Folder list is preserved. [y/N] ")
        if confirm.strip().lower() not in {"y", "yes"}:
            print("Cancelled.")
            return 0
    Recall().reset()
    print("Index cleared.")
    return 0


def cmd_folders(args: argparse.Namespace) -> int:
    r = Recall()
    if not r.folders:
        print("(none)")
        return 0
    for f in r.folders:
        print(f)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="recall",
        description="Recall — local semantic memory engine (Phase 1A: core only).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="add a folder to the index list")
    p.add_argument("path")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("remove", help="remove a folder from the index list")
    p.add_argument("path")
    p.set_defaults(fn=cmd_remove)

    p = sub.add_parser("folders", help="list configured folders")
    p.set_defaults(fn=cmd_folders)

    p = sub.add_parser("index", help="(re)index all configured folders")
    p.set_defaults(fn=cmd_index)

    p = sub.add_parser("search", help="run a semantic query")
    p.add_argument("query")
    p.add_argument("-k", type=int, default=8, help="number of results (default: 8)")
    p.add_argument(
        "--min",
        type=float,
        default=None,
        help="minimum cosine-similarity score, 0–1 (default: 0.30)",
    )
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser(
        "repl",
        help="interactive REPL — model loads once, fast successive queries",
    )
    p.add_argument("-k", type=int, default=8)
    p.add_argument("--min", type=float, default=None)
    p.set_defaults(fn=cmd_repl)

    p = sub.add_parser("stats", help="show index size and configured folders")
    p.set_defaults(fn=cmd_stats)

    p = sub.add_parser("reset", help="wipe all embeddings (folder list preserved)")
    p.add_argument("--yes", action="store_true", help="skip confirmation")
    p.set_defaults(fn=cmd_reset)

    args = parser.parse_args(argv)
    return int(args.fn(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
