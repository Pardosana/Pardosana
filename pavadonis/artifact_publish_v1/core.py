"""artifact_publish_v1 kodols.

Job formāts:

    {
      "type": "artifact_publish_v1",
      "id": "job-123",                  # neobligāts, nonāk manifestā
      "payload": {
        "source_root": "C:/PAVADONIS/work",   # no kurienes drīkst ņemt failus
        "target_root": "C:/PAVADONIS/publish",# kur publicēt
        "name": "salesengine-v16",            # publikācijas nosaukums [A-Za-z0-9._-]
        "files": ["deck/index.html", "docs/book.pdf"],  # relatīvi pret source_root
        "dry_run": true                        # noklusējums: true
      }
    }

Rezultāts: {"ok": bool, "dry_run": bool, "version": str|None,
            "published_dir": str|None, "files": [...], "error": str|None}

Publicēšana:
  target_root/<name>/<version>/...   — nemainīga versijas mape
  target_root/<name>/current.json    — norāde uz aktīvo versiju
  target_root/<name>/<version>/manifest.json — sha256 un izmēri

Nekas netiek pārrakstīts vai dzēsts: katra publikācija ir jauna versija,
atsaukšana (rollback) tikai pārvieto current.json norādi.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JOB_TYPE = "artifact_publish_v1"

ALLOWED_SUFFIXES = frozenset(
    {".html", ".htm", ".css", ".js", ".json", ".md", ".txt", ".pdf",
     ".docx", ".pptx", ".xlsx", ".csv", ".png", ".jpg", ".jpeg", ".svg",
     ".webp", ".gif", ".mp3", ".mp4", ".woff", ".woff2"}
)
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 500 * 1024 * 1024
MAX_FILES = 500
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class PublishError(Exception):
    """Job noraidīts. Ziņojums ir drošs rādīšanai lietotājam."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_root(raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise PublishError(f"{label} nav norādīts")
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise PublishError(f"{label} nav mape: {root}")
    return root


def _resolve_source(source_root: Path, rel: Any) -> tuple[str, Path]:
    if not isinstance(rel, str) or not rel.strip():
        raise PublishError("tukšs faila ceļš")
    rel_path = Path(rel)
    if rel_path.is_absolute() or rel_path.drive or ".." in rel_path.parts:
        raise PublishError(f"aizliegts ceļš: {rel}")
    candidate = source_root / rel_path
    # Simboliskās saites netiek sekotas — tās varētu izvest ārpus source_root.
    for parent in [candidate, *candidate.parents]:
        if parent == source_root:
            break
        if parent.is_symlink():
            raise PublishError(f"simboliskā saite nav atļauta: {rel}")
    resolved = candidate.resolve()
    if source_root not in resolved.parents:
        raise PublishError(f"ceļš iziet ārpus source_root: {rel}")
    if not resolved.is_file():
        raise PublishError(f"fails nav atrasts: {rel}")
    if resolved.suffix.lower() not in ALLOWED_SUFFIXES:
        raise PublishError(f"faila tips nav atļauts: {rel}")
    return rel_path.as_posix(), resolved


