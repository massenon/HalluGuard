"""
verifier.py
------------
Main orchestration loop implementing Algorithm 1 (HalluGuard CoV
Process / VerifyAndMitigate) from Section 3.4.

This is the entry point that ties together:
  - registry_client.py   (V_exist)
  - security_score.py    (V_secure)
  - relevance_judge.py   (V_relevant)
  - mitigation.py         (Mitigation & Regeneration Module)
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from registry_client import RegistryClient, Dependency
from security_score import calculate_security_score
from relevance_judge import CrossModelJudge
from mitigation import MitigationModule, MitigationRequest

logger = logging.getLogger("halluguard.verifier")


@dataclass
class VerificationOutcome:
    final_code: Optional[str]
    success: bool
    iterations_used: int
    rejection_log: list = field(default_factory=list)


class HalluGuardVerifier:
    """
    Implements Algorithm 1: VerifyAndMitigate(P, k).

    Sequential, short-circuiting Chain-of-Verification:
        V_pkg(d_i, P) = V_exist(d_i) -> V_secure(d_i) -> V_relevant(d_i, P)
    A failure at any stage halts the chain for that dependency and
    triggers the Mitigation Module before re-entering the loop.
    """

    def __init__(self, llm_client_factory, popular_packages: list[str],
                 module_dictionary: dict, config: dict):
        self.registry = RegistryClient()
        self.judge = CrossModelJudge(llm_client_factory)
        self.mitigation = MitigationModule(llm_client_factory)
        self.llm_client_factory = llm_client_factory
        self.popular_packages = popular_packages
        self.module_dictionary = module_dictionary
        self.config = config

    def extract_dependencies(self, code: str, ecosystem: str = "python") -> list[Dependency]:
        """
        Stage 1 (Section 3.3.1): AST/tree-sitter parsing to extract
        import statements. Simplified regex-based stub here; the full
        tree-sitter implementation is provided in the companion module
        `ast_extractor.py` (omitted here for brevity).
        """
        import re
        deps = []
        if ecosystem == "python":
            for match in re.finditer(r"^\s*(?:import|from)\s+([\w\.]+)", code, re.MULTILINE):
                module = match.group(1).split(".")[0]
                canonical = self.registry.resolve_canonical_name(
                    module, ecosystem, self.module_dictionary
                )
                deps.append(Dependency(canonical, ecosystem=ecosystem))
        return deps

    def generate_initial_code(self, prompt: str, generator_model: str) -> str:
        client = self.llm_client_factory(generator_model)
        return client.complete(prompt)

    def verify_and_mitigate(self, prompt: str, max_iterations: int = 3,
                             generator_model: str = "gpt-4-turbo-2024-04-09",
                             judge_model: str = "claude-3-5-sonnet-20240620"
                             ) -> VerificationOutcome:
        code = self.generate_initial_code(prompt, generator_model)
        rejection_log = []

        for iteration in range(1, max_iterations + 1):
            deps = self.extract_dependencies(code)
            all_verified = True

            for dep in deps:
                # --- V_exist ---
                exist_result = self.registry.verify_existence(dep)
                if not exist_result.exists:
                    rejection_log.append((iteration, dep.package_name, "not_exist"))
                    req = MitigationRequest(prompt, code, dep.package_name, "not_exist")
                    code = self.mitigation.regenerate(req, generator_model)
                    all_verified = False
                    break

                # --- V_secure ---
                sec_result = calculate_security_score(
                    dep.package_name, dep.version_specifier, self.popular_packages
                )
                if not sec_result.passed:
                    rejection_log.append((iteration, dep.package_name, "insecure"))
                    req = MitigationRequest(prompt, code, dep.package_name, "insecure")
                    code = self.mitigation.regenerate(req, generator_model)
                    all_verified = False
                    break

                # --- V_relevant ---
                rel_result = self.judge.verify_relevance(
                    dep.package_name, prompt, generator_model, judge_model
                )
                if not rel_result.verdict:
                    rejection_log.append((iteration, dep.package_name, "not_relevant"))
                    req = MitigationRequest(prompt, code, dep.package_name, "not_relevant")
                    code = self.mitigation.regenerate(req, generator_model)
                    all_verified = False
                    break

            if all_verified:
                return VerificationOutcome(
                    final_code=code, success=True,
                    iterations_used=iteration, rejection_log=rejection_log,
                )

        return VerificationOutcome(
            final_code=None, success=False,
            iterations_used=max_iterations, rejection_log=rejection_log,
        )


if __name__ == "__main__":
    class DummyClient:
        def complete(self, prompt: str) -> str:
            return "import requests\nresponse = requests.get('https://example.com')"

    verifier = HalluGuardVerifier(
        llm_client_factory=lambda model: DummyClient(),
        popular_packages=["requests", "numpy", "pandas"],
        module_dictionary={},
        config={},
    )
    outcome = verifier.verify_and_mitigate(
        "Write Python code to fetch and parse data from a URL."
    )
    print(outcome)
