# New Import Service — Performance Testing

> **Jira Ticket:** [DD-8340](https://archeiojira.atlassian.net/browse/DD-8340)  
> **Epic:** [DD-2672](https://archeiojira.atlassian.net/browse/DD-2672) — Document Import & OCR Process Optimization (MVP) - Phase 1  
> **Status:** Done | **Priority:** Medium  
> **QA Engineer:** Diego Sanchez Medina  
> **Reported by:** Claire Smith  
> **Period:** July 2025 – October 2025

---

## Overview

This document captures the performance testing results for the **New Document Import Service**. The goal was to validate that the service can handle parallel imports at scale and operate continuously without degrading end-user performance.

### Objectives

- Support parallel imports (multiple customers importing simultaneously in a turn-key manner).
- Demonstrate the ability to run imports 24 hours a day without performance impact to end users.
- Measure the time to process **1,000 documents** through exploration + import.
- If the 1k test was successful, evaluate scalability up to **10,000 documents**.

---

## Acceptance Criteria

| # | Criteria | Result |
|---|----------|--------|
| 1 | Support parallel imports (multiple customers simultaneously) | ✅ Validated |
| 2 | Run imports 24 h/day without impacting end users | ✅ Validated |
| 3 | Measure time to process 1,000 docs through exploration + import | ✅ Done |
| 4 | Evaluate expansion to 10,000 documents | ✅ Done (4 attempts required) |

---

## Test Setup

| Parameter | Value |
|-----------|-------|
| Environment | QA — Archeio Tenant |
| New importer page | Document Import (New Document Import - Quorum Software) |
| Connection type | SFTP |
| Baseline tool | Merit QA (old importer via Job Management page) |
| Baseline source | AWS S3 Bucket |

---

## Baseline — Old Importer (S3 Bucket via Merit QA)

These results were used to establish a reference point before testing the new importer.

| Documents | Duration | Errors |
|-----------|----------|--------|
| ~1,119 | ~16 minutes | 2 |
| 10,000 | ~2 hours 25 minutes | 6 |

---

## Performance Results — New Importer (SFTP)

### 1,000 Documents

| Execution | Job Name | Exploration | Import Duration | Notes |
|-----------|----------|-------------|-----------------|-------|
| 1st | `DiegoImport_1k_SFTP_00` | ~31 s (1,120 files) | ~22 min (15:34:46 → 15:56:05) | ✅ Successful |
| 2nd | `DiegoImport_1k_SFTP_01` | ~43 s (1,120 files) | ~21 min (16:48 → 17:09) | ⚠️ Error displayed on start, import continued and completed |

**1k Summary:**  
Exploration consistently completed in under 1 minute. Import processed ~1,120 documents in approximately **21–22 minutes** via SFTP.

---

### 10,000 Documents

| Attempt | Job Name / Job ID | Exploration | Import Duration | Result |
|---------|-------------------|-------------|-----------------|--------|
| 1st | `DiegoImport_10k_SFTP_01` | ~25 s | — | ❌ Status stuck in "Exploring"; no logs recorded. |
| 2nd | `DiegoImport_10k_SFTP_02` | ~46 s (10,001 files) | — | ❌ Import failed due to a recent deployment. |
| 3rd | `DiegoImport_10k_SFTP_03` / `11ffa5b4-317f-4bc6-be4e-b8547c19b9d4` | ~35 s (10,001 files) | — | ❌ Error on import start; status showed "Unknown"; job stuck in "Exploring"; 400 Bad Request on log download. |
| 4th ✅ | `DiegoImport_10k_SFTP_03` / `694addec-78e5-4360-83bb-9f8cfa2d37c1` | ~35 s (10,001 files) | ~1 h 31 min (2025-10-09 23:12 → 2025-10-10 00:43) | ✅ Successful |

**10k Summary:**  
After 3 failed attempts (due to stuck statuses and a deployment-related failure), the 4th attempt processed **10,001 documents in approximately 1 hour and 31 minutes** via SFTP.

---

## Performance Comparison

| Scenario | Documents | Tool | Exploration | Import | Total |
|----------|-----------|------|-------------|--------|-------|
| Baseline | ~1,119 | Old Importer (S3) | N/A | ~16 min | ~16 min |
| Baseline | 10,000 | Old Importer (S3) | N/A | ~2 h 25 min | ~2 h 25 min |
| New Importer | ~1,120 | New Service (SFTP) | ~31–43 s | ~21–22 min | ~22–23 min |
| New Importer | 10,001 | New Service (SFTP) | ~35 s | ~1 h 31 min | ~1 h 32 min |

> **Key finding:** The new importer processed 10,000 documents approximately **54 minutes faster** than the old importer baseline using SFTP (~1h 31 min vs ~2h 25 min).

---

## QA Findings & Issues

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | Medium | Error message displayed when starting the 2nd 1k SFTP import; import continued and completed normally. | ⚠️ Needs investigation — UI error vs. actual behavior mismatch. |
| 2 | High | 10k import (Attempt 1): status stuck in "Exploring" indefinitely; no logs were recorded. Job had been running for 2+ days with no progress. | Resolved in subsequent attempts. |
| 3 | Medium | 10k import (Attempt 2): import failed immediately due to a recent deployment. | Expected — environment issue, not service defect. |
| 4 | Medium | Log files are not sorted by date/time, making debugging difficult. | Reported — to be addressed. |
| 5 | High | 10k import (Attempt 3): error after starting import; status reported as "Unknown"; job stuck in "Exploring"; log download returned **400 Bad Request**. | Resolved in Attempt 4. |

---

## Related Tickets

| Ticket | Summary | Relationship |
|--------|---------|--------------|
| [DD-8314](https://archeiojira.atlassian.net/browse/DD-8314) | [Import] QA \| End to End Testing | Relates to |
| [DD-8276](https://archeiojira.atlassian.net/browse/DD-8276) | [Import][FE] Integrate Error Pop-Ups into Unified Process | Blocked by DD-8340 |
| [DD-8338](https://archeiojira.atlassian.net/browse/DD-8338) | [Import][FE] Import Status Handler | Blocked by DD-8340 |
| [DD-8942](https://archeiojira.atlassian.net/browse/DD-8942) | Import Service Performance Scaling for SFTP | Relates to (Resolved) |
| [DD-8966](https://archeiojira.atlassian.net/browse/DD-8966) | Import Service Performance Scaling for AWS S3 | Relates to (In Development) |

---

## Attachments (from Jira)

The following files were captured during the successful 10k test run (`694addec-78e5-4360-83bb-9f8cfa2d37c1`):

- `import_report_694addec-78e5-4360-83bb-9f8cfa2d37c1.xlsx` — Summary report with all temporary content IDs.
- `Log-694addec-78e5-4360-83bb-9f8cfa2d37c1.log` — Full import log (~5.1 MB).

Screenshots captured during testing are available in Jira (DD-8340, 13 images uploaded between 2025-10-07 and 2025-10-10).
