"""Post-call orchestration: pull Fathom transcript, run LLM analysis, write CRM."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .crm_writer import CRMUpdate, CRMWriter
from .fathom_client import FathomClient
from .llm_analyzer import LLMAnalyzer, PostCallAnalysis


def analyze_meeting(
    meeting_id: str,
    fathom: FathomClient,
    analyzer: LLMAnalyzer,
    crm: CRMWriter | None,
    contact_email: str | None = None,
) -> dict[str, Any]:
    transcript = fathom.fetch_transcript(meeting_id)
    analysis: PostCallAnalysis = analyzer.post_call(
        transcript_text=transcript.text,
        meta={"meeting_id": meeting_id, "summary": transcript.summary, "action_items": transcript.action_items},
    )

    crm_result = None
    if crm is not None and contact_email:
        update = CRMUpdate(
            contact_email=contact_email,
            deal_stage=_stage_from_score(analysis.score_1_to_13),
            score=analysis.score_1_to_13,
            summary=transcript.summary or "",
            next_step=analysis.next_step_phrase,
            next_step_due=analysis.next_step_due,
        )
        crm_result = crm.write(update)

    return {
        "meeting_id": meeting_id,
        "analysis": asdict(analysis),
        "crm_result": crm_result,
    }


def _stage_from_score(score: int) -> str:
    if score >= 11:
        return "won_or_close"
    if score >= 8:
        return "negotiation"
    if score >= 5:
        return "qualified"
    if score >= 1:
        return "discovery"
    return "unknown"
