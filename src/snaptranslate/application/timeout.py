from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


class OperationTimeoutError(RuntimeError):
    pass


def run_with_timeout(operation: Callable[[], T], timeout_seconds: float, message: str) -> T:
    result_queue: queue.Queue[tuple[str, T | Exception]] = queue.Queue(maxsize=1)

    def worker() -> None:
        try:
            result = operation()
        except Exception as exc:
            result_queue.put(("error", exc))
        else:
            result_queue.put(("ok", result))

    thread = threading.Thread(target=worker, name="timeout-operation", daemon=True)
    thread.start()
    try:
        kind, value = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        raise OperationTimeoutError(message) from exc
    if kind == "error":
        raise value
    return value
