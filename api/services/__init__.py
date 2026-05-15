"""Service layer for the local memory API.

Four explicit boundaries, each backed by an existing Phase 1
module so prior phases aren't rewritten — only re-exposed:

  • StorageService        — wraps EventLogger + EventStore (Phase 1A)
  • IngestionService      — validates + sanitizes + persists (Phase 1B)
  • RetrievalService      — episodic search + file search (Phase 1C)
  • ReconstructionService — sessions + micro-contexts (Phase 1E + 1F)

Each service is a thin facade. The work lives in `app/core/*`; the
service layer adds HTTP-shaped methods and pydantic-shaped types.
"""

from .evolution import EvolutionService
from .ingestion import IngestionService
from .reconstruction import ReconstructionService
from .recovery import RecoveryService
from .resurfacing import ResurfacingService
from .retrieval import RetrievalService
from .storage import StorageService
from .threads import ThreadsService

__all__ = [
    "StorageService",
    "IngestionService",
    "RetrievalService",
    "ReconstructionService",
    "ResurfacingService",
    "ThreadsService",
    "EvolutionService",
    "RecoveryService",
]
