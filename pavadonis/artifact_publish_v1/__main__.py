"""CLI: python -m pavadonis.artifact_publish_v1 --job job.json
       python -m pavadonis.artifact_publish_v1 --rollback TARGET_ROOT NAME [VERSION]
"""

from __future__ import annotations

import argparse
import json
import sys

from .core import PublishError, handle, rollback


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="artifact_publish_v1")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--job", help="ceļš uz job JSON failu ('-' = stdin)")
    g.add_argument("--rollback", nargs="+", metavar="ARG",
                   help="TARGET_ROOT NAME [VERSION]")
    args = p.parse_args(argv)

    if args.job:
        raw = sys.stdin.read() if args.job == "-" else open(args.job, encoding="utf-8").read()
        out = handle(json.loads(raw))
    else:
        if len(args.rollback) not in (2, 3):
            p.error("--rollback vajag TARGET_ROOT NAME [VERSION]")
        try:
            out = rollback(*args.rollback)
        except PublishError as exc:
            out = {"ok": False, "error": str(exc)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
