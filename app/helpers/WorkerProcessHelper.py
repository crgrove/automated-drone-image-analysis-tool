"""Run tasks in worker processes that can be killed at any moment.

Kept free of heavy imports: each worker process imports this module on start.
"""
import time
from collections import deque
from multiprocessing import Pipe, Process
from multiprocessing.connection import wait


def _worker_main(conn, target):
    """Worker process: run target(*args) for each request until the pipe closes."""
    try:
        while True:
            conn.send(target(*conn.recv()))
    except EOFError:
        pass


def run_in_workers(tasks, num_processes, cancel_conn, target, timeout):
    """Run target(*args) for each (key, args) task across worker processes.

    Yields (key, result) as each task finishes. result is an exception when the
    task's worker died or exceeded `timeout` seconds; that worker is replaced,
    so a bad task costs only itself. Returns as soon as `cancel_conn` becomes
    readable. Every worker still alive is killed when the generator finishes or
    is closed - which is how a cancel stops tasks already in progress.

    Not multiprocessing.Pool: Pool sends every result through one shared pipe,
    and on Windows Pool.terminate() stops reading that pipe, writes a sentinel
    into it and only then kills the workers. Workers holding results bigger
    than the pipe's buffer (AOI lists routinely are) keep it full, so the
    sentinel never lands and terminate() deadlocks; under Python 3.12 the same
    race can instead raise "concurrent send_bytes() calls are not supported".
    Here each worker has its own pipe, and nothing is ever written to a pipe
    nobody reads.

    Args:
        tasks: Iterable of (key, args) pairs; key identifies the task in results.
        num_processes: Maximum number of worker processes.
        cancel_conn: Connection that becomes readable when the run is cancelled.
        target: Picklable callable run in the workers as target(*args).
        timeout: Seconds a single task may run before its worker is killed.
    """
    queue = deque(tasks)
    busy = {}  # parent end of a worker's pipe -> (process, key, deadline)

    def spawn():
        conn, child_conn = Pipe()
        process = Process(target=_worker_main, args=(child_conn, target), daemon=True)
        process.start()
        child_conn.close()
        return conn, process

    def assign(conn, process):
        if not queue:
            stop(conn, process)
            return
        key, args = queue.popleft()
        conn.send(args)
        busy[conn] = (process, key, time.monotonic() + timeout)

    def stop(conn, process):
        process.kill()
        process.join()
        conn.close()

    if cancel_conn.poll():
        return
    try:
        # Spawn all before sending: a send larger than the pipe buffer blocks
        # until that child has finished importing and starts reading.
        for worker in [spawn() for _ in range(min(num_processes, len(queue)))]:
            assign(*worker)
        while busy:
            soonest = min(deadline for _, _, deadline in busy.values())
            ready = wait([*busy, cancel_conn], timeout=max(0, soonest - time.monotonic()))
            if cancel_conn in ready:
                return
            for conn in list(busy):
                process, key, deadline = busy[conn]
                if conn in ready:
                    try:
                        result = conn.recv()
                    except Exception as e:
                        del busy[conn]
                        stop(conn, process)
                        yield key, RuntimeError(f"Worker process exited unexpectedly ({e!r})")
                        if queue:
                            assign(*spawn())
                        continue
                    yield key, result  # still in busy, so a close() here kills it
                    del busy[conn]
                    assign(conn, process)
                elif time.monotonic() >= deadline:
                    del busy[conn]
                    stop(conn, process)
                    yield key, TimeoutError(f"Processing exceeded {timeout}s and was skipped")
                    if queue:
                        assign(*spawn())
    finally:
        for conn, (process, _, _) in busy.items():
            stop(conn, process)
