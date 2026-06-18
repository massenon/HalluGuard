"""
mitigation.py
--------------
Implements the Mitigation and Regeneration Module described in
Section 3.5. Constructs a structured correction prompt and triggers
a new generation cycle when any verification stage fails.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("halluguard.mitigation")

MITIGATION_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "verbatim_mitigation_prompt.txt"

REASON_CODES = {
    "not_exist": "does not exist on PyPI/npm",
    "insecure": "has known critical vulnerabilities (CVE: {cve_id})",
    "not_relevant": "is not relevant to the stated task",
}


@dataclass
class MitigationRequest:
    original_prompt: str
    flawed_code: str          # FULL snippet C_g — never truncated (Sec 3.5.1)
    package_name: str
    reason_code: str
    cve_id: str = ""


class MitigationModule:
    def __init__(self, llm_client_factory):
        self.llm_client_factory = llm_client_factory
        self.template = MITIGATION_TEMPLATE_PATH.read_text()

    def build_correction_prompt(self, request: MitigationRequest) -> str:
        reason_text = REASON_CODES[request.reason_code].format(cve_id=request.cve_id)
        return self.template.format(
            original_prompt=request.original_prompt,
            flawed_code=request.flawed_code,
            package_name=request.package_name,
            reason=reason_text,
        )

    def regenerate(self, request: MitigationRequest, generator_model: str) -> str:
        """
        Issues the correction prompt to the generator model and
        returns the new candidate snippet, which re-enters the
        Chain-of-Verification from the beginning (Algorithm 1).
        """
        prompt = self.build_correction_prompt(request)
        client = self.llm_client_factory(generator_model)
        new_snippet = client.complete(prompt)
        logger.info("Regenerated snippet after rejecting package '%s' (%s)",
                    request.package_name, request.reason_code)
        return new_snippet


if __name__ == "__main__":
    class DummyClient:
        def complete(self, prompt: str) -> str:
            return "import requests\nresponse = requests.get(url)"

    module = MitigationModule(llm_client_factory=lambda model: DummyClient())
    req = MitigationRequest(
        original_prompt="Write Python code to fetch and parse data from a URL.",
        flawed_code="import requests_plus\nresponse = requests_plus.get(url)",
        package_name="requests_plus",
        reason_code="not_exist",
    )
    print(module.regenerate(req, generator_model="gpt-4-turbo-2024-04-09"))
