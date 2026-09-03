"""Typed configuration loaded from ``config.yaml`` plus environment variables.

API credentials are never stored in the YAML file; they are read from the
environment at load time (see ``.env.example``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


@dataclass(frozen=True)
class SecurityWeights:
    vuln: float
    rep: float
    typo: float

    def __post_init__(self) -> None:
        for name, value in (("vuln", self.vuln), ("rep", self.rep), ("typo", self.typo)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"weight '{name}' must be in [0, 1], got {value}")


@dataclass(frozen=True)
class Settings:
    generator_model: str
    judge_model: str
    generation_temperature: float
    max_tokens: int
    max_regeneration_attempts: int
    tau_secure: float
    weights: SecurityWeights
    osv_snapshot_date: str
    typosquat_list_size: int
    http_timeout_s: float
    pypi_url: str
    osv_url: str
    libraries_io_url: str
    seeds: tuple[int, ...]
    openai_api_key: str | None = field(default=None, repr=False)
    anthropic_api_key: str | None = field(default=None, repr=False)
    libraries_io_api_key: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.generator_model == self.judge_model:
            raise ValueError("judge_model must differ from generator_model")
        if not 0.0 <= self.tau_secure <= 1.0:
            raise ValueError("tau_secure must be in [0, 1]")
        if self.max_regeneration_attempts < 1:
            raise ValueError("max_regeneration_attempts must be >= 1")


def load_settings(path: Path | str = DEFAULT_CONFIG_PATH) -> Settings:
    """Load and validate settings; credentials come from the environment."""
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    llm, sec, rep = raw["llm"], raw["security"], raw["reproducibility"]
    return Settings(
        generator_model=llm["generator_model"],
        judge_model=llm["judge_model"],
        generation_temperature=float(llm["generation_temperature"]),
        max_tokens=int(llm["max_tokens"]),
        max_regeneration_attempts=int(llm["max_regeneration_attempts"]),
        tau_secure=float(sec["tau_secure"]),
        weights=SecurityWeights(**sec["weights"]),
        osv_snapshot_date=str(sec["osv_snapshot_date"]),
        typosquat_list_size=int(sec["typosquat_list_size"]),
        http_timeout_s=float(raw["network"]["http_timeout_s"]),
        pypi_url=str(raw["network"]["pypi_url"]),
        osv_url=str(raw["network"]["osv_url"]),
        libraries_io_url=str(raw["network"]["libraries_io_url"]),
        seeds=tuple(int(s) for s in rep["seeds"]),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        libraries_io_api_key=os.environ.get("LIBRARIES_IO_API_KEY"),
    )
