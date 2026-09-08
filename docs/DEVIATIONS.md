# Implementation notes

Practical notes for running the released reference implementation, and where its configuration
differs from the environment described in the manuscript.

## Dependency extraction

Extraction uses the Python standard-library `ast` module (`halluguard/extractor.py`). The parser
walks `Import` and `ImportFrom` nodes, handles aliased imports, multi-line import blocks and
conditional imports, and excludes standard-library roots and relative imports. Extending
extraction to further languages would call for a multi-language front end such as `tree-sitter`;
that is future work rather than part of the Python and PyPI scope evaluated here.

## Advisory data

`SecurityScorer.query_severity()` queries the OSV API at `https://api.osv.dev/v1/query`. The
study used a snapshot dated 2025-03-01, recorded in `config.yaml` as `osv_snapshot_date`; that
snapshot is not redistributed. Security sub-scores from a live run therefore reflect the current
state of OSV, and advisories published since the snapshot date will be picked up.

## Reference lists

`module_to_package.json` ships 17 mappings and `popular_pypi_reference.json` ships 159 reference
names. Both are reduced working sets. `S_typo` is a maximum over the reference list, so a live
run against the shorter list produces lower similarity scores and a correspondingly higher
`S_final` than the evaluated configuration.

## Configuration keys

`config.yaml` records `typosquat_list_size`, `osv_snapshot_date` and `seeds` as machine-readable
documentation of the study configuration. No code reads them: `SecurityScorer` receives its
reference list as a constructor argument, and `grid_search.py` takes its own `--seed` with a
default of 42.

## Figure regeneration

`figures/plot_results.py` regenerates the four data-driven figures and
`figures/plot_diagrams.py` the three schematic figures that carry study numbers. Both write to
`results/generated/figures/`, `figures/`, and the manuscript's `figures/` directory. The
remaining figures, the architecture diagram and the four stage-flow diagrams, are authored by
hand.

## Metric names

An earlier public release used `HR` and `MSR`. The current names are `PHR` (Package Hallucination
Rate, existence-based), `UDR` (Unsafe Dependency Rate, any stage) and `ARR` (Automated Repair
Rate). The old `rejected_vexist_pct` column corresponds to PHR. See
`docs/CHANGELOG-replication.md`.

## Environment

Dependencies are pinned (`numpy==1.26.4`, `scipy==1.13.1`), which resolves on Python 3.10 to
3.12. The study environment was Python 3.11.9 on Ubuntu 22.04 LTS. Credentials are read from the
environment only; no analysis script that reproduces a reported number requires credentials or
network access.
