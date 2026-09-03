# Security policy

## Scope of this repository

HalluGuard is defensive research tooling: it validates third-party Python dependencies in
LLM-generated code *before* installation. It contains no exploit code and no attack payloads.

Malicious package identifiers in `data/adversarial_benchmark/adversarial_benchmark_500.csv` are
deliberately pseudonymised (`cve-pkg-###`, `typo-pkg-###`, `slop-pkg-###`) so that publishing
this benchmark does not propagate live attack names or supply a ready-made target list. The
pseudonym-to-name mapping is held by the authors and shared on reasonable request for
verification purposes. Please do not open issues or pull requests that de-anonymise them.

## Reporting a vulnerability

Report security issues in this code by email to the corresponding authors
(saurabh@yu.ac.kr, wooguilpak@yu.ac.kr) rather than in a public issue.

## Operational cautions for anyone running this framework

* **`V_secure` reflects OSV as of the moment you run it**, not the 2025-03-01 snapshot used in
  the study, and the shipped typosquat reference list has 159 names rather than the study's
  top-5,000. Both make a live run *more permissive* than the evaluated configuration. See
  `docs/DEVIATIONS.md`.
* **An unreachable data source yields `INDETERMINATE`, never a pass.** If you adapt this code,
  preserve that: mapping a network failure to "safe" turns the guard into a no-op exactly when
  an attacker would most like it to be one.
* **Verification is package-level only.** A verified package can still expose a hallucinated
  function or class; the framework does not check API surfaces.
* **Do not treat a `VERIFIED` outcome as a licence to install unreviewed code.** Reported
  detection rates come from a study whose per-instance records were not retained
  (`data/PROVENANCE.md`); they are not a warranty.
