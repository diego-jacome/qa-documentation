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

## 🔵 QA

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

- [ ] DD-8944 — Migrate DD Apps from HTTP Email Endpoint to Azure Service Bus
- [ ] DD-8779 — [Import][FE] Performance: Status doesn't update in large number of files
- [ ] DD-8743 — [Export][BE] Include metadata in email notifications
- [ ] DD-8957 — Adjust Confidence Restriction to allow re-processing of any document
- [ ] DD-8710 — [Import][FE] Ability to Retrieve Job Summary on Older Imports
- [ ] DD-8602 — [NewImport] Exploration Detail Log shows only counts for files in root path

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] DD-8941 — QEnergyUSA Regular Search Broken
- [ ] DD-8936 — Batch download for multiple emails error
- [ ] DD-8928 — Email Ingestion Error — 522: Connection timed out

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

- [ ] DD-8944 — Migrate DD Apps from HTTP Email Endpoint to Azure Service Bus
- [ ] DD-8779 — [Import][FE] Performance: Status doesn't update in large number of files
- [ ] DD-8743 — [Export][BE] Include metadata in email notifications
- [ ] DD-8957 — Adjust Confidence Restriction to allow re-processing of any document
- [ ] DD-8710 — [Import][FE] Ability to Retrieve Job Summary on Older Imports
- [ ] DD-8602 — [NewImport] Exploration Detail Log shows only counts for files in root path

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] DD-8941 — QEnergyUSA Regular Search Broken
- [ ] DD-8936 — Batch download for multiple emails error
- [ ] DD-8928 — Email Ingestion Error — 522: Connection timed out

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

- [ ] DD-8944 — Migrate DD Apps from HTTP Email Endpoint to Azure Service Bus
- [ ] DD-8779 — [Import][FE] Performance: Status doesn't update in large number of files
- [ ] DD-8743 — [Export][BE] Include metadata in email notifications
- [ ] DD-8957 — Adjust Confidence Restriction to allow re-processing of any document
- [ ] DD-8710 — [Import][FE] Ability to Retrieve Job Summary on Older Imports
- [ ] DD-8602 — [NewImport] Exploration Detail Log shows only counts for files in root path

</details>

<details>
<summary><b>8. Bug Fixes</b></summary>

- [ ] DD-8941 — QEnergyUSA Regular Search Broken
- [ ] DD-8936 — Batch download for multiple emails error
- [ ] DD-8928 — Email Ingestion Error — 522: Connection timed out

</details>

---

## Notes / Fails / Blocks

<!-- Add a comment for each failed or blocked item with:
- Test case name
- Environment
- Steps to reproduce or reason blocked
-->
