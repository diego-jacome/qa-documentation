---
name: Regression Checklist
about: Template for regression testing each release
title: "Regression Checklist — v[VERSION]"
labels: regression, qa
assignees: ""
---

## Metadata

| Field | Value |
|-------|-------|
| **Version** | <!-- e.g. 26.04 --> |
| **QA / Staging deploy** | <!-- YYYY-MM-DD --> |
| **Production deploy** | <!-- YYYY-MM-DD --> |
| **Testers** | <!-- @user1 · @user2 · @user3 --> |

---

## Legend

| Symbol | Status |
|:------:|--------|
| ✅ | Pass |
| ❌ Fail | Fail — add comment with details |
| ⚠️ | Blocked |
| ⏭️ | Skipped / N/A |

> Mark each item as done clicking the checkbox. Add a comment below for fails/blocks.

---

## � QA

<details>
<summary><b>1. Login</b></summary>

- [ ] 🟢 Login credentials
- [ ] 🟢 Login SSO
- [ ] 🟢 Login Okta

</details>

<details>
<summary><b>2. System Admin</b></summary>

- [ ] 🟢 Import via S3 big import: cancel before start
- [ ] 🟢 Import via S3 big import: cancel
- [ ] 🟢 Import via S3
- [ ] 🟢 New Email Ingestion
- [ ] 🟢 New Email Ingestion (Email Notification)
- [ ] 🟢 Email Ingestion auto-rename (new or old)
- [ ] 🟢 Email Ingestion unexisting rule (new or old)
- [ ] 🟢 Export system admin: to SFTP
- [ ] 🟢 Export system admin: to DropBox

</details>

<details>
<summary><b>3. Client Admin</b></summary>

- [ ] 🟢 Notifications
- [ ] 🟢 Profile
- [ ] 🟢 Home page
- [ ] 🟢 Document Location Setup page
- [ ] 🟢 Roles page
- [ ] 🟢 Permissions page
- [ ] 🟢 Policy page
- [ ] 🟢 Client Settings page
- [ ] 🟢 Document Type Setup page
- [ ] 🟢 Attributes page
- [ ] 🟢 Export (SFTP, Dropbox)
- [ ] 🟢 Document Insights (invoices — QUTI tenant)
- [ ] 🟢 Bulk Assign permissions for Projects
- [ ] 🟢 Restore soft-deleted document
- [ ] 🟢 Restore soft-deleted document to Inactive Location
- [ ] 🟢 .LAS visualizer (visualize a document)
- [ ] 🟢 Create a new User

</details>

<details>
<summary><b>4. Document Management</b></summary>

- [ ] 🟢 Keyword search
- [ ] 🟢 Other searches
- [ ] 🟢 Saved Search
- [ ] 🟢 Search using system attributes
- [ ] 🟢 Tree View (Upload / Move)
- [ ] 🟢 Actions on Search Criteria panel (Search, Subscribe, Manage)
- [ ] 🟢 Upload document
- [ ] 🟢 Upload document to subscribed folder (check email notification)
- [ ] 🟢 Document menu
- [ ] 🟢 Document Menu: Redact
- [ ] 🟢 Multiple documents — Document menu
- [ ] 🟢 Project menu
- [ ] 🟢 Multiple projects — Project menu
- [ ] 🟢 Edit document
- [ ] 🟢 Actions on Properties panel
- [ ] 🟢 Bulk Create projects (with autopopulation)
- [ ] 🟢 Bulk Create projects with sys_Location Attribute
- [ ] 🟢 Bulk Create projects with sys_DocumentAttribute
- [ ] 🟢 Auto-populate project: saved search + Encino rule
- [ ] 🟢 APWF is working with Veryfi Turned ON
- [ ] 🟢 APWF is working with Veryfi Turned OFF

</details>

<details>
<summary><b>5. End User</b></summary>

- [ ] 🟢 Home page: transition to Document
- [ ] 🟢 Home page: transition to Project
- [ ] 🟢 Edit under Role with limited permissions (Merit custom search)
- [ ] 🟢 Upload under Role with limited permissions (Merit custom search)

</details>

<details>
<summary><b>6. On Demand Importer</b></summary>

- [ ] 🟢 Update Document Attributes
- [ ] 🟢 Add Locations
- [ ] 🟢 Add Primary Location Attributes
- [ ] 🟢 Add Secondary Location Attributes
- [ ] 🟢 Add Tertiary Location Attributes
- [ ] 🟢 Add Users
- [ ] 🟢 Create or update document types
- [ ] 🟢 Link or Unlink Locations
- [ ] 🟢 Save Staged Documents
- [ ] 🟢 Update Hierarchy
- [ ] 🟢 Update Location Names

</details>

<details>
<summary><b>7. New Features</b></summary>

