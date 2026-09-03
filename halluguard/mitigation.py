"""Mitigation and Regeneration Module: structured correction prompt + regeneration."""

from __future__ import annotations

from enum import Enum

from halluguard.llm import Completer
from halluguard.prompts import MITIGATION_SYSTEM, MITIGATION_USER


class ReasonCode(str, Enum):
    NOT_EXIST = "does not exist on PyPI"
    INSECURE = "has known critical vulnerabilities (CVE: {cve_id})"
    NOT_RELEVANT = "is not contextually relevant to the stated task"


def build_correction_prompt(original_prompt: str, flawed_code: str, package_name: str,
                            reason: ReasonCode, cve_id: str = "unspecified") -> str:
    """The complete flawed snippet is always included, never truncated."""
    return MITIGATION_USER.format(
        original_prompt=original_prompt,
        flawed_code=flawed_code,
        package_name=package_name,
        reason_code=reason.value.format(cve_id=cve_id),
    )


class MitigationModule:
    def __init__(self, completer: Completer, temperature: float, max_tokens: int) -> None:
        self._completer = completer
        self._temperature = temperature
        self._max_tokens = max_tokens

    def regenerate(self, original_prompt: str, flawed_code: str, package_name: str,
                   reason: ReasonCode, cve_id: str = "unspecified") -> str:
        user = build_correction_prompt(original_prompt, flawed_code, package_name, reason, cve_id)
        return self._completer.complete(MITIGATION_SYSTEM, user, self._temperature, self._max_tokens)
