import pytest

from halluguard.config import SecurityWeights, load_settings


def test_default_config_loads_and_validates():
    s = load_settings()
    assert s.generator_model != s.judge_model
    assert s.tau_secure == 0.70
    assert (s.weights.vuln, s.weights.rep, s.weights.typo) == (0.6, 0.2, 0.2)
    assert s.seeds == (42, 137, 2024)


def test_invalid_weight_rejected():
    with pytest.raises(ValueError):
        SecurityWeights(1.5, 0.2, 0.2)