def _plan(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise PublishError("payload nav objekts")
    source_root = _resolve_root(payload.get("source_root"), "source_root")
    target_root = _resolve_root(payload.get("target_root"), "target_root")
    if target_root == source_root or source_root in target_root.parents \
            or target_root in source_root.parents:
        raise PublishError("source_root un target_root nedrīkst pārklāties")

    name = payload.get("name")
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise PublishError("nederīgs name (atļauts A-Z a-z 0-9 . _ -, līdz 64)")

    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise PublishError("files jābūt netukšam sarakstam")
    if len(files) > MAX_FILES:
        raise PublishError(f"pārāk daudz failu (maks. {MAX_FILES})")

    entries, seen, total = [], set(), 0
    for rel in files:
        rel_norm, src = _resolve_source(source_root, rel)
        if rel_norm.lower() in seen:
            raise PublishError(f"dublēts fails: {rel_norm}")
        seen.add(rel_norm.lower())
        size = src.stat().st_size
        if size > MAX_FILE_BYTES:
            raise PublishError(f"fails par lielu: {rel_norm}")
        total += size
        if total > MAX_TOTAL_BYTES:
            raise PublishError("kopējais izmērs par lielu")
        entries.append({"path": rel_norm, "src": src, "bytes": size,
                        "sha256": _sha256(src)})

    dry_run = payload.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise PublishError("dry_run jābūt true/false")
    return {"source_root": source_root, "target_root": target_root,
            "name": name, "entries": entries, "dry_run": dry_run}


def _write_json_atomic(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _publish(plan: dict, job_id: str | None) -> tuple[str, Path]:
    pub_root = plan["target_root"] / plan["name"]
    pub_root.mkdir(exist_ok=True)
    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    final_dir = pub_root / version
    if final_dir.exists():
        raise PublishError("versija jau eksistē, mēģini vēlreiz")

    staging = Path(tempfile.mkdtemp(dir=pub_root, prefix=".staging-"))
    try:
        for e in plan["entries"]:
            dst = staging / e["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(e["src"], dst)
            if _sha256(dst) != e["sha256"]:
                raise PublishError(f"fails mainījās kopēšanas laikā: {e['path']}")
        manifest = {
            "job_type": JOB_TYPE, "job_id": job_id, "name": plan["name"],
            "version": version,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "files": [{k: e[k] for k in ("path", "bytes", "sha256")}
                      for e in plan["entries"]],
        }
        _write_json_atomic(staging / "manifest.json", manifest)
        os.replace(staging, final_dir)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    current = pub_root / "current.json"
    previous = None
    if current.is_file():
        previous = json.loads(current.read_text(encoding="utf-8")).get("version")
    _write_json_atomic(current, {"version": version, "previous": previous})
    return version, final_dir


def handle(job: dict) -> dict:
    """Job-bus ieejas punkts. Nekad nemet izņēmumu uz āru par sliktu job."""
    result: dict = {"ok": False, "dry_run": True, "version": None,
                    "published_dir": None, "files": [], "error": None}
    try:
        if not isinstance(job, dict) or job.get("type") != JOB_TYPE:
            raise PublishError(f"job type nav {JOB_TYPE}")
        plan = _plan(job.get("payload"))
        result["dry_run"] = plan["dry_run"]
        result["files"] = [{k: e[k] for k in ("path", "bytes", "sha256")}
                           for e in plan["entries"]]
        if not plan["dry_run"]:
            version, final_dir = _publish(plan, job.get("id"))
            result["version"] = version
            result["published_dir"] = str(final_dir)
        result["ok"] = True
    except PublishError as exc:
        result["error"] = str(exc)
    except OSError as exc:
        result["error"] = f"failu sistēmas kļūda: {exc.strerror or exc}"
    return result


def rollback(target_root: str, name: str, version: str | None = None) -> dict:
    """Pārslēdz current.json uz iepriekšējo (vai norādīto) versiju. Neko nedzēš."""
    if not _NAME_RE.match(name or ""):
        raise PublishError("nederīgs name")
    pub_root = _resolve_root(target_root, "target_root") / name
    current = pub_root / "current.json"
    if not current.is_file():
        raise PublishError("nav aktīvas publikācijas")
    state = json.loads(current.read_text(encoding="utf-8"))
    target = version or state.get("previous")
    if not target or not _NAME_RE.match(target):
        raise PublishError("nav uz ko atgriezties")
    if not (pub_root / target / "manifest.json").is_file():
        raise PublishError(f"versija nav atrasta: {target}")
    _write_json_atomic(current, {"version": target, "previous": state.get("version")})
    return {"ok": True, "version": target, "previous": state.get("version")}
