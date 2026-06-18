"""
relevance_judge.py
-------------------
Implements V_relevant: contextual relevance verification using a
cross-model LLM judge (Section 3.4.3 and Section 3.4.4 — Cross-Model
Verification Protocol).

CRITICAL DESIGN CONSTRAINT: the judge model MUST differ from the
code-generator model to prevent the intra-model bias quantified in
Table 11 of the manuscript (+3.2 pp F1 inflation under same-model
verification, p < 0.01).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("halluguard.relevance_judge")

PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "verbatim_relevance_prompt.txt"


@dataclass
class RelevanceResult:
    package_name: str
    prompt: str
    judge_model: str
    generator_model: str
    verdict: bool          # True = relevant (pass), False = irrelevant (fail)
    raw_response: str


class CrossModelJudge:
    """
    Wraps the V_relevant check. Selects a judge model that is
    architecturally distinct from the generator model, per
    Section 3.4.4 (Cross-Model Verification Protocol).
    """

    DEFAULT_JUDGE_FALLBACK = {
        "gpt-4-turbo-2024-04-09": "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229": "gpt-4-turbo-2024-04-09",
        "mistral-large-latest": "llama-3-70b-instruct",
    }

    def __init__(self, llm_client_factory):
        """
        llm_client_factory: callable(model_name) -> object with
        a `.complete(prompt: str) -> str` method. Injected to keep
        this module provider-agnostic (OpenAI / Anthropic / local).
        """
        self.llm_client_factory = llm_client_factory
        self.prompt_template = PROMPT_TEMPLATE_PATH.read_text()

    def select_judge_model(self, generator_model: str, configured_judge: str) -> str:
        """
        Enforces generator != judge. If a misconfiguration sets them
        equal, falls back to the documented cross-model pairing table.
        """
        if configured_judge != generator_model:
            return configured_judge
        logger.warning(
            "Judge model equals generator model (%s); switching to "
            "cross-model fallback to prevent intra-model bias.", generator_model
        )
        return self.DEFAULT_JUDGE_FALLBACK.get(generator_model, "claude-3-5-sonnet-20240620")

    def verify_relevance(self, package_name: str, original_prompt: str,
                          generator_model: str, configured_judge: str) -> RelevanceResult:
        judge_model = self.select_judge_model(generator_model, configured_judge)
        client = self.llm_client_factory(judge_model)

        query = self.prompt_template.format(
            package_name=package_name,
            original_prompt=original_prompt,
        )
        raw_response = client.complete(query).strip().lower()
        verdict = raw_response.startswith("yes")

        return RelevanceResult(
            package_name=package_name,
            prompt=original_prompt,
            judge_model=judge_model,
            generator_model=generator_model,
            verdict=verdict,
            raw_response=raw_response,
        )


if __name__ == "__main__":
    class DummyClient:
        def complete(self, prompt: str) -> str:
            return "Yes"

    judge = CrossModelJudge(llm_client_factory=lambda model: DummyClient())
    result = judge.verify_relevance(
        package_name="requests",
        original_prompt="Write Python code to fetch and parse data from a URL.",
        generator_model="gpt-4-turbo-2024-04-09",
        configured_judge="claude-3-5-sonnet-20240620",
    )
    print(result)
