# CMIS API — Performance Test Run 2
**Date:** April 14, 2026 | **Environment:** QA — Tenant: OnDemandQA1 | **Tool:** k6 v1.7.1

## Configuration

| Parameter | Value |
|-----------|-------|
| Concurrent Users (VUs) | 5 |
| Iterations per User | 100 |
| Total Iterations | 500 |
| Document Size | 3 MB |
| Total Duration | 7 min 23 sec |
| Data Sent | 2.1 GB |
| Data Received | 1.6 GB |

## Results by Endpoint

| Endpoint | Action | avg | median | p(90) | p(95) | max | vs Run 1 avg | Result |
|----------|--------|-----|--------|-------|-------|-----|-------------|--------|
| `createDocument` | Document Uploaded | 2.85s | 2.66s | 3.34s | 3.75s | 10.9s | +0.19s (+7%) | ✅ PASS |
| `getContentStream` | Document Downloaded | 1.02s | 932ms | 1.38s | 1.54s | 6.77s | -0.15s (-13%) | ✅ PASS |
| `getObject` | Document Viewed | 475ms | 434ms | 696ms | 819ms | 1.56s | +21ms (+5%) | ✅ PASS |

## Reliability

| Metric | Run 2 | Run 1 |
|--------|-------|-------|
| Total Requests | 1,500 | 1,500 |
| Successful Requests | 1,500 (100%) | 1,500 (100%) |
| Error Rate | 0.00% | 0.00% |
| Throughput | 3.39 req/s | ≈3.25 req/s |
| Total Duration | 7 min 23 sec | 7 min 26 sec |
| All Thresholds | PASSED | PASSED |

## Verdict

Results are consistent with Run 1. Variance across all endpoints stays within normal range (±13%). Zero errors in both runs confirm the API handles 5 concurrent users uploading 100 files of 3 MB with no degradation. **Performance is stable and reproducible.**

## Notes

- `-skipCleanup` flag used — 500 new documents left in QA folder-2307.
- Combined with 501 docs from Run 1, there are **1001 k6perf documents** pending deletion.
- Per-request NDJSON captured (7 MB, 1500 requests).

## Raw Data

- [qa-run2-summary.json](raw-data/qa-run2-summary.json)
- [qa-run2-summary.txt](raw-data/qa-run2-summary.txt)
- [qa-run2-requests.ndjson](raw-data/qa-run2-requests.ndjson) — per-request raw data (7 MB)
- [qa-run2-k6perf-ids.txt](raw-data/qa-run2-k6perf-ids.txt) — 1001 document IDs pending deletion in QA

## ADO Reference

- Work Item: [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375)
- Comment ID: 16443718
- Attachment: `cmis-requests-run2-2026-04-14.ndjson` (ID: 7b275f58-42cc-4ddd-adc6-c84ae8888bc3)
