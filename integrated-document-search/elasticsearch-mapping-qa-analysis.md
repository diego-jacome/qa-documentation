# Elasticsearch Mapping — QA Analysis: `documents` Index

| | |
|---|---|
| **Index** | `documents` |
| **Related Guide** | [Integrated Searches Guide](Integrated_Searches_Guide.md) |
| **Version** | v1.0 |
| **Status** | Draft |
| **Date** | March 23, 2026 |
| **Author** | Diego Jacome |
| **Audience** | QA Team |

---

## Table of Contents

- [Elasticsearch Mapping — QA Analysis: `documents` Index](#elasticsearch-mapping--qa-analysis-documents-index)
  - [Table of Contents](#table-of-contents)
  - [General Configuration](#general-configuration)
  - [Main Fields](#main-fields)
  - [Boolean Flags as `long`](#boolean-flags-as-long)
  - [Nested Objects](#nested-objects)
    - [`attribute_values`](#attribute_values)
    - [`comments`](#comments)
    - [`hashtags`](#hashtags)
    - [`linked_to`](#linked_to)
    - [`packet` ⚠️ (object — NOT nested)](#packet-️-object--not-nested)
  - [The `EXPR$N` Fields](#the-exprn-fields)
  - [Architecture Summary](#architecture-summary)
  - [QA Issues to Validate](#qa-issues-to-validate)

---

## General Configuration

- **`_routing: required: true`** — Every operation on documents (index, get, delete) must include an explicit routing value. This means documents are intentionally distributed into specific shards, most likely by tenant (`client_id` or `system_id`).

> **QA implication**: Any API request that doesn't send the routing value will be rejected by Elasticsearch. Validate that every search, get, and delete operation includes the correct routing key.

---

## Main Fields

| Field | Type | Notes |
|---|---|---|
| `client_id` | `keyword` | Client/tenant identifier — exact match only |
| `system_id` | `keyword` | Source system — multi-system support |
| `document_id` | `text + keyword` | Document ID with full-text and exact search |
| `doc_name` | `text + keyword` | Document name |
| `content` | `text + keyword` | Full-text content (likely from OCR or text extraction) |
| `content_id` | `long` | Indexed content ID |
| `content_version` | `long` | Version control field |
| `template_id` | `long` | Template associated with the document |
| `extension` | `text + keyword` | File extension |
| `file_ref` | `keyword` | Reference to the file in storage |
| `file_size` | `float` | File size |
| `ocr_confidence` | `float` | OCR confidence score (0–1 or 0–100 — validate range) |
| `processing_status` | `text + keyword` | Document processing state |
| `creation_date` | `long` | Creation date stored as epoch (ms) |
| `last_modification_date` | `long` | Last modification stored as epoch (ms) |
| `primary_location_id` | `long` | Primary location in hierarchy |
| `secondary_location_id` | `long` | Secondary location |
| `tertiary_location_id` | `long` | Tertiary location |

---

## Boolean Flags as `long`

These fields behave as boolean flags (expected values: `0` or `1`) but are mapped as `long`:

| Field | Meaning |
|---|---|
| `is_content_active` | Whether the content is active |
| `is_current` | Whether this is the current version |
| `is_locked` | Whether the document is locked |
| `is_soft_deleted` | Logical/soft deletion flag |
| `locked_by` | ID of the user who locked the document |

> **Note**: Using `long` instead of `boolean` works but is storage-inefficient and less semantic. Native Elasticsearch boolean operators (`filter: term`) will still work, but values must always be `0` or `1`.

---

## Nested Objects

These fields use the `nested` type, meaning each element in the array is indexed as an isolated internal document. This prevents cross-object field matching (false positives) that occurs with the default `object` type.

### `attribute_values`

Dynamic metadata/attributes associated with the document.

| Sub-field | Type | Notes |
|---|---|---|
| `attribute_id` | `long` | Attribute identifier |
| `value` | `text + keyword` | Text value of the attribute |
| `date_value` | `long` | Date value stored as epoch |
| `EXPR$0` | `long` | Unnamed calculated column |
| `EXPR$1` | `text + keyword` | Unnamed calculated column |
| `EXPR$2` | `long` | Unnamed calculated column |

Maps to the API request body fields: `attributes[].attributeId`, `attributes[].value`, `attributes[].dateValue`, `attributes[].dateFrom/dateTo`, `attributes[].numberFrom/numberTo`

---

### `comments`

Comments associated with the document.

| Sub-field | Type | Notes |
|---|---|---|
| `comment` | `text + keyword` | Comment text |
| `user_id` | `long` | Author's user ID |
| `EXPR$0` | `text + keyword` | Unnamed calculated column |
| `EXPR$1` | `long` | Unnamed calculated column |

Maps to: `document.comments[].userId`, `document.comments[].comment`

---

### `hashtags`

Tags/categories assigned to the document.

| Sub-field | Type | Notes |
|---|---|---|
| `name` | `text + keyword` | Tag name |
| `EXPR$0` | `text + keyword` | Unnamed calculated column |

Maps to: `document.hashtags[]`

---

### `linked_to`

Related documents or entities.

| Sub-field | Type | Notes |
|---|---|---|
| `tertiary_id` | `long` | Related entity ID |
| `name` | `text + keyword` | Related entity name |
| `EXPR$0` | `long` | Unnamed calculated column |
| `EXPR$1` | `text + keyword` | Unnamed calculated column |

Maps to: `document.linkedTo[].tertiaryId`, `document.linkedTo[].name`

---

### `packet` ⚠️ (object — NOT nested)

Packet/dossier information. Unlike the others, this is mapped as a plain **object**, not `nested`.

| Sub-field | Type |
|---|---|
| `packet_id` | `long` |
| `order` | `long` |
| `is_read_only` | `boolean` |
| `EXPR$0` | `long` |
| `EXPR$1` | `long` |
| `EXPR$2` | `boolean` |

> **Risk**: Since this is `object` (not `nested`), if a document belongs to multiple packets, Elasticsearch internal flattening can produce false positives in queries. Validate that each document only ever has a single packet, or that this behavior is acceptable.

Maps to: `document.packetIds[]`

---

## The `EXPR$N` Fields

Almost all nested objects contain unnamed fields: `EXPR$0`, `EXPR$1`, `EXPR$2`.

**Root cause**: The index is populated through a **SQL → Elasticsearch pipeline** (likely Apache Calcite, Apache Drill, or a JDBC connector). When SQL query columns don't have explicit aliases, they are auto-generated as `EXPR$0`, `EXPR$1`, etc.

**Implications for QA**:
- These fields are ambiguous — their meaning depends entirely on the **column order** in the source SQL query.
- If the source query changes column order, the mapping breaks silently.
- Validate whether these fields are actually used in search queries or aggregations. If not, they add noise.
- If they are used, they represent a **brittle dependency** on SQL column ordering.

---

## Architecture Summary

```
Multi-tenant Document Management System (DMS)
├── Routing required   → shard distribution by tenant
├── Versioning         → is_current, content_version
├── Soft delete        → is_soft_deleted
├── Locking            → is_locked, locked_by
├── OCR processing     → content, ocr_confidence, processing_status
├── Location hierarchy → primary / secondary / tertiary location IDs
├── Dynamic attributes → attribute_values (nested)
├── Collaboration      → comments (nested)
├── Tagging            → hashtags (nested)
├── Relations          → linked_to (nested)
└── Dossiers           → packet (object — NOT nested)
```

---

## QA Issues to Validate

| # | Issue | Risk | What to Test |
|---|---|---|---|
| 1 | **`EXPR$N` fields** | High | Verify if these are used in queries. If so, validate they don't break when the source SQL changes column order. |
| 2 | **Dates as `long`** | Medium | Confirm all date fields arrive as epoch milliseconds. Range filters (`dateFrom`/`dateTo`) must convert correctly before querying. |
| 3 | **`packet` as `object` vs `nested`** | Medium | Test documents belonging to multiple packets. Validate there are no false positive matches across different packet entries. |
| 4 | **Boolean flags as `long`** | Low–Medium | Validate that `is_current`, `is_locked`, `is_soft_deleted`, `is_content_active` only ever store `0` or `1`. Test filtering on each. |
| 5 | **`document_id` as `text`** | Low | If used as a unique identifier, ensure queries always use `.keyword` subfield for exact matching, not the analyzed `text` field. |
| 6 | **`ocr_confidence` range** | Low | Clarify and document the valid range (0–1 or 0–100). Validate `minOCRConfidence`/`maxOCRConfidence` filters work correctly at boundaries. |
| 7 | **`_routing` enforcement** | High | Confirm that requests without routing are rejected. Validate the routing key is consistent across index, get, update, and delete operations for the same document. |
| 8 | **`softDeletedFilter`** | High | Test all three values: `ExcludeDeleted`, `IncludeDeleted`, and `OnlyDeleted` (if supported). Confirm `is_soft_deleted` is correctly applied in each case. |

---

## Elasticsearch Queries for QA Validation

> All queries filter by `system_id` to scope results to the target system. Replace `63` with the actual system ID for your test environment.

---

### Q1 — Verify boolean flags only contain values 0 or 1

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "is_soft_deleted_values": {
      "terms": { "field": "is_soft_deleted" }
    },
    "is_current_values": {
      "terms": { "field": "is_current" }
    },
    "is_locked_values": {
      "terms": { "field": "is_locked" }
    },
    "is_content_active_values": {
      "terms": { "field": "is_content_active" }
    }
  }
}
```
> If any value other than `0` or `1` appears, it is a data integrity bug.

---

### Q2 — Documents with no valid `is_current` value (versioning orphans)

```json
GET documents/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "system_id": "63" } }
      ],
      "must_not": [
        { "term": { "is_current": 1 } },
        { "term": { "is_current": 0 } }
      ]
    }
  }
}
```

---

### Q3 — Documents soft-deleted but still marked as active

```json
GET documents/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "system_id": "63" } },
        { "term": { "is_soft_deleted": 1 } },
        { "term": { "is_content_active": 1 } }
      ]
    }
  }
}
```
> A soft-deleted document should never be active at the same time.

---

### Q4 — Distribution of `processing_status` by tenant

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "by_client": {
      "terms": { "field": "client_id" },
      "aggs": {
        "by_status": {
          "terms": { "field": "processing_status.keyword" }
        }
      }
    }
  }
}
```

