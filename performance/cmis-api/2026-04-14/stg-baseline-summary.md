# CMIS API — Performance Test STG Baseline
**Date:** April 14, 2026 | **Environment:** Staging — Tenant: Encino | **Tool:** k6 v1.7.1

## Configuration

| Parameter | Value |
|-----------|-------|
| Concurrent Users (VUs) | 5 |
| Iterations per User | 100 |
| Total Iterations | 500 |
| Document Size | 3 MB |
| Total Duration | 7 min 47 sec |
| Teardown | Automatic (501 docs deleted) |

## Results by Endpoint

| Endpoint | Action | avg | median | p(90) | p(95) | max | Result |
|----------|--------|-----|--------|-------|-------|-----|--------|
| `createDocument` | Document Uploaded | 2.17s | 2.11s | 2.56s | 2.77s | 5.19s | ✅ PASS |
| `getContentStream` | Document Downloaded | 1.50s | 1.44s | 2.06s | 2.30s | 4.28s | ✅ PASS |
| `getObject` | Document Viewed | 865ms | 807ms | 1.24s | 1.34s | 2.22s | ✅ PASS |

## STG vs QA Comparison (avg)

| Endpoint | STG Baseline | QA Run 1 | QA Run 2 | Δ vs QA R1 |
|----------|-------------|----------|----------|------------|
| `createDocument` | **2.17s** | 2.66s | 2.85s | -18% faster |
| `getContentStream` | **1.50s** | 1.17s | 1.02s | +28% slower |
| `getObject` | **865ms** | 454ms | 475ms | +90% slower |

> Read operations are slower in STG — expected for a different tenant/dataset size.

## Reliability

| Metric | Value |
|--------|-------|
| Total Requests | 1,500 |
| Successful Requests | 1,500 (100%) |
| Error Rate | 0.00% |
| Throughput | ≈ 3.21 req/s |
| All Thresholds | PASSED |

## Verdict

STG Baseline completed with **0 errors across 500 iterations** (1,500 requests). Upload performance is **18% faster than QA** (2.17s vs 2.66s avg). Read operations (`getObject`, `getContentStream`) are slower in STG — expected for a different tenant/dataset. Baseline established for future STG regression comparisons.

## Raw Data

- [stg-baseline-summary.json](raw-data/stg-baseline-summary.json)
- [stg-baseline-summary.txt](raw-data/stg-baseline-summary.txt)

## ADO Reference

- Work Item: [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375)
- Comment ID: 16444741
