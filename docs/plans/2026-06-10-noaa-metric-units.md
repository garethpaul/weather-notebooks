# NOAA Metric Units

Status: Completed

## Context

NOAA CDO v2 does not scale or convert data values when the `units` parameter is
omitted. The notebook treated raw GHCND precipitation as millimeters and used
an incorrect inches divisor, which could materially overstate rainfall.

Official API reference:
https://www.ncei.noaa.gov/cdo-web/webservices/v2

## Changes

- Request `metric` units on every paginated NOAA data call.
- Convert scaled Celsius values directly to Fahrenheit.
- Convert scaled millimeter precipitation to inches using `25.4`.
- Add offline contracts for the request unit and each conversion assumption.

## Verification

- `make check`
- Remove the metric request parameter and confirm the contract checker fails
  before restoring it.
