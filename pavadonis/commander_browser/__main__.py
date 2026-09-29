"""python -m commander_browser status [--port N]
   python -m commander_browser login-state instagram [--port N]
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import DEFAULT_PORT, SITES, login_state, status


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="commander_browser")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    ls = sub.add_parser("login-state")
    ls.add_argument("site", choices=sorted(SITES))
    a = p.parse_args(argv)
    out = status(a.port) if a.cmd == "status" else login_state(a.site, a.port)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    ok = out.get("running") and (a.cmd == "status" or out.get("logged_in") is True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