- [ ] 🟢 DD-8991 — [Export][CredMgmt][FE] UI to manage user Credentials
- [ ] 🟢 DD-8979 — [Export][CredMgmt] Design/Create services in API
- [ ] 🟢 DD-8978 — [Export][CredMgmt] Create data persistence objects in DD Database
- [ ] 🟢 DD-8973 — Implementing Auto-Response for Non-Existent Email Ingestion Addresses
- [ ] 🟢 DD-8961 — QAI Support — Add Link to QAI Support to Footer
- [ ] 🟢 DD-8956 — Background Excel Export for Search Results (>10K rows)
- [ ] 🟢 DD-8955 — Search API: Add streaming export endpoint for bulk Excel export (500K+ docs)
- [ ] 🟢 DD-8954 — Search API: Fix deep pagination to support search results beyond 10K
- [ ] 🟢 DD-8920 — [BE] OCR Confidence Search tech setup
- [ ] 🟢 DD-7895 — [FE] OCR Confidence — Search Criteria and Results in UI

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] 🟢 DD-8965 — Import jobs remain stuck in "In Progress" in test environment
- [ ] 🟢 DD-8964 — Search Results page goes blank after editing document attributes
- [ ] 🟢 DD-8963 — Success notification shows error after deleting projects
- [ ] 🟢 DD-8958 — Email Ingestion Errors for Large Number of Attachments — No Error Message

</details>

---

## 🟡 Staging

<details>
<summary><b>1. Login</b></summary>

- [ ] Login credentials
- [ ] Login SSO
- [ ] Login Okta

</details>

<details>
<summary><b>2. System Admin</b></summary>

- [ ] Import via S3 big import: cancel before start
- [ ] Import via S3 big import: cancel
- [ ] Import via S3
- [ ] New Email Ingestion
- [ ] New Email Ingestion (Email Notification)
- [ ] Email Ingestion auto-rename (new or old)
- [ ] Email Ingestion unexisting rule (new or old)
- [ ] Export system admin: to SFTP
- [ ] Export system admin: to DropBox

</details>

<details>
<summary><b>3. Client Admin</b></summary>

- [ ] Notifications
- [ ] Profile
- [ ] Home page
- [ ] Document Location Setup page
- [ ] Roles page
- [ ] Permissions page
- [ ] Policy page
- [ ] Client Settings page
- [ ] Document Type Setup page
- [ ] Attributes page
- [ ] Export (SFTP, Dropbox)
- [ ] Document Insights (invoices — QUTI tenant)
- [ ] Bulk Assign permissions for Projects
- [ ] Restore soft-deleted document
- [ ] Restore soft-deleted document to Inactive Location
- [ ] .LAS visualizer (visualize a document)
- [ ] Create a new User

</details>

<details>
<summary><b>4. Document Management</b></summary>

- [ ] Keyword search
- [ ] Other searches
- [ ] Saved Search
- [ ] Search using system attributes
- [ ] Tree View (Upload / Move)
- [ ] Actions on Search Criteria panel (Search, Subscribe, Manage)
- [ ] Upload document
- [ ] Upload document to subscribed folder (check email notification)
- [ ] Document menu
- [ ] Document Menu: Redact
- [ ] Multiple documents — Document menu
- [ ] Project menu
- [ ] Multiple projects — Project menu
- [ ] Edit document
- [ ] Actions on Properties panel
- [ ] Bulk Create projects (with autopopulation)
- [ ] Bulk Create projects with sys_Location Attribute
- [ ] Bulk Create projects with sys_DocumentAttribute
- [ ] Auto-populate project: saved search + Encino rule
- [ ] APWF is working with Veryfi Turned ON
- [ ] APWF is working with Veryfi Turned OFF

</details>

<details>
<summary><b>5. End User</b></summary>

- [ ] Home page: transition to Document
- [ ] Home page: transition to Project
- [ ] Edit under Role with limited permissions (Merit custom search)
- [ ] Upload under Role with limited permissions (Merit custom search)

</details>

<details>
<summary><b>6. On Demand Importer</b></summary>

- [ ] Update Document Attributes
- [ ] Add Locations
- [ ] Add Primary Location Attributes
- [ ] Add Secondary Location Attributes
- [ ] Add Tertiary Location Attributes
- [ ] Add Users
- [ ] Create or update document types
- [ ] Link or Unlink Locations
- [ ] Save Staged Documents
- [ ] Update Hierarchy
- [ ] Update Location Names

</details>

<details>
<summary><b>7. New Features</b></summary>

- [ ] DD-8991 — [Export][CredMgmt][FE] UI to manage user Credentials
- [ ] DD-8979 — [Export][CredMgmt] Design/Create services in API
- [ ] DD-8978 — [Export][CredMgmt] Create data persistence objects in DD Database
- [ ] DD-8973 — Implementing Auto-Response for Non-Existent Email Ingestion Addresses
- [ ] DD-8961 — QAI Support — Add Link to QAI Support to Footer
- [ ] DD-8956 — Background Excel Export for Search Results (>10K rows)
- [ ] DD-8955 — Search API: Add streaming export endpoint for bulk Excel export (500K+ docs)
- [ ] DD-8954 — Search API: Fix deep pagination to support search results beyond 10K
- [ ] DD-8920 — [BE] OCR Confidence Search tech setup
- [ ] DD-7895 — [FE] OCR Confidence — Search Criteria and Results in UI

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] DD-8965 — Import jobs remain stuck in "In Progress" in test environment
- [ ] DD-8964 — Search Results page goes blank after editing document attributes
- [ ] DD-8963 — Success notification shows error after deleting projects
- [ ] DD-8958 — Email Ingestion Errors for Large Number of Attachments — No Error Message