---

### Q5 — OCR confidence score distribution (validate range)

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "ocr_stats": {
      "extended_stats": { "field": "ocr_confidence" }
    },
    "ocr_ranges": {
      "range": {
        "field": "ocr_confidence",
        "ranges": [
          { "key": "< 0 (invalid)", "to": 0 },
          { "key": "0.0 – 0.5 (low)", "from": 0, "to": 0.5 },
          { "key": "0.5 – 0.8 (medium)", "from": 0.5, "to": 0.8 },
          { "key": "0.8 – 1.0 (high)", "from": 0.8, "to": 1.0 },
          { "key": "> 1.0 (scale 0-100?)", "from": 1.0 }
        ]
      }
    }
  }
}
```
> Confirms whether the scale is 0–1 or 0–100.

---

### Q6 — Multiple versions per `content_id` — verify only one has `is_current = 1`

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "by_content_id": {
      "terms": {
        "field": "content_id",
        "min_doc_count": 2
      },
      "aggs": {
        "current_count": {
          "filter": { "term": { "is_current": 1 } }
        }
      }
    }
  }
}
```
> If `current_count.doc_count > 1` for any `content_id`, there is a versioning bug.

---

### Q7 — Documents locked (`is_locked = 1`) but missing `locked_by`

```json
GET documents/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "system_id": "63" } },
        { "term": { "is_locked": 1 } }
      ],
      "must_not": [
        { "exists": { "field": "locked_by" } }
      ]
    }
  }
}
```

