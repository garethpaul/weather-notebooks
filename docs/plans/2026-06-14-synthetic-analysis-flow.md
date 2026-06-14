# Synthetic Weather Analysis Flow

## Status: Planned

## Context

The NOAA request, pagination, validation, and scalar conversion helpers have
unit coverage, while dataframe row construction and plotting remain inline in
the notebook. The complete analysis path is therefore not exercised without a
live token.

## Requirements

- Extract deterministic date-aligned row construction into the existing
  `weather_notebook.py` module.
- Preserve sorted dates, display-unit conversions, missing-measurement skips,
  and the explicit empty-analysis error.
- Keep the notebook as the composition surface and call the shared helper.
- Add an offline synthetic integration test that exercises fake NOAA responses,
  observation bucketing, row construction, pandas dataframe columns, and a
  headless average-temperature line plot.
- Require the notebook to remain output-free and token-free.
- Add mutation-sensitive contracts for helper use, integration-test scope,
  roadmap status, suite registration, and completed plan evidence.

## Verification Plan

- focused row-construction and synthetic analysis-flow tests
- repository and external-directory `make check`
- hostile helper, ordering, conversion, empty-result, dataframe, plot, offline,
  roadmap, suite, notebook, and plan-status mutations
- pinned Python 3.12 package integrity, notebook JSON/output, artifact,
  credential, exact-diff, and hosted verification audits

## Scope Boundary

- Do not change NOAA origins, token handling, pagination, request bounds,
  station/date defaults, dependency versions, locks, workflows, or saved output.
- Do not make live NOAA requests or commit tokens, refreshed datasets, images,
  execution counts, or notebook outputs.
- Do not merge or close stacked pull requests without owner authorization.
