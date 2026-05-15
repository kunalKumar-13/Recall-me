"""Recall local memory API — Phase 2A.

A FastAPI service that owns event ingestion, episodic retrieval,
session reconstruction, and micro-context reconstruction. Runs
in-process inside the desktop daemon, bound to 127.0.0.1 only.

Public entry points:

  • `create_app(...)`  — build the FastAPI app for tests or custom
                         hosting.
  • `APIService(...)`  — wraps the app in a uvicorn server that
                         can be started/stopped from a Qt thread.
"""

from .main import APIService, create_app

__all__ = ["APIService", "create_app"]
