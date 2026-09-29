"""artifact_publish_v1 — PAVADONIS production_worker adapteris.

Publicē lietotāja skaidri autorizētu lokālu failu uz allowlist galamērķi
(pašlaik tikai Google Drive) un pēc augšupielādes veic neatkarīgu readback.

Integrācijas robeža ar PAVADONIS ir aprakstīta INSTALL.md. Šī pakete neko
neimportē no PAVADONIS: ExecutionResult, approval pārbaude un Drive
piekļuves tokens tiek padoti no ārpuses.
"""

from .adapter import (
    ADAPTER_NAME,
    ArtifactPublishBlocked,
    ArtifactPublishConfig,
    ArtifactPublishV1Adapter,
    payload_digest,
)
from .drive import DriveError, GoogleDriveClient

__all__ = [
    "ADAPTER_NAME",
    "ArtifactPublishBlocked",
    "ArtifactPublishConfig",
    "ArtifactPublishV1Adapter",
    "DriveError",
    "GoogleDriveClient",
    "payload_digest",
]
