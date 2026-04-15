# Performance Testing — Index

All performance test runs organized by functionality and date.

## How to navigate

```
performance/
  <functionality>/
    <YYYY-MM-DD>/
      run1-summary.md     ← human-readable report
      run2-summary.md     ← ...
      raw-data/           ← k6 JSON summaries, NDJSON per-request, IDs
```

---

## Run History

| Date | Functionality | Env | Scenario | VUs | Iterations | Errors | Result | ADO |
|------|--------------|-----|----------|-----|-----------|--------|--------|-----|
| 2026-04-14 | [CMIS API — QA Run 1](cmis-api/2026-04-14/qa-run1-summary.md) | QA | 3MB upload/view/download | 5 | 100×5=500 | 0% | ✅ PASS | [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375) |
| 2026-04-14 | [CMIS API — QA Run 2](cmis-api/2026-04-14/qa-run2-summary.md) | QA | 3MB upload/view/download | 5 | 100×5=500 | 0% | ✅ PASS | [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375) |
| 2026-04-14 | [CMIS API — STG Baseline](cmis-api/2026-04-14/stg-baseline-summary.md) | STG | 3MB upload/view/download | 5 | 100×5=500 | 0% | ✅ PASS | [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375) |
| 2026-04-14 | [CMIS API — PROD Baseline](cmis-api/2026-04-14/prod-baseline-summary.md) | PROD | 3MB upload/view/download | 5 | 100×5=500 | 0% | ✅ PASS | [1796375](https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1796375) |