</details>

---

## 🟢 Production

<details>
<summary><b>1. Login</b></summary>

- [ ] Login credentials
- [ ] Login SSO
- [ ] Login Okta

</details>

<details>
<summary><b>2. System Admin</b></summary>

- [ ] Import via S3 big import: cancel before start
- [ ] Import via S3 big import: cancel
- [ ] Import via S3
- [ ] New Email Ingestion
- [ ] New Email Ingestion (Email Notification)
- [ ] Email Ingestion auto-rename (new or old)
- [ ] Email Ingestion unexisting rule (new or old)
- [ ] Export system admin: to SFTP
- [ ] Export system admin: to DropBox

</details>

<details>
<summary><b>3. Client Admin</b></summary>

- [ ] Notifications
- [ ] Profile
- [ ] Home page
- [ ] Document Location Setup page
- [ ] Roles page
- [ ] Permissions page
- [ ] Policy page
- [ ] Client Settings page
- [ ] Document Type Setup page
- [ ] Attributes page
- [ ] Export (SFTP, Dropbox)
- [ ] Document Insights (invoices — QUTI tenant)
- [ ] Bulk Assign permissions for Projects
- [ ] Restore soft-deleted document
- [ ] Restore soft-deleted document to Inactive Location
- [ ] .LAS visualizer (visualize a document)
- [ ] Create a new User

</details>

<details>
<summary><b>4. Document Management</b></summary>

- [ ] Keyword search
- [ ] Other searches
- [ ] Saved Search
- [ ] Search using system attributes
- [ ] Tree View (Upload / Move)
- [ ] Actions on Search Criteria panel (Search, Subscribe, Manage)
- [ ] Upload document
- [ ] Upload document to subscribed folder (check email notification)
- [ ] Document menu
- [ ] Document Menu: Redact
- [ ] Multiple documents — Document menu
- [ ] Project menu
- [ ] Multiple projects — Project menu
- [ ] Edit document
- [ ] Actions on Properties panel
- [ ] Bulk Create projects (with autopopulation)
- [ ] Bulk Create projects with sys_Location Attribute
- [ ] Bulk Create projects with sys_DocumentAttribute
- [ ] Auto-populate project: saved search + Encino rule
- [ ] APWF is working with Veryfi Turned ON
- [ ] APWF is working with Veryfi Turned OFF

</details>

<details>
<summary><b>5. End User</b></summary>

- [ ] Home page: transition to Document
- [ ] Home page: transition to Project
- [ ] Edit under Role with limited permissions (Merit custom search)
- [ ] Upload under Role with limited permissions (Merit custom search)

</details>

<details>
<summary><b>6. On Demand Importer</b></summary>

- [ ] Update Document Attributes
- [ ] Add Locations
- [ ] Add Primary Location Attributes
- [ ] Add Secondary Location Attributes
- [ ] Add Tertiary Location Attributes
- [ ] Add Users
- [ ] Create or update document types
- [ ] Link or Unlink Locations
- [ ] Save Staged Documents
- [ ] Update Hierarchy
- [ ] Update Location Names

</details>

<details>
<summary><b>7. New Features</b></summary>

- [ ] DD-8991 — [Export][CredMgmt][FE] UI to manage user Credentials
- [ ] DD-8979 — [Export][CredMgmt] Design/Create services in API
- [ ] DD-8978 — [Export][CredMgmt] Create data persistence objects in DD Database
- [ ] DD-8973 — Implementing Auto-Response for Non-Existent Email Ingestion Addresses
- [ ] DD-8961 — QAI Support — Add Link to QAI Support to Footer
- [ ] DD-8956 — Background Excel Export for Search Results (>10K rows)
- [ ] DD-8955 — Search API: Add streaming export endpoint for bulk Excel export (500K+ docs)
- [ ] DD-8954 — Search API: Fix deep pagination to support search results beyond 10K
- [ ] DD-8920 — [BE] OCR Confidence Search tech setup
- [ ] DD-7895 — [FE] OCR Confidence — Search Criteria and Results in UI

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] DD-8965 — Import jobs remain stuck in "In Progress" in test environment
- [ ] DD-8964 — Search Results page goes blank after editing document attributes
- [ ] DD-8963 — Success notification shows error after deleting projects
- [ ] DD-8958 — Email Ingestion Errors for Large Number of Attachments — No Error Message

</details>

---

## Notes / Fails / Blocks

<!-- Add a comment for each failed or blocked item with:
- Test case name
- Environment
- Steps to reproduce or reason blocked
-->
