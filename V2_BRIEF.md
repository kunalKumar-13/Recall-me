# V2_BRIEF.md — north star

Recall is a continuity layer for unfinished work. When someone returns after
minutes, hours, or days, Recall helps them continue exactly where they left
off. It is NOT a launcher, NOT search, NOT a memory database. Recovery is the
hero; search is secondary.

The Python engine + FastAPI service at `127.0.0.1:4545` and its seven layers
are the core IP — do NOT rewrite them. A new launcher comes later as a thin
client over the existing HTTP API.

v1 mistakes to avoid: search-first thinking, building UI before the data is
real, and repeatedly rewriting the launcher.
