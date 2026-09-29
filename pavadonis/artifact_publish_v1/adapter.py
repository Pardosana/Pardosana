"""artifact_publish_v1 adapteris PAVADONIS ProductionWorker.

Integrācijas robeža (neko neminam par PAVADONIS iekšieni):

  * `result_factory(result, evidence, artifacts)`: jānodod PAVADONIS
    `ExecutionResult`. Noklusējums ir tikai testiem.
  * `approval_verifier(digest, payload) -> bool`: jāpārbauda, ka
    PAVADONIS approval ir piesaistīts TIEŠI šim payload digest. Obligāts,
    noklusējuma nav: bez tā adapteri nevar izveidot.
  * `payload_from_spec(spec) -> Mapping`: kā no `spec` iegūt apstiprināto
    payload. Noklusējums: pats `spec`.
  * `drive_client`: `GoogleDriveClient(access_token_provider=...)`, kur
    tokens nāk no PAVADONIS esošās credential glabātuves.

Kļūme jebkurā posmā → `ArtifactPublishBlocked` (nekad DONE/VERIFIED).
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from .drive import DriveClient, DriveError

ADAPTER_NAME = "artifact_publish_v1"
PAYLOAD_FIELDS = ("source_path", "expected_sha256", "expected_size",
                  "provider", "destination", "file_name")
IDEMPOTENCY_KEY = "pav_idem"
DEFAULT_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".docx",
                    ".xlsx", ".pptx", ".csv", ".txt", ".md", ".json", ".html",
                    ".mp3", ".mp4", ".zip")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_BAD_NAME_RE = re.compile(r'[\x00-\x1f\x7f/\\]')


class ArtifactPublishBlocked(Exception):
    """Darbs jāatzīmē BLOCKED. `evidence` nesatur secrets."""

    def __init__(self, reason: str, evidence: dict | None = None):
        super().__init__(reason)
        self.reason = reason
        self.evidence = evidence or {}


@dataclass(frozen=True)
class _DefaultExecutionResult:
    result: dict
    evidence: dict
    artifacts: list


@dataclass(frozen=True)
class ArtifactPublishConfig:
    allow_roots: tuple[str, ...]
    destinations: Mapping[str, tuple[str, ...]]  # provider -> atļautie folder ID
    max_bytes: int = 50 * 1024 * 1024
    allowed_suffixes: tuple[str, ...] = DEFAULT_SUFFIXES

    def __post_init__(self):
        if not self.allow_roots:
            raise ValueError("allow_roots nedrīkst būt tukšs")
        if not self.destinations:
            raise ValueError("destinations nedrīkst būt tukšs")
        if self.max_bytes <= 0:
            raise ValueError("max_bytes jābūt > 0")

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ArtifactPublishConfig":
        kwargs: dict[str, Any] = {
            "allow_roots": tuple(raw["allow_roots"]),
            "destinations": {p: tuple(ids) for p, ids in raw["destinations"].items()},
        }
        if "max_bytes" in raw:
            kwargs["max_bytes"] = int(raw["max_bytes"])
        if "allowed_suffixes" in raw:
            kwargs["allowed_suffixes"] = tuple(s.lower() for s in raw["allowed_suffixes"])
        return cls(**kwargs)

    @classmethod
    def from_file(cls, path: str | os.PathLike) -> "ArtifactPublishConfig":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


def payload_digest(payload: Mapping[str, Any]) -> str:
    """Kanonisks SHA256 no sešiem payload laukiem. Approval jāpiesaista šim."""
    canon = {k: payload.get(k) for k in PAYLOAD_FIELDS}
    raw = json.dumps(canon, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _norm(p: Path) -> str:
    return os.path.normcase(str(p))


def _is_under(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([_norm(path), _norm(root)]) == _norm(root) \
            and _norm(path) != _norm(root)
    except ValueError:  # dažādi diski Windows
        return False


def _is_link(p: Path) -> bool:
    is_junction = getattr(p, "is_junction", None)
    return p.is_symlink() or bool(is_junction and is_junction())


class ArtifactPublishV1Adapter:
    name = ADAPTER_NAME

    def __init__(self, config: ArtifactPublishConfig, *, drive_client: DriveClient,
                 approval_verifier: Callable[[str, Mapping[str, Any]], bool],
                 result_factory: Callable[..., Any] = _DefaultExecutionResult,
                 payload_from_spec: Callable[[Any], Mapping[str, Any]] = lambda s: s):
        if approval_verifier is None:
            raise ValueError("approval_verifier ir obligāts")
        self._cfg = config
        self._roots = tuple(Path(r).resolve() for r in config.allow_roots)
        # Saites pārbaude apstājas pie root, kā tas rakstīts konfigurācijā vai atrisināts.
        self._root_stops = {_norm(Path(r).absolute()) for r in config.allow_roots} \
            | {_norm(r) for r in self._roots}
        self._drive = drive_client
        self._approved = approval_verifier
        self._make_result = result_factory
        self._payload_from_spec = payload_from_spec

    # ---------- validācija (pirms jebkādas ārējas darbības) ----------

    def _validate(self, payload: Mapping[str, Any]) -> dict:
        if not isinstance(payload, Mapping):
            raise ArtifactPublishBlocked("payload nav objekts")
        missing = [k for k in PAYLOAD_FIELDS if k not in payload]
        if missing:
            raise ArtifactPublishBlocked(f"trūkst payload lauku: {', '.join(missing)}")

        provider = payload["provider"]
        if provider not in self._cfg.destinations:
            raise ArtifactPublishBlocked(f"provider nav atļauts: {provider!r}")
        destination = payload["destination"]
        if destination not in self._cfg.destinations[provider]:
            raise ArtifactPublishBlocked("destination nav allowlist sarakstā")

        file_name = payload["file_name"]
        if not isinstance(file_name, str) or not file_name.strip() \
                or len(file_name) > 255 or _BAD_NAME_RE.search(file_name) \
                or file_name in (".", ".."):
            raise ArtifactPublishBlocked("nederīgs file_name")

        sha = payload["expected_sha256"]
        if not isinstance(sha, str) or not _HEX64_RE.match(sha.lower()):
            raise ArtifactPublishBlocked("expected_sha256 nav 64 hex simboli")
        size = payload["expected_size"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ArtifactPublishBlocked("expected_size nav nenegatīvs vesels skaitlis")
        if size > self._cfg.max_bytes:
            raise ArtifactPublishBlocked("expected_size pārsniedz max_bytes")

        source = self._validate_source(payload["source_path"])
        return {"provider": provider, "destination": destination,
                "file_name": file_name, "expected_sha256": sha.lower(),
                "expected_size": size, "source": source}

    def _validate_source(self, raw: Any) -> Path:
        if not isinstance(raw, str) or not raw.strip():
            raise ArtifactPublishBlocked("source_path nav norādīts")
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise ArtifactPublishBlocked("source_path jābūt absolūtam ceļam")
        if ".." in candidate.parts:
            raise ArtifactPublishBlocked("source_path nedrīkst saturēt '..'")
        for part in [candidate, *candidate.parents]:
            if _norm(part) in self._root_stops:
                break
            if _is_link(part):
                raise ArtifactPublishBlocked("source_path satur saiti (symlink/junction)")
        resolved = candidate.resolve()
        if not any(_is_under(resolved, r) for r in self._roots):
            raise ArtifactPublishBlocked("source_path nav zem atļautā allow_root")
        try:
            st = resolved.stat()
        except OSError:
            raise ArtifactPublishBlocked("source_path neeksistē") from None
        if not stat.S_ISREG(st.st_mode):
            raise ArtifactPublishBlocked("source_path nav parasts fails")
        if resolved.suffix.lower() not in self._cfg.allowed_suffixes:
            raise ArtifactPublishBlocked(f"faila tips nav atļauts: {resolved.suffix}")
        if st.st_size > self._cfg.max_bytes:
            raise ArtifactPublishBlocked("fails pārsniedz max_bytes")
        return resolved

    # ---------- izpilde ----------

    def execute(self, spec: Any) -> Any:
        payload = self._payload_from_spec(spec)
        v = self._validate(payload)
        digest = payload_digest(payload)
        if self._approved(digest, payload) is not True:
            raise ArtifactPublishBlocked("nav approval, kas piesaistīts šim payload",
                                         {"payload_digest": digest})

        # Viena nolasīšana: augšupielādē tieši tos baitus, kuriem aprēķināts hash.
        data = v["source"].read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
        local = {"source_path": str(v["source"]), "sha256": sha256, "bytes": len(data),
                 "payload_digest": digest}
        if len(data) != v["expected_size"]:
            raise ArtifactPublishBlocked("size mismatch pirms upload", local)
        if sha256 != v["expected_sha256"]:
            raise ArtifactPublishBlocked("SHA256 mismatch pirms upload", local)

        idem = hashlib.sha256("|".join(
            (sha256, v["provider"], v["destination"], v["file_name"])).encode()).hexdigest()
        try:
            existing = self._drive.find_by_app_property(v["destination"], IDEMPOTENCY_KEY, idem)
            if len(existing) > 1:
                raise ArtifactPublishBlocked("galamērķī jau ir vairāki šī artefakta faili",
                                             {**local, "existing_file_ids": existing})
            reused = bool(existing)
            if reused:
                file_id = existing[0]
            else:
                mime = mimetypes.guess_type(v["file_name"])[0] or "application/octet-stream"
                file_id = self._drive.upload(data=data, name=v["file_name"],
                                             folder_id=v["destination"], mime_type=mime,
                                             app_properties={IDEMPOTENCY_KEY: idem})
            meta = self._drive.get_metadata(file_id)
        except DriveError as exc:
            raise ArtifactPublishBlocked(str(exc), local) from None

        expected = {"file_id": file_id, "file_name": v["file_name"], "bytes": len(data),
                    "sha256": sha256, "md5": md5, "destination": v["destination"],
                    "idempotency_key": idem}
        readback, compare = _readback(meta), _compare(meta, expected)
        result = {
            "provider": v["provider"], "source_path": str(v["source"]),
            "sha256": sha256, "md5": md5, "bytes": len(data),
            "file_id": file_id, "file_name": v["file_name"],
            "destination": v["destination"], "url": meta.get("webViewLink"),
            "idempotency_key": idem, "reused_existing": reused,
            "readback": readback, "compare": compare,
        }
        evidence = {**local, "readback": readback, "compare": compare,
                    "reused_existing": reused}
        if not compare["match"]:
            raise ArtifactPublishBlocked("Drive readback nesakrīt ar avota failu", evidence)
        artifacts = [{"type": "google_drive_file", "file_id": file_id,
                      "url": meta.get("webViewLink"), "source_sha256": sha256}]
        return self._make_result(result=result, evidence=evidence, artifacts=artifacts)

    def verify(self, result: Mapping[str, Any]) -> dict:
        """Svaigs neatkarīgs readback verify_task() vajadzībām. Nekad nemet izņēmumu."""
        expected = {k: result.get(k) for k in
                    ("file_id", "file_name", "bytes", "sha256", "md5",
                     "destination", "idempotency_key")}
        try:
            meta = self._drive.get_metadata(expected["file_id"])
        except DriveError as exc:
            return {"verified": False, "error": str(exc), "readback": None, "compare": None}
        compare = _compare(meta, expected)
        return {"verified": compare["match"], "readback": _readback(meta), "compare": compare}


def _readback(meta: Mapping[str, Any]) -> dict:
    keep = ("id", "name", "size", "mimeType", "parents", "trashed",
            "sha256Checksum", "md5Checksum", "webViewLink")
    return {k: meta.get(k) for k in keep}


def _compare(meta: Mapping[str, Any], exp: Mapping[str, Any]) -> dict:
    checks = {
        "file_id": meta.get("id") == exp["file_id"],
        "file_name": meta.get("name") == exp["file_name"],
        "bytes": str(meta.get("size")) == str(exp["bytes"]),
        "destination": exp["destination"] in (meta.get("parents") or []),
        "not_trashed": meta.get("trashed") is False,
        "idempotency_key": (meta.get("appProperties") or {}).get(IDEMPOTENCY_KEY)
        == exp["idempotency_key"],
    }
    if meta.get("sha256Checksum"):
        checks["sha256"] = meta["sha256Checksum"].lower() == exp["sha256"]
    elif meta.get("md5Checksum"):
        checks["md5"] = meta["md5Checksum"].lower() == exp["md5"]
    else:
        checks["checksum_present"] = False
    return {"checks": checks, "match": all(checks.values())}
