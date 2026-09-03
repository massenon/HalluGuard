"""V_relevant: binary contextual-relevance judgement by a separate LLM."""

from __future__ import annotations

from dataclasses import dataclass

from halluguard.extractor import Dependency
from halluguard.llm import Completer
from halluguard.prompts import RELEVANCE_SYSTEM, RELEVANCE_USER


@dataclass(frozen=True)
class RelevanceResult:
    dependency: Dependency
    relevant: bool | None      # None => unparseable judge output (escalate)
    raw_response: str


class RelevanceJudge:
    def __init__(self, completer: Completer, temperature: float, max_tokens: int = 8) -> None:
        self._completer = completer
        self._temperature = temperature
        self._max_tokens = max_tokens

    def judge(self, dep: Dependency, original_prompt: str) -> RelevanceResult:
        user = RELEVANCE_USER.format(
            original_prompt=original_prompt,
            package_name=dep.package_name,
            version_specifier=dep.version_specifier or "unspecified",
        )
        raw = self._completer.complete(RELEVANCE_SYSTEM, user, self._temperature, self._max_tokens)
        verdict = raw.strip().lower().rstrip(".")
        relevant = True if verdict == "yes" else False if verdict == "no" else None
        return RelevanceResult(dep, relevant, raw)
