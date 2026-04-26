"""LLM-backed pre-call brief and post-call analysis.

Both calls embed the V14.1 master script + AI coach prompt as system context so the
analysis is grounded in our 6-layer / 8-prompt-core / Hope Break discipline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_SCRIPT_PATH = REPO_ROOT / "docs" / "v14.1" / "LV_MASTER_SCRIPT_V14_1.md"
COACH_PROMPT_PATH = REPO_ROOT / "coach" / "V14_1_AI_SALES_COACH_PROMPT.md"


def _safe_read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


@dataclass
class PreCallBrief:
    client_type_hypothesis: list[str] = field(default_factory=list)
    suggested_q_path: list[str] = field(default_factory=list)
    expected_objections: list[str] = field(default_factory=list)
    coi_math: str = ""
    critical_mistake: str = ""
    raw_response: str = ""


@dataclass
class PostCallAnalysis:
    score_1_to_13: int = 0
    weakest_node: str = ""
    what_worked: list[str] = field(default_factory=list)
    what_to_change: list[str] = field(default_factory=list)
    next_step_phrase: str = ""
    next_step_due: str = ""
    raw_response: str = ""


class LLMAnalyzer:
    def __init__(self, provider: str, api_key: str | None, model: str, temperature: float = 0.2):
        self._provider = provider
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._coach = _safe_read(COACH_PROMPT_PATH)
        self._master = _safe_read(MASTER_SCRIPT_PATH)

    def _system_prompt(self, mode: str) -> str:
        return (
            f"{self._coach}\n\n"
            f"# REŽĪMS: {mode}\n\n"
            f"# ZINĀŠANU BĀZE (V14.1 Master Script — saīsināts):\n{self._master[:18000]}"
        )

    def _chat(self, system: str, user: str) -> str:
        if not self._api_key:
            return "[LLM disabled — no API key in env]"
        if self._provider == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=self._api_key)
            response = client.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content or ""
        if self._provider == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=self._api_key)
            response = client.messages.create(
                model=self._model,
                max_tokens=1500,
                temperature=self._temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return "".join(block.text for block in response.content if hasattr(block, "text"))
        raise ValueError(f"Unknown LLM provider: {self._provider}")

    def pre_call(self, prospect_json: dict[str, Any]) -> PreCallBrief:
        system = self._system_prompt("pre_call")
        user = (
            "Atgriez JSON ar laukiem: client_type_hypothesis (saraksts), "
            "suggested_q_path (saraksts), expected_objections (saraksts), "
            "coi_math (string), critical_mistake (string).\n\n"
            f"PROSPECT:\n{json.dumps(prospect_json, ensure_ascii=False)}"
        )
        raw = self._chat(system, user)
        data = _coerce_json(raw)
        return PreCallBrief(
            client_type_hypothesis=list(data.get("client_type_hypothesis", []) or []),
            suggested_q_path=list(data.get("suggested_q_path", []) or []),
            expected_objections=list(data.get("expected_objections", []) or []),
            coi_math=str(data.get("coi_math", "") or ""),
            critical_mistake=str(data.get("critical_mistake", "") or ""),
            raw_response=raw,
        )

    def post_call(self, transcript_text: str, meta: dict[str, Any] | None = None) -> PostCallAnalysis:
        system = self._system_prompt("post_call")
        user = (
            "Atgriez JSON ar laukiem: score_1_to_13 (vesels), weakest_node (string), "
            "what_worked (saraksts ar 3), what_to_change (saraksts ar 3 dict {moment, alt_phrase}), "
            "next_step_phrase (string), next_step_due (ISO datums).\n\n"
            f"META: {json.dumps(meta or {}, ensure_ascii=False)}\n\n"
            f"TRANSKRIPTS:\n{transcript_text[:20000]}"
        )
        raw = self._chat(system, user)
        data = _coerce_json(raw)
        return PostCallAnalysis(
            score_1_to_13=int(data.get("score_1_to_13", 0) or 0),
            weakest_node=str(data.get("weakest_node", "") or ""),
            what_worked=list(data.get("what_worked", []) or []),
            what_to_change=list(data.get("what_to_change", []) or []),
            next_step_phrase=str(data.get("next_step_phrase", "") or ""),
            next_step_due=str(data.get("next_step_due", "") or ""),
            raw_response=raw,
        )


def _coerce_json(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    text = raw.strip()
    # Strip code fences
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {}
    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return {}
