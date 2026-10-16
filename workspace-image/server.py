"""Browser terminal for PrairieLearn workspaces that runs only gdb."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from launcher import build_command
from terminado.management import UniqueTermManager
from terminado.websocket import TermSocket
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

HERE = Path(__file__).resolve().parent


class IndexHandler(RequestHandler):
    """Serve only index.html (never the rest of this directory)."""

    def get(self, *_: Any) -> None:
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.write((HERE / "index.html").read_text())


class GdbTermSocket(TermSocket):
    home = "/home/student"
    uid = 1001
    gid = 1001

    def check_origin(self, origin: str) -> bool:
        return True  # PrairieLearn proxies from another origin

    def open(self, *args: Any, **kwargs: Any) -> Any:
        if os.getuid() == 0:
            # Local dev: PrairieLearn copies workspace files in as root after
            # the container starts. (In production we already run as 1001.)
            subprocess.run(
                ["chown", "-R", f"{self.uid}:{self.gid}", self.home], check=False
            )
        return super().open(*args, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--uid", type=int, default=1001)
    parser.add_argument("--gid", type=int, default=1001)
    parser.add_argument("--home", default="/home/student")
    parser.add_argument("--gdb-scripts", default="/opt/gdb")
    args = parser.parse_args()

    # Same idea as Checkpoint's runtime.program_args (a JSON list).
    program_args = json.loads(os.environ.get("PROGRAM_ARGS", "[]"))
    run_uses_shell = os.environ.get("GDB_RUN_USES_SHELL", "0") == "1"

    command = build_command(
        uid=args.uid,
        gid=args.gid,
        home=args.home,
        program_args=program_args,
        script_dir=args.gdb_scripts,
        run_uses_shell=run_uses_shell,
        running_as_root=os.getuid() == 0,
    )
    print("Terminal command:", command, flush=True)

    GdbTermSocket.home, GdbTermSocket.uid, GdbTermSocket.gid = (
        args.home, args.uid, args.gid,
    )
    term_manager = UniqueTermManager(shell_command=command)

    app = Application(
        [
            (r"/terminals/(.*)", GdbTermSocket, {"term_manager": term_manager}),
            (r"/.*", IndexHandler),
        ],
        websocket_ping_interval=30,
    )
    app.listen(args.port, "0.0.0.0")
    print(f"Terminal server listening on {args.port}", flush=True)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
