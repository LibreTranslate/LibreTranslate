import subprocess
import sys
from pathlib import Path

import pytest

GUNICORN_CONF = Path(__file__).resolve().parents[2] / "scripts" / "gunicorn_conf.py"

LOAD_CONF = """
import importlib.util
import os
import sys
import threading
import types

spec = importlib.util.spec_from_file_location("gunicorn_conf", sys.argv[1])
conf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conf)
"""

# A worker that leaves like gunicorn's spawn_worker does (sys.exit inside
# try/finally, worker_exit in the finally) while a non-daemon thread keeps
# the interpreter from shutting down.
RECYCLED_WORKER = LOAD_CONF + """
threading.Thread(target=threading.Event().wait).start()
try:
    sys.exit(3)
finally:
    if sys.argv[2] == "hook":
        conf.worker_exit(None, types.SimpleNamespace(pid=os.getpid()))
"""

ARBITER = LOAD_CONF + """
conf.worker_exit(None, types.SimpleNamespace(pid=os.getpid() + 1))
print("alive")
"""


def run(script, *args, timeout):
    return subprocess.run(
        [sys.executable, "-c", script, str(GUNICORN_CONF), *args],
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout,
    )


def test_worker_exit_ends_a_recycled_worker_with_its_exit_code():
    result = run(RECYCLED_WORKER, "hook", timeout=60)
    assert result.returncode == 3, result.stderr


def test_without_worker_exit_the_same_worker_hangs():
    with pytest.raises(subprocess.TimeoutExpired):
        run(RECYCLED_WORKER, "bare", timeout=3)


def test_worker_exit_in_the_arbiter_leaves_the_arbiter_running():
    result = run(ARBITER, timeout=60)
    assert (result.returncode, result.stdout.strip()) == (0, "alive"), result.stderr
