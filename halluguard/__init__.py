"""HalluGuard: registry-aware Chain-of-Verification for Python dependencies."""

from halluguard.config import Settings, load_settings
from halluguard.verifier import HalluGuardVerifier, VerificationOutcome

__all__ = ["HalluGuardVerifier", "Settings", "VerificationOutcome", "load_settings"]
__version__ = "1.0.0"
