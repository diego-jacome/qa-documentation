# CMIS API — Performance Test PROD Baseline
**Date:** April 14, 2026 | **Environment:** PROD — Tenant: ProductionTest (Archwell) | **Tool:** k6 v1.7.1

## Configuration

| Parameter | Value |
|-----------|-------|
| Concurrent Users (VUs) | 5 |
| Iterations per User | 100 |
| Total Iterations | 500 |
| Document Size | 3 MB |
| Total Duration | 5 min 14 sec |
| Document Type (CMIS objectTypeId) | dd:Agreement |
| CMIS Repository ID | 2 |
| Teardown | FAILED (CMIS children returns 500 for PROD folder-2315) |

## Results by Endpoint

| Endpoint | Action | avg | median | p(90) | p(95) | max | Result |
|----------|--------|-----|--------|-------|-------|-----|--------|
| `createDocument` | Document Uploaded | 2.12s | 2.00s | 2.32s | 2.48s | 9.74s | ✅ PASS |
| `getContentStream` | Document Downloaded | 638ms | 558ms | 893ms | 1.13s | 6.29s | ✅ PASS |
| `getObject` | Document Viewed | 297ms | 256ms | 384ms | 402ms | 1.99s | ✅ PASS |

## PROD vs QA vs STG Comparison (avg)

| Endpoint | PROD Baseline | STG Baseline | QA Run 2 | Δ vs STG | Δ vs QA |
|----------|--------------|--------------|----------|----------|---------|
| `createDocument` | **2.12s** | 2.17s | 2.85s | ≈ -2% (similar) | ≈ -26% faster |
| `getContentStream` | **638ms** | 1.50s | 1.02s | ≈ -57% faster | ≈ -37% faster |
| `getObject` | **297ms** | 865ms | 475ms | ≈ -66% faster | ≈ -37% faster |

> PROD read operations are significantly faster than QA and STG — consistent with PROD having better infrastructure provisioning. Upload is comparable to STG.

## Reliability

| Metric | Value |
|--------|-------|
| Total Requests | 1,500 |
| Successful Requests | 1,500 (100%) |
| Error Rate | 0.00% |
| Throughput | ≈ 4.78 req/s |
| All Thresholds | PASSED |

## Verdict

PROD baseline completed with **0 errors across 500 iterations** (1,500 requests). All three CMIS endpoints performed within acceptable thresholds. PROD demonstrates the best read performance of all three environments. **Baseline established for future PROD regression comparisons.**

## Notes

- k6 teardown failed: CMIS `children` endpoint returns HTTP 500 for PROD `folder-2315`. ~500 k6perf documents were left in PROD after the run and will be cleaned up via DD API (`scripts/k6/cleanup_prod_k6perf.py`).

## Raw Data

- [prod-baseline-summary.json](raw-data/prod-baseline-summary.json)
- [prod-baseline-summary.txt](raw-data/prod-baseline-summary.txt)
- [prod-baseline-requests.ndjson](raw-data/prod-baseline-requests.ndjson) — per-request raw data

## ADO Reference

- Work Item: [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375)
- Comment ID: 16447321
