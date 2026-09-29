"""artifact_publish_v1 — publicē lokālus artefaktus drošā publicēšanas mapē.

Pieņemtais job-bus līgums (pielāgo PAVADONIS reģistrācijai, ja atšķiras):

    handle(job: dict) -> dict

Tikai standarta bibliotēka. Nav tīkla piekļuves. Pēc noklusējuma dry-run.
"""

from .core import JOB_TYPE, PublishError, handle, rollback

__all__ = ["JOB_TYPE", "PublishError", "handle", "rollback"]
