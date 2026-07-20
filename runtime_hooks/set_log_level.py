"""PyInstaller runtime hook — default packaged ADIAT builds to WARNING logging.

Wired into the build via ``runtime_hooks`` in ``app.spec``. PyInstaller runs
this during the frozen-app bootstrap, BEFORE ``app/__main__.py``, so the level
is already in the environment by the time ``LoggerService`` is first
constructed. This keeps shipped builds from accumulating verbose debug/info
logs on users' machines.

``setdefault`` (not a plain assignment) means an operator-supplied
``ADIAT_LOG_LEVEL`` still wins — e.g. set ``ADIAT_LOG_LEVEL=DEBUG`` to crank a
shipped build back up for field troubleshooting.

This is intentionally belt-and-suspenders with
``LoggerService.resolve_log_level``'s own ``sys.frozen`` default (both resolve
packaged builds to WARNING); it makes the build's logging policy explicit in
the packaging config. Keep it dependency-free — it runs before the app's
modules are importable.
"""
import os

os.environ.setdefault("ADIAT_LOG_LEVEL", "WARNING")
