import os
import re
import sys

from prometheus_client import multiprocess


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)

def worker_exit(server, worker):
    # A worker recycled by --max-requests can hang in interpreter shutdown
    # (native thread pools, see #1008) until the arbiter kills it after
    # --timeout; with one worker nothing is served for that long.
    # gunicorn also runs this hook in the arbiter for an already reaped
    # worker, so only the worker process itself is ended here.
    if os.getpid() != worker.pid:
        return
    sys.stdout.flush()
    sys.stderr.flush()
    code = getattr(sys.exc_info()[1], "code", 1)
    os._exit(code if isinstance(code, int) else 1)

def on_starting(server):
    # Parse command line arguments
    proc_name = server.cfg.default_proc_name
    kwargs = {}
    if proc_name.startswith("wsgi:app"):
        str_args = re.sub(r'wsgi:app\s*\(\s*(.*)\s*\)', '\\1', proc_name).strip().split(",")
        for a in str_args:
            if "=" in a:
                k,v = a.split("=")
                k = k.strip()
                v = v.strip()

                if v.lower() in ["true", "false"]:
                    v = v.lower() == "true"
                    if not v:
                        continue
                elif v[0] == '"':
                    v = v[1:-1]
                kwargs[k] = v

    from libretranslate.main import get_args
    sys.argv = ['--wsgi']

    for k in kwargs:
        ck = k.replace("_", "-")
        if isinstance(kwargs[k], bool) and kwargs[k]:
            sys.argv.append("--" + ck)
        else:
            sys.argv.append("--" + ck)
            sys.argv.append(kwargs[k])

    args = get_args()

    from libretranslate import flood, scheduler, secret, storage, cache
    storage.setup(args.shared_storage)
    cache.setup(args.translation_cache)
    scheduler.setup(args)
    flood.setup(args)
    secret.setup(args)