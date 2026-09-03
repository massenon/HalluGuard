"""LLM completion interface with a minimal OpenAI/Anthropic adapter.

Providers are optional dependencies; import errors surface only when a
provider is actually instantiated.
"""

from __future__ import annotations

from typing import Protocol


class Completer(Protocol):
    def complete(self, system: str, user: str, temperature: float, max_tokens: int) -> str: ...


def make_completer(model: str, openai_api_key: str | None, anthropic_api_key: str | None) -> Completer:
    if model.startswith("claude"):
        if not anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic  # optional dependency

        client = Anthropic(api_key=anthropic_api_key)

        class _Anthropic:
            def complete(self, system: str, user: str, temperature: float, max_tokens: int) -> str:
                msg = client.messages.create(model=model, system=system, temperature=temperature,
                                             max_tokens=max_tokens,
                                             messages=[{"role": "user", "content": user}])
                return "".join(block.text for block in msg.content if hasattr(block, "text"))

        return _Anthropic()

    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    from openai import OpenAI  # optional dependency

    client = OpenAI(api_key=openai_api_key)

    class _OpenAI:
        def complete(self, system: str, user: str, temperature: float, max_tokens: int) -> str:
            resp = client.chat.completions.create(
                model=model, temperature=temperature, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return resp.choices[0].message.content or ""

    return _OpenAI()