---

### Q8 — Nested query on `attribute_values` (validates no cross-object mixing)

```json
GET documents/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "system_id": "63" } },
        {
          "nested": {
            "path": "attribute_values",
            "query": {
              "bool": {
                "must": [
                  { "term": { "attribute_values.attribute_id": 5 } },
                  { "match": { "attribute_values.value": "confidential" } }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```
> The `nested` type ensures both conditions are met within the **same** attribute object, preventing false positives.

---

### Q9 — Inspect `packet` field presence and distribution

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "has_packet": {
      "filter": { "exists": { "field": "packet.packet_id" } },
      "aggs": {
        "packet_ids": {
          "terms": { "field": "packet.packet_id" }
        }
      }
    }
  }
}
```
> Since `packet` is `object` (not `nested`), validate that no document has multiple packet entries that could cause cross-matching.

---

### Q10 — Documents without a primary location assigned (orphans)

```json
GET documents/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "system_id": "63" } }
      ],
      "must_not": [
        { "exists": { "field": "primary_location_id" } }
      ]
    }
  }
}
```

---

### Q11 — File size statistics by tenant

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "by_client": {
      "terms": { "field": "client_id" },
      "aggs": {
        "max_file_size": { "max": { "field": "file_size" } },
        "avg_file_size": { "avg": { "field": "file_size" } },
        "total_storage": { "sum": { "field": "file_size" } }
      }
    }
  }
}
```

---

### Q12 — Check if `EXPR$N` fields in nested objects are populated

```json
GET documents/_search
{
  "size": 0,
  "query": {
    "term": { "system_id": "63" }
  },
  "aggs": {
    "expr_in_attributes": {
      "nested": { "path": "attribute_values" },
      "aggs": {
        "has_expr0": { "filter": { "exists": { "field": "attribute_values.EXPR$0" } } },
        "has_expr1": { "filter": { "exists": { "field": "attribute_values.EXPR$1" } } },
        "has_expr2": { "filter": { "exists": { "field": "attribute_values.EXPR$2" } } }
      }
    }
  }
}
```
> If `EXPR$N` counts are always 0, those fields are dead weight in the index.

---

### Query Reference Summary

| # | Query | Category | Risk Validated |
|---|---|---|---|
| Q1 | Boolean flags distribution | Data integrity | Boolean flags as `long` |
| Q2 | Versioning orphans | Data integrity | Versioning |
| Q3 | Soft-deleted + active conflict | Data integrity | Soft delete logic |
| Q4 | Processing status by tenant | Observability | Processing pipeline |
| Q5 | OCR confidence range | Data integrity | OCR score scale |
| Q6 | Multiple `is_current = 1` per content | Data integrity | Versioning |
| Q7 | Locked without `locked_by` | Data integrity | Locking |
| Q8 | Nested attribute cross-match | Correctness | Nested vs Object |
| Q9 | Packet distribution | Correctness | Object flattening risk |
| Q10 | Documents without location | Data integrity | Orphan documents |
| Q11 | File size stats by tenant | Observability | Storage |
| Q12 | EXPR$N field population | Data integrity | SQL pipeline fields |
