"""Minimāls Google Drive v3 klients (tikai standarta bibliotēka).

Tokens netiek glabāts: katrs pieprasījums izsauc `access_token_provider()`,
ko nodrošina PAVADONIS (integrācijas robeža). Tokens nekad nenonāk kļūdu
ziņojumos, rezultātā vai evidence.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Protocol

API = "https://www.googleapis.com/drive/v3"
UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"
METADATA_FIELDS = (
    "id,name,size,mimeType,parents,trashed,md5Checksum,sha256Checksum,"
    "webViewLink,appProperties"
)
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,256}$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
TIMEOUT_S = 60


class DriveError(Exception):
    """Drive API kļūda. Satur tikai HTTP statusu un Drive reason, bez headeriem."""

    def __init__(self, status: int | None, reason: str):
        super().__init__(f"Drive API kļūda ({status}): {reason}")
        self.status = status
        self.reason = reason


class DriveClient(Protocol):
    def find_by_app_property(self, folder_id: str, key: str, value: str) -> list[str]: ...

    def upload(self, *, data: bytes, name: str, folder_id: str, mime_type: str,
               app_properties: dict[str, str]) -> str: ...

    def get_metadata(self, file_id: str) -> dict[str, Any]: ...


def check_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _ID_RE.match(value):
        raise DriveError(None, f"nederīgs {label}")
    return value


class GoogleDriveClient:
    def __init__(self, access_token_provider: Callable[[], str],
                 urlopen: Callable[..., Any] = urllib.request.urlopen):
        self._token = access_token_provider
        self._urlopen = urlopen

    def _request(self, method: str, url: str, *, body: bytes | None = None,
                 headers: dict[str, str] | None = None) -> tuple[dict, Any]:
        hdrs = {"Authorization": f"Bearer {self._token()}", "Cache-Control": "no-cache"}
        hdrs.update(headers or {})
        req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
        try:
            with self._urlopen(req, timeout=TIMEOUT_S) as resp:
                raw = resp.read()
                resp_headers = resp.headers
        except urllib.error.HTTPError as exc:
            raise DriveError(exc.code, _error_reason(exc)) from None
        except urllib.error.URLError as exc:
            raise DriveError(None, f"tīkla kļūda: {exc.reason}") from None
        data = json.loads(raw) if raw else {}
        return data, resp_headers

    def find_by_app_property(self, folder_id: str, key: str, value: str) -> list[str]:
        check_id(folder_id, "folder_id")
        if not re.match(r"^[a-z_]{1,30}$", key) or not _HEX64_RE.match(value):
            raise DriveError(None, "nederīgs appProperties vaicājums")
        q = (f"'{folder_id}' in parents and trashed = false and "
             f"appProperties has {{ key='{key}' and value='{value}' }}")
        params = urllib.parse.urlencode({
            "q": q, "fields": "files(id)", "pageSize": "10",
            "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
        })
        data, _ = self._request("GET", f"{API}/files?{params}")
        return [f["id"] for f in data.get("files", [])]

    def upload(self, *, data: bytes, name: str, folder_id: str, mime_type: str,
               app_properties: dict[str, str]) -> str:
        check_id(folder_id, "folder_id")
        meta = json.dumps({"name": name, "parents": [folder_id],
                           "appProperties": app_properties}).encode("utf-8")
        params = urllib.parse.urlencode({"uploadType": "resumable",
                                         "supportsAllDrives": "true", "fields": "id"})
        _, headers = self._request(
            "POST", f"{UPLOAD_API}/files?{params}", body=meta,
            headers={"Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": mime_type,
                     "X-Upload-Content-Length": str(len(data))})
        session_url = headers.get("Location") if headers else None
        if not session_url or not session_url.startswith(UPLOAD_API + "/"):
            raise DriveError(None, "Drive neatgrieza derīgu upload sesiju")
        result, _ = self._request("PUT", session_url, body=data,
                                  headers={"Content-Type": mime_type,
                                           "Content-Length": str(len(data))})
        return check_id(result.get("id", ""), "file_id")

    def get_metadata(self, file_id: str) -> dict[str, Any]:
        check_id(file_id, "file_id")
        params = urllib.parse.urlencode({"fields": METADATA_FIELDS,
                                         "supportsAllDrives": "true"})
        data, _ = self._request("GET", f"{API}/files/{file_id}?{params}")
        return data


def _error_reason(exc: urllib.error.HTTPError) -> str:
    try:
        body = json.loads(exc.read() or b"{}")
        err = body.get("error", {})
        reasons = [e.get("reason") for e in err.get("errors", []) if e.get("reason")]
        return (reasons[0] if reasons else err.get("status")) or str(exc.reason)
    except (ValueError, AttributeError):
        return str(exc.reason)
