"""Chain-of-Verification loop (V_exist -> V_secure -> V_relevant) with mitigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from halluguard.extractor import Dependency, resolve_dependencies
from halluguard.mitigation import MitigationModule, ReasonCode
from halluguard.registry_client import RegistryClient
from halluguard.relevance_judge import RelevanceJudge
from halluguard.security_score import SecurityScorer


class Outcome(str, Enum):
    VERIFIED = "verified"
    FAILED = "failed"            # exhausted regeneration attempts
    INDETERMINATE = "indeterminate"  # a data source was unreachable; human review required
    UNPARSEABLE = "unparseable"  # generated code is not valid Python


@dataclass(frozen=True)
class Rejection:
    attempt: int
    dependency: Dependency
    reason: ReasonCode


@dataclass
class VerificationOutcome:
    outcome: Outcome
    final_code: str | None
    attempts: int
    rejections: list[Rejection] = field(default_factory=list)


class HalluGuardVerifier:
    def __init__(self, generator, registry: RegistryClient, scorer: SecurityScorer,
                 judge: RelevanceJudge, mitigation: MitigationModule,
                 module_to_package: dict[str, str], max_attempts: int) -> None:
        self._generate = generator          # callable(prompt) -> code
        self._registry = registry
        self._scorer = scorer
        self._judge = judge
        self._mitigation = mitigation
        self._module_map = module_to_package
        self._max_attempts = max_attempts

    def verify_and_mitigate(self, prompt: str) -> VerificationOutcome:
        code = self._generate(prompt)
        rejections: list[Rejection] = []

        for attempt in range(1, self._max_attempts + 1):
            try:
                deps = resolve_dependencies(code, self._module_map)
            except SyntaxError:
                return VerificationOutcome(Outcome.UNPARSEABLE, code, attempt, rejections)

            failure = self._first_failure(deps, prompt)
            if failure is None:
                return VerificationOutcome(Outcome.VERIFIED, code, attempt, rejections)
            if failure == "indeterminate":
                return VerificationOutcome(Outcome.INDETERMINATE, code, attempt, rejections)

            dep, reason = failure
            rejections.append(Rejection(attempt, dep, reason))
            code = self._mitigation.regenerate(prompt, code, dep.package_name, reason)

        return VerificationOutcome(Outcome.FAILED, None, self._max_attempts, rejections)

    def _first_failure(self, deps: list[Dependency], prompt: str):
        """Short-circuit chain: returns None (all pass), 'indeterminate', or (dep, reason)."""
        for dep in deps:
            exist = self._registry.verify_existence(dep)
            if exist.exists is None:
                return "indeterminate"
            if not exist.exists:
                return dep, ReasonCode.NOT_EXIST

            sec = self._scorer.score(dep)
            if sec.passed is None:
                return "indeterminate"
            if not sec.passed:
                return dep, ReasonCode.INSECURE

            rel = self._judge.judge(dep, prompt)
            if rel.relevant is None:
                return "indeterminate"
            if not rel.relevant:
                return dep, ReasonCode.NOT_RELEVANT
        return None
