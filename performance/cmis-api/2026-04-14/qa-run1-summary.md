# CMIS API — Performance Test Run 1
**Date:** April 14, 2026 | **Environment:** QA — Tenant: OnDemandQA1 | **Tool:** k6 v1.7.1

## Configuration

| Parameter | Value |
|-----------|-------|
| Concurrent Users (VUs) | 5 |
| Iterations per User | 100 |
| Total Iterations | 500 |
| Document Size | 3 MB |
| Total Duration | 7 min 26 sec |
| Data Sent | 2.1 GB |
| Data Received | 1.6 GB |

## Results by Endpoint

| Endpoint | Action | avg | median | p(90) | p(95) | max | Result |
|----------|--------|-----|--------|-------|-------|-----|--------|
| `createDocument` | Document Uploaded | 2.66s | 2.53s | 3.23s | 3.58s | 9.57s | ✅ PASS |
| `getContentStream` | Document Downloaded | 1.17s | 1.04s | 1.75s | 1.93s | 8.04s | ✅ PASS |
| `getObject` | Document Viewed | 454ms | 427ms | 591ms | 730ms | 1.46s | ✅ PASS |

## Reliability

| Metric | Value |
|--------|-------|
| Total Requests | 1,500 |
| Successful Requests | 1,500 (100%) |
| Error Rate | 0.00% |
| Throughput | ≈3.25 req/s |
| All Thresholds | PASSED |

## Notes

- Teardown deleted all uploaded `k6perf-*` documents automatically.
- No NDJSON captured (per-request file not enabled in this run).

## Raw Data

- [qa-run1-summary.json](raw-data/qa-run1-summary.json)
- [qa-run1-summary.txt](raw-data/qa-run1-summary.txt)

## ADO Reference

- Work Item: [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375)
- Comment ID: 16443095
