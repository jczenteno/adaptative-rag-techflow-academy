"""PostgreSQL connection pool utilities.

This module provides a process-wide connection pool that can be initialized
once at application startup and reused anywhere (e.g., inside tools).
"""

from __future__ import annotations

import os
from typing import Optional

from psycopg_pool import ConnectionPool

_pool: Optional[ConnectionPool] = None


def init_pool(dsn: Optional[str] = None, min_size: int = 1, max_size: int = 10) -> ConnectionPool:
    """Initialize a global connection pool if not already created.

    Parameters
    ----------
    dsn: Optional[str]
        PostgreSQL connection string. If not provided, reads from
        environment variables ``POSTGRES_URL`` or ``DATABASE_URL``.
    min_size: int
        Minimum number of pooled connections.
    max_size: int
        Maximum number of pooled connections.

    Returns
    -------
    ConnectionPool
        The initialized global connection pool.
    """
    global _pool
    if _pool is not None:
        return _pool

    effective_dsn = dsn or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
    if not effective_dsn:
        raise ValueError("POSTGRES_URL o DATABASE_URL no está configurado en el entorno")

    _pool = ConnectionPool(effective_dsn, min_size=min_size, max_size=max_size)
    return _pool


def get_pool() -> ConnectionPool:
    """Get the global connection pool, initializing it lazily if needed."""
    global _pool
    if _pool is None:
        init_pool()
    assert _pool is not None
    return _pool


def close_pool() -> None:
    """Close the global connection pool if it exists."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


