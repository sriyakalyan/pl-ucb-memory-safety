"""Minimal browser terminal for PrairieLearn workspaces (no grading / missions)."""
import argparse
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

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


class PermissiveTermSocket(TermSocket):
    """Terminal websocket; PrairieLearn proxies from a different origin."""

    workdir = "/home/student"
    user = "student"

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self, *args: Any, **kwargs: Any) -> Any:
        # PrairieLearn copies workspace files in as root *after* the container
        # starts, so make sure the student owns them by the time a shell opens.
        subprocess.run(
            ["chown", "-R", f"{self.user}:{self.user}", self.workdir], check=False
        )
        return super().open(*args, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--user", required=True)
    parser.add_argument("--workdir", required=True)
    args = parser.parse_args()

    PermissiveTermSocket.workdir = args.workdir
    PermissiveTermSocket.user = args.user

    program = os.environ.get("TERMINAL_PROGRAM", "bash")
    setup = os.environ.get("TERMINAL_SETUP", "").strip()

    command = f"cd {shlex.quote(args.workdir)}"
    if setup:
        command += f" && {setup}"
    command += f" && exec {program}"

    term_manager = UniqueTermManager(
        shell_command=["su", "-l", args.user, "--session-command", command]
    )

    app = Application(
        [
            (r"/terminals/(.*)", PermissiveTermSocket, {"term_manager": term_manager}),
            (r"/.*", IndexHandler),
        ],
        websocket_ping_interval=30,  # keeps the proxied connection alive
    )
    app.listen(args.port, "0.0.0.0")
    print(f"Terminal server listening on {args.port}", flush=True)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
