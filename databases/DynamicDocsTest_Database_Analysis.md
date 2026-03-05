# Database Analysis: DynamicDocsTest

**Server:** Dynamic Docs QA (qa-skywell-db.c2fif7x7ouda.us-west-2.rds.amazonaws.com)  
**Analysis date:** February 28, 2026  
**Total relationships (Foreign Keys):** 252

---

## Table of Contents

- [Summary](#summary)
- [1. Configuration and Multi-Tenancy (Core)](#1-configuration-and-multi-tenancy-core)
- [2. Users, Roles and Permissions (RBAC)](#2-users-roles-and-permissions-rbac)
- [3. Location Hierarchy (Department → Cabinet → Folder)](#3-location-hierarchy-department--cabinet--folder)
- [4. Documents and Content (DMS Core)](#4-documents-and-content-dms-core)
- [5. Templates and Attributes (Document Typing)](#5-templates-and-attributes-document-typing)
- [6. Packets / Projects](#6-packets--projects)
- [7. Entities and Properties (Dynamic Metadata)](#7-entities-and-properties-dynamic-metadata)
- [8. OCR, Data Extraction and Text Analysis](#8-ocr-data-extraction-and-text-analysis)
- [9. Document Import and Export](#9-document-import-and-export)
- [10. Email Ingestion](#10-email-ingestion)
- [11. Notifications and Messaging](#11-notifications-and-messaging)
- [12. Auditing and Tracking](#12-auditing-and-tracking)
- [13. Auxiliary Tables and CDC](#13-auxiliary-tables-and-cdc)
- [14. Location Attributes](#14-location-attributes)
- [Simplified Main Relationship Diagram](#simplified-main-relationship-diagram)
- [Complete Foreign Key Relationships (252 total)](#complete-foreign-key-relationships-252-total)

---

## Summary

It is a multi-tenant **Document Management System (DMS)**. The architecture is based on:
- **Multi-tenancy** filtered by `ClientID`
- **Granular RBAC** (permissions at department, cabinet, folder, template and project level)
- Support for **OCR, data extraction, automated import/export and email capture**

---

## 1. CONFIGURATION AND MULTI-TENANCY (Core)

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **ConfigClient** | Central clients/tenants table. Almost all tables point here via `ClientID` |
| **ConfigState** | Geographic states catalog. Referenced by `ConfigClient` and `ConfigUser` |
| **ConfigModule** | System functional modules |
| **ClientModule** | N:N relationship between clients and enabled modules |
| **ClientSetting** | Client-specific settings (search type, etc.) |
| **ClientUserTab** | Custom tabs per client |

</details>

---

## 2. USERS, ROLES AND PERMISSIONS (RBAC)

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **ConfigUser** | System users → belong to `ConfigClient`, have `UserType` and `UserCategory` |
| **ConfigUserType** | User types |
| **ConfigUserCathegory** | User categories |
| **ConfigRole** | Roles defined per client |
| **ConfigUserRole** | N:N relationship between users and roles |
| **ConfigAction** | Possible actions (view, edit, delete, etc.) |
| **ConfigResource** | System resources on which permissions are applied |
| **ConfigResourceAction** | N:N relationship between resources and allowed actions |
| **ConfigPermission** | Permissions = combination of `Resource` + `Action` |
| **ConfigRolePermission** | Permissions assigned to roles |
| **ConfigUserPermission** | Permissions assigned directly to users |
| **ConfigQuestion / ConfigUserQuestion** | Security questions for users |

</details>

---

## 3. LOCATION HIERARCHY (Department → Cabinet → Folder)

<details>
<summary>Show content</summary>

```
Department (e.g.: "Accounting")
  └── Cabinet (e.g.: "Invoices 2025")
       └── Folder (e.g.: "January")
            └── Content (documents)
```

| Table | Purpose |
|-------|---------|
| **Department** | Highest level of organization → belongs to `ConfigClient` |
| **Cabinet** | Container within a department |
| **Folder** | Folder within a cabinet |
| **DepartmentConfigPermission** | Permissions on departments (Role/User + Action) |
| **CabinetConfigPermission** | Permissions on cabinets |
| **FolderConfigPermission** | Permissions on folders |
| **RootLocationConfigPermission** | Root-level location permissions |
| **DepartmentSpecialLocation** | Special locations per department |
| **FrozenFolder** | Frozen folders (non-modifiable) |
| **DefaultFolder** | Default folders per client |

</details>

---

## 4. DOCUMENTS AND CONTENT (DMS Core)

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **Content** | **Central documents table**. References `Folder`, `Template` and `LockedBy` (user) |
| **ContentVersion** | Document versions → references `Content`, `ConfigUser`, `OcrStatus`, `AnalysisStatus` |
| **ContentVersionComment** | Comments on document versions |
| **ContentAttribute** | Attribute/metadata values assigned to a document |
| **ContentEntity** | Entities associated with content |
| **ContentHashtag** | N:N relationship between content and hashtags |
| **ContentDeleted** | Deleted documents record (who deleted them) |
| **ContentNotification** | Notifications linked to documents and versions |
| **ContentReminder** | Reminders about documents (with source/destination user and role) |
| **ContentReminderExclude** | Users excluded from reminders |
| **LinkedContent** | Documents linked to other folders (shortcuts) |
| **FixedContent** | Pinned documents |
| **TemporaryContent** | Temporary content (being uploaded) |

</details>

---

## 5. TEMPLATES AND ATTRIBUTES (Document Typing)

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **Template** | Document types (e.g.: "Invoice", "Contract") → per client |
| **Attribute** | Attribute/metadata definition (name, type) → per client |
| **AttributeType** | Attribute type catalog (text, number, date, list, etc.) |
| **TemplateAttribute** | N:N relationship: which attributes each template has |
| **AttributeValueOption** | Predefined options for list-type attributes |
| **AttributeColumn** | Attribute column configuration |
| **TemplateFolder** | Relationship between templates and folders |
| **TemplateConfigPermission** | Permissions on templates (Role/User + Action) |
| **RootTemplateConfigPermission** | Root-level template permissions |
| **DefaultAttributesForRoles** | Default attributes per role |
| **DefaultAttributesForUpload** | Default attributes when uploading documents |

</details>

---

## 6. PACKETS / PROJECTS

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **Packet** | Packets/projects → per client, created by a user |
| **PacketContent** | N:N relationship: documents within a packet |
| **PacketEntity** | Entities associated with packets |
| **ProjectConfigPermission** | Permissions on projects |
| **RootProjectConfigPermission** | Root-level project permissions |
| **ProjectCreationRole** | Roles that can create projects |
| **ProjectAutopopulationRole** | Roles for project auto-population |
| **RoleDefaultProject** | Default project per role |

</details>

---

## 7. ENTITIES AND PROPERTIES (Dynamic Metadata)

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **EntityProperties** | Property definition per entity → references `ConfigClient` and `ConfigResource` |
| **Properties** | Specific properties within an entity |
| **PropertyValue** | Property values |
| **EntityLinking** | Linking between entities |
| **EntityAttributesForRoles** | Entity attributes per role |
| **DefaultEntityAttributesForRoles** | Default entity attributes per role |

</details>

---

## 8. OCR, DATA EXTRACTION AND TEXT ANALYSIS

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **OcrStatus** | OCR processing statuses |
| **DataExtractionEngine** | Data extraction engines |
| **DataExtractionResult** | Extraction results → per content, version, engine and client |
| **TemplateDataExtractionEngine** | N:N relationship between templates and extraction engines |
| **AnalysisStatus / AnalysisType** | Text analysis catalogs |
| **TextAnalysisJob** | Text analysis jobs |
| **TextAnalysisEntitiesResult** | Entities found by analysis |
| **TextAnalysisKeyPhrasesResult** | Key phrases found by analysis |

</details>

---

## 9. DOCUMENT IMPORT AND EXPORT

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **JobContentImport** | Content import jobs |
| **JobContentImportRunDetails** | Import execution details |
| **ImportJobSettings / ImportJobFtpSettings / ImportJobS3Settings** | Import configurations (local, FTP, S3) |
| **ImportHistory / ImportStatus / ImportTypes** | Import history and catalogs |
| **ExportServiceConfig** | Export service configuration |
| **ExportServiceRun** | Export executions |
| **ExportServiceType / ExportStatus** | Export catalogs |
| **ExportToCloudSettings** | Configuration for exporting to Box/Dropbox |
| **ExportToFtpSettings** | Configuration for exporting via FTP |
| **ExportContentInProcess / ExportContentRunDetails** | Exports in progress |
| **FileUploads / DocumentBatches / UploadStatus** | Batch upload management |

</details>

---

## 10. EMAIL INGESTION

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **JobEmailIngestionMailSetup** | Mailbox configuration |
| **JobEmailIngestionRules** | Classification rules (which Department/Cabinet/Folder/Template to route to) |
| **JobEmailIngestionHandledMessages** | Already processed messages |
| **JobEmailIngestionNotifyUsers** | Users to notify |
| **JobEmailIngestionRunDetail** | Execution details |

</details>

---

## 11. NOTIFICATIONS AND MESSAGING

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **ConfigNotification** | Per-user notification configuration |
| **ConfigNotificationType** | Notification types |
| **NotificationDeliveryType** | Delivery types (email, in-app, etc.) |
| **Notification** | Sent notifications |
| **NotificationHistory** | Delivery history |
| **Message** | Messages between users (with sender/receiver) |
| **UserReadMessage** | Read messages record |

</details>

---

## 12. AUDITING AND TRACKING

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **TrackContent** | Tracking of actions on documents |
| **TrackLocation** | Tracking of actions on locations |
| **TrackPacket** | Tracking of actions on packets |
| **UserSessionInfo** | User session information |
| **UserFeed** | User activity feed |
| **UserRetrieval** | Retrieved documents history |
| **UserTrackItem** | Items tracked by user |

</details>

---

## 13. AUXILIARY TABLES AND CDC

<details>
<summary>Show content</summary>

| Table | Purpose |
|-------|---------|
| **cdc.\*** | Change Data Capture tables (Debezium) for synchronization |
| **DebeziumHeartbeat** | Heartbeat for CDC |
| **VirtualLocation / VirtualLocationEntity** | Virtual locations |
| **SavedSearch** | Saved searches per user |
| **UserCart** | User document cart |
| **ScannerConfigurations** | Scanner configurations |
| **DBVersion / VersionInfo** | Database version control |
| **ColumnConfig / ColumnDisplayOrder** | Visible column configuration |

</details>

---

## 14. Location Attributes

<details>
<summary>Show content</summary>

**Location attributes** (metadata/properties associated with *locations* such as Department/Cabinet/Folder) are found in the **Entities and Properties (Dynamic Metadata)** block, using **`ConfigResource`** to identify the "Location" resource.

In this database, the pattern is:

- **Definition of "which attributes exist" for a resource**  
  → `EntityProperties` (by `ClientID` + `ResourceID`)
- **List of properties/attributes within that entity**  
  → `Properties` (by `EntityPropertiesID`)
- **Captured values**  
  → `PropertyValue` (by `PropertyId`)

### Key tables (where to look)

```text
EntityProperties   -> defines the property set per resource (e.g. Location) and client [**Find here the Location Attributes name**]
Properties         -> property/attribute catalog (name, etc.) within EntityProperties
PropertyValue      -> stored values of those properties
ConfigResource     -> resource catalog; look here for the Resource representing Location
```

### How to locate them specifically

1) **Find the ResourceID for "Location"** in `ConfigResource`.  
   (It may be called `Location`, `Locations`, `VirtualLocation` or similar; depends on the actual naming in your instance.)

2) With that `ResourceID`, search in `EntityProperties` for the client's rows (`ClientID`) for that resource.

3) With `EntityPropertiesID`, list the properties in `Properties`.

4) Values are in `PropertyValue` linked by `PropertyId`.

### Example guide query

```sql
-- 1) locate the ResourceID for "Location"
SELECT *
FROM ConfigResource
WHERE Name LIKE '%Location%';

-- 2) view property definitions for that resource and client
SELECT *
FROM EntityProperties
WHERE ResourceID = <ResourceID_Location>
  AND ClientID = <ClientID>;

-- 3) list attributes (properties) of that entity
SELECT p.*
FROM Properties p
JOIN EntityProperties ep ON ep.EntityPropertiesID = p.EntityPropertiesID
WHERE ep.ResourceID = <ResourceID_Location>
  AND ep.ClientID = <ClientID>;

-- 4) view captured values
SELECT pv.*
FROM PropertyValue pv
JOIN Properties p ON p.PropertyID = pv.PropertyId
JOIN EntityProperties ep ON ep.EntityPropertiesID = p.EntityPropertiesID
WHERE ep.ResourceID = <ResourceID_Location>
  AND ep.ClientID = <ClientID>;
```

### Note: location permissions ≠ location attributes

Tables like `DepartmentConfigPermission`, `CabinetConfigPermission`, `FolderConfigPermission`, `RootLocationConfigPermission` are **permissions**, not metadata.

</details>

---

## Simplified Main Relationship Diagram

<details>
<summary>Show content</summary>

```
ConfigClient (tenant)
├── ConfigUser ──── ConfigUserRole ──── ConfigRole
│    │                                     │
│    ├── ConfigUserPermission              ├── ConfigRolePermission
│    │         │                           │         │
│    │         └── ConfigPermission ───────┘         │
│    │              (Resource + Action)               │
│    │                                                │
├── Department ── Cabinet ── Folder ── Content ── ContentVersion
│                                        │              │
│                                        ├── ContentAttribute
│                                        ├── ContentHashtag
│                                        ├── LinkedContent
│                                        └── PacketContent ── Packet
│
├── Template ── TemplateAttribute ── Attribute
│                                       │
│                                       └── AttributeType
├── EntityProperties ── Properties ── PropertyValue
│
└── ExportServiceConfig / JobContentImport / JobEmailIngestion...
```

</details>

---

## Complete Foreign Key Relationships (252 total)

<details>
<summary>Show content</summary>

| Source Table | Column | Referenced Table | Referenced Column |
|---|---|---|---|
| Attribute | ClientId | ConfigClient | ClientID |
| Attribute | TypeId | AttributeType | AttributeTypeID |
| AttributeColumn | ClientID | ConfigClient | ClientID |
| AttributeValueOption | TemplateAttributeId | TemplateAttribute | TemplateAttributeId |
| BulkAssignPermissionsRunDetails | StatusId | ImportStatus | ImportStatusId |
| Cabinet | DepartmentID | Department | DepartmentID |
| CabinetConfigPermission | CabinetID | Cabinet | CabinetID |
| CabinetConfigPermission | ActionID | ConfigAction | ActionID |
| CabinetConfigPermission | RoleID | ConfigRole | RoleID |
| CabinetConfigPermission | UserID | ConfigUser | UserID |
| ClientContentSearchSource | ClientId | ConfigClient | ClientID |
| ClientContentSearchSource | ContentSearchSourceId | ContentSearchSource | ContentSearchSourceId |
| ClientDocumentManagementPanel | ClientID | ConfigClient | ClientID |
| ClientDocumentManagementPanel | DocumentManagementPanelID | DocumentManagementPanel | Id |
| ClientModule | ClientId | ConfigClient | ClientID |
| ClientModule | ModuleId | ConfigModule | Id |
| ClientSetting | ClientId | ConfigClient | ClientID |
| ClientSetting | SearchTypeId | SearchType | SearchTypeId |
| ClientUserTab | ClientId | ConfigClient | ClientID |
| ColumnDisplayOrder | ColumnID | ColumnConfig | ColumnID |
| ColumnDisplayOrder | ClientID | ConfigClient | ClientID |
| ConfigClient | StateID | ConfigState | StateID |
| ConfigNotification | ClientId | ConfigClient | ClientID |
| ConfigNotification | NotificationTypeID | ConfigNotificationType | NotificationTypeID |
| ConfigNotification | UserID | ConfigUser | UserID |
| ConfigNotification | NotificationDeliveryTypeId | NotificationDeliveryType | NotificationDeliveryTypeId |
| ConfigPermission | ActionID | ConfigAction | ActionID |
| ConfigPermission | ResourceID | ConfigResource | ResourceID |
| ConfigResourceAction | ActionID | ConfigAction | ActionID |
| ConfigResourceAction | ResourceID | ConfigResource | ResourceID |
| ConfigRole | ClientID | ConfigClient | ClientID |
| ConfigRolePermission | PermissionID | ConfigPermission | PermissionID |
| ConfigRolePermission | RoleID | ConfigRole | RoleID |
| ConfigStatus | ClientID | ConfigClient | ClientID |
| ConfigUser | ClientID | ConfigClient | ClientID |
| ConfigUser | StateID | ConfigState | StateID |
| ConfigUser | UserCathegoryID | ConfigUserCathegory | UserCathegoryID |
| ConfigUser | UserTypeId | ConfigUserType | UserTypeId |
| ConfigUserPermission | PermissionID | ConfigPermission | PermissionID |
| ConfigUserPermission | UserID | ConfigUser | UserID |
| ConfigUserQuestion | QuestionID | ConfigQuestion | QuestionID |
| ConfigUserQuestion | UserID | ConfigUser | UserID |
| ConfigUserRole | RoleID | ConfigRole | RoleID |
| ConfigUserRole | UserID | ConfigUser | UserID |
| Content | LockedBy | ConfigUser | UserID |
| Content | FolderID | Folder | FolderID |
| Content | TemplateID | Template | TemplateID |
| ContentAttribute | ContentID | Content | ContentID |
| ContentDeleted | DeletedBy | ConfigUser | UserID |
| ContentDeleted | ContentId | Content | ContentID |
| ContentEntity | ClientId | ConfigClient | ClientID |
| ContentEntity | ContentId | Content | ContentID |
| ContentHashtag | ContentID | Content | ContentID |
| ContentHashtag | HashtagID | Hashtag | HashtagID |
| ContentNotification | UserId | ConfigUser | UserID |
| ContentNotification | ContentId | Content | ContentID |
| ContentNotification | StatusId | ContentNotificationStatus | Id |
| ContentNotification | ContentVersionId | ContentVersion | ContentVersionID |
| ContentReminder | ClientId | ConfigClient | ClientID |
| ContentReminder | RoleId | ConfigRole | RoleID |
| ContentReminder | AddedByUserId | ConfigUser | UserID |
| ContentReminder | UserId | ConfigUser | UserID |
| ContentReminder | ContentId | Content | ContentID |
| ContentReminderExclude | UserId | ConfigUser | UserID |
| ContentReminderExclude | ContentReminderId | ContentReminder | Id |
| ContentVersion | AnalysisStatusId | AnalysisStatus | Id |
| ContentVersion | UserID | ConfigUser | UserID |
| ContentVersion | ContentID | Content | ContentID |
| ContentVersion | ProcessingStatus | OcrStatus | OcrStatusID |
| ContentVersionComment | UserID | ConfigUser | UserID |
| ContentVersionComment | ContentID | Content | ContentID |
| ContentVersionComment | ContentVersionID | ContentVersion | ContentVersionID |
| CustomerLocationsLabels | ClientID | ConfigClient | ClientID |
| CustomerLocationsLabels | ResourceID | ConfigResource | ResourceID |
| DataExtractionResult | AnalysisStatusId | AnalysisStatus | Id |
| DataExtractionResult | ClientId | ConfigClient | ClientID |
| DataExtractionResult | ContentId | Content | ContentID |
| DataExtractionResult | ContentVersionId | ContentVersion | ContentVersionID |
| DataExtractionResult | DataExtractionEngineId | DataExtractionEngine | Id |
| DefaultAttributesForRoles | ClientId | ConfigClient | ClientID |
| DefaultAttributesForRoles | RoleId | ConfigRole | RoleID |
| DefaultAttributesForRoles | OrderTypeId | SortOrderType | Id |
| DefaultAttributesForUpload | ClientID | ConfigClient | ClientID |
| DefaultAttributesForUpload | RoleID | ConfigRole | RoleID |
| DefaultAttributesForUpload | AttributeID | EntityProperties | EntityPropertiesID |
| DefaultEntityAttributesForRoles | ClientId | ConfigClient | ClientID |
| DefaultEntityAttributesForRoles | RoleId | ConfigRole | RoleID |
| DefaultEntityAttributesForRoles | AttributeId | EntityProperties | EntityPropertiesID |
| DefaultFolder | ClientID | ConfigClient | ClientID |
| DefaultFoldersForUpload | ClientID | ConfigClient | ClientID |
| DefaultFoldersForUpload | RoleID | ConfigRole | RoleID |
| Department | ClientID | ConfigClient | ClientID |
| DepartmentConfigPermission | ActionID | ConfigAction | ActionID |
| DepartmentConfigPermission | RoleID | ConfigRole | RoleID |
| DepartmentConfigPermission | UserID | ConfigUser | UserID |
| DepartmentConfigPermission | DepartmentID | Department | DepartmentID |
| EntityProperties | ClientID | ConfigClient | ClientID |
| EntityProperties | ResourceID | ConfigResource | ResourceID |
| ExportContentRunDetails | ClientID | ConfigClient | ClientID |
| ExportServiceConfig | ClientID | ConfigClient | ClientID |
| ExportServiceConfig | UserCategoryId | ConfigUserCathegory | UserCathegoryID |
| ExportServiceConfig | ExportTypeID | ExportServiceType | TypeID |
| ExportServiceConfig | PriorityID | ServicePriority | ID |
| ExportServiceRun | CabinetID | Cabinet | CabinetID |
| ExportServiceRun | DepartmentID | Department | DepartmentID |
| ExportServiceRun | ExportServiceID | ExportServiceConfig | ID |
| ExportServiceRun | StatusID | ExportStatus | ID |
| ExportServiceRun | FolderID | Folder | FolderID |
| ExportServiceRun | PacketID | Packet | PacketID |
| ExportServiceRun | TemplateID | Template | TemplateID |
| ExportToCloudSettings | BoxClient | ConnectedBoxAccount | ID |
| ExportToCloudSettings | DropBoxClient | ConnectedDropBoxAccount | ID |
| ExportToCloudSettings | ExportConfigID | ExportServiceConfig | ID |
| ExportToFtpSettings | ExportConfigID | ExportServiceConfig | ID |
| FileUploads | ContentId | Content | ContentID |
| FileUploads | DocumentBatchId | DocumentBatches | DocumentBatchId |
| FileUploads | UploadStatus | UploadStatus | UploadStatusId |
| FixedContent | ContentId | Content | ContentID |
| Folder | CabinetID | Cabinet | CabinetID |
| FolderConfigPermission | ActionID | ConfigAction | ActionID |
| FolderConfigPermission | RoleID | ConfigRole | RoleID |
| FolderConfigPermission | UserID | ConfigUser | UserID |
| FolderConfigPermission | FolderID | Folder | FolderID |
| FrozenFolder | ClientId | ConfigClient | ClientID |
| Hashtag | ClientID | ConfigClient | ClientID |
| ImportJobFtpSettings | JobId | JobContentImport | JobID |
| ImportJobS3Settings | JobId | JobContentImport | JobID |
| ImportJobSettings | JobId | JobContentImport | JobID |
| JobContentImport | ClientID | ConfigClient | ClientID |
| JobContentImport | ImportTypeId | ImportTypes | Id |
| JobContentImportRunDetails | ImportStatusId | ImportStatus | ImportStatusId |
| JobContentImportRunDetails | JobID | JobContentImport | JobID |
| JobEmailIngestionHandledMessages | MailSetupID | JobEmailIngestionMailSetup | ID |
| JobEmailIngestionMailSetup | ClientID | ConfigClient | ClientID |
| JobEmailIngestionNotifyUsers | UserID | ConfigUser | UserID |
| JobEmailIngestionNotifyUsers | JobEmailIngestionMailSetupID | JobEmailIngestionMailSetup | ID |
| JobEmailIngestionNotifyUsers | EmailRuleID | JobEmailIngestionRules | ID |
| JobEmailIngestionRules | CabinetID | Cabinet | CabinetID |
| JobEmailIngestionRules | DepartmnetID | Department | DepartmentID |
| JobEmailIngestionRules | FolderID | Folder | FolderID |
| JobEmailIngestionRules | DocumentTypeID | Template | TemplateID |
| JobEmailIngestionRules | MailSetupID | JobEmailIngestionMailSetup | ID |
| JobEmailIngestionRunDetail | JobID | JobEmailIngestionMailSetup | ID |
| LinkedContent | ContentId | Content | ContentID |
| LinkedContent | FolderId | Folder | FolderID |
| Message | ClientID | ConfigClient | ClientID |
| Message | ReceiverID | ConfigUser | UserID |
| Message | SenderID | ConfigUser | UserID |
| Notification | NotificationTypeID | ConfigNotificationType | NotificationTypeID |
| Notification | RoleID | ConfigRole | RoleID |
| Notification | UserID | ConfigUser | UserID |
| NotificationHistory | NotificationDeliveryTypeId | NotificationDeliveryType | NotificationDeliveryTypeId |
| Packet | ClientID | ConfigClient | ClientID |
| Packet | CreatedBy | ConfigUser | UserID |
| PacketContent | AddedBy | ConfigUser | UserID |
| PacketContent | ContentID | Content | ContentID |
| PacketContent | PacketID | Packet | PacketID |
| PacketEntity | ResourceID | ConfigResource | ResourceID |
| PacketEntity | AddedBy | ConfigUser | UserID |
| PacketEntity | PacketID | Packet | PacketID |
| ProjectAutopopulationRole | ClientId | ConfigClient | ClientID |
| ProjectAutopopulationRole | RoleId | ConfigRole | RoleID |
| ProjectConfigPermission | ActionId | ConfigAction | ActionID |
| ProjectConfigPermission | RoleId | ConfigRole | RoleID |
| ProjectConfigPermission | UserId | ConfigUser | UserID |
| ProjectConfigPermission | ProjectId | Packet | PacketID |
| ProjectCreationRole | ClientId | ConfigClient | ClientID |
| ProjectCreationRole | RoleId | ConfigRole | RoleID |
| Properties | EntityPropertiesID | EntityProperties | EntityPropertiesID |
| PropertyValue | PropertyId | Properties | PropertyID |
| ReviewerRole | RoleId | ConfigRole | RoleID |
| ReviewerRole | ClientId | ConfigClient | ClientID |
| RoleAdvancedViewRule | ClientID | ConfigClient | ClientID |
| RoleAdvancedViewRule | RoleID | ConfigRole | RoleID |
| RoleDefaultDepartment | ClientID | ConfigClient | ClientID |
| RoleDefaultDepartment | RoleID | ConfigRole | RoleID |
| RoleDefaultDepartment | DepartmentID | Department | DepartmentID |
| RoleDefaultProject | ClientID | ConfigClient | ClientID |
| RoleDefaultProject | RoleID | ConfigRole | RoleID |
| RootLocationConfigPermission | ActionID | ConfigAction | ActionID |
| RootLocationConfigPermission | ClientID | ConfigClient | ClientID |
| RootLocationConfigPermission | RoleID | ConfigRole | RoleID |
| RootLocationConfigPermission | UserID | ConfigUser | UserID |
| RootProjectConfigPermission | ActionId | ConfigAction | ActionID |
| RootProjectConfigPermission | ClientId | ConfigClient | ClientID |
| RootProjectConfigPermission | RoleId | ConfigRole | RoleID |
| RootProjectConfigPermission | UserId | ConfigUser | UserID |
| RootTemplateConfigPermission | ActionID | ConfigAction | ActionID |
| RootTemplateConfigPermission | ClientID | ConfigClient | ClientID |
| RootTemplateConfigPermission | RoleID | ConfigRole | RoleID |
| RootTemplateConfigPermission | UserID | ConfigUser | UserID |
| SavedSearch | ClientId | ConfigClient | ClientID |
| SavedSearch | AuthorId | ConfigUser | UserID |
| ScannerConfigurations | TargetCabinetID | Cabinet | CabinetID |
| ScannerConfigurations | ClientID | ConfigClient | ClientID |
| ScannerConfigurations | TargetDepartmentID | Department | DepartmentID |
| ScannerConfigurations | TargetFolderID | Folder | FolderID |
| ScannerConfigurations | TargetTemplateId | Template | TemplateID |
| Template | ClientID | ConfigClient | ClientID |
| TemplateAttribute | AttributeId | Attribute | AttributeId |
| TemplateAttribute | TemplateId | Template | TemplateID |
| TemplateConfigPermission | ActionID | ConfigAction | ActionID |
| TemplateConfigPermission | RoleID | ConfigRole | RoleID |
| TemplateConfigPermission | UserID | ConfigUser | UserID |
| TemplateConfigPermission | TemplateID | Template | TemplateID |
| TemplateDataExtractionEngine | DataExtractionEngineId | DataExtractionEngine | Id |
| TemplateDataExtractionEngine | TemplateId | Template | TemplateID |
| TemplateFolder | TemplateID | Template | TemplateID |
| TemporaryContent | ClientID | ConfigClient | ClientID |
| TemporaryContent | UserID | ConfigUser | UserID |
| TemporaryContent | ProcessingStatus | OcrStatus | OcrStatusID |
| TextAnalysisEntitiesResult | ContentVersionId | ContentVersion | ContentVersionID |
| TextAnalysisJob | AnalysisStatusId | AnalysisStatus | Id |
| TextAnalysisJob | AnalysisTypeId | AnalysisType | Id |
| TextAnalysisJob | UserId | ConfigUser | UserID |
| TextAnalysisJob | ContentVersionId | ContentVersion | ContentVersionID |
| TextAnalysisKeyPhrasesResult | ContentVersionId | ContentVersion | ContentVersionID |
| TrackContent | ClientId | ConfigClient | ClientID |
| TrackContent | UserID | ConfigUser | UserID |
| TrackContent | ContentID | Content | ContentID |
| TrackLocation | ClientId | ConfigClient | ClientID |
| TrackLocation | ResourceID | ConfigResource | ResourceID |
| TrackLocation | UserID | ConfigUser | UserID |
| TrackPacket | ClientId | ConfigClient | ClientID |
| TrackPacket | UserID | ConfigUser | UserID |
| TrackPacket | PacketID | Packet | PacketID |
| UserAdvancedViewRule | ClientID | ConfigClient | ClientID |
| UserAdvancedViewRule | UserID | ConfigUser | UserID |
| UserCart | AddToCartTypeId | AddToCartType | Id |
| UserCart | RoleId | ConfigRole | RoleID |
| UserCart | UserID | ConfigUser | UserID |
| UserCart | ContentID | Content | ContentID |
| UserCart | PacketID | Packet | PacketID |
| UserFeed | UserID | ConfigUser | UserID |
| UserReadMessage | MessageID | Message | MessageID |
| UserReadMessage | UserID | ConfigUser | UserID |
| UserRetrieval | UserID | ConfigUser | UserID |
| UserRetrieval | ContentID | Content | ContentID |
| UserRetrieval | ContentTypeID | Template | TemplateID |
| UserSessionInfo | UserID | ConfigUser | UserID |
| UserTrackItem | UserID | ConfigUser | UserID |
| UserTrackItem | ContentID | Content | ContentID |
| VirtualLocation | ClientID | ConfigClient | ClientID |
| VirtualLocation | ResourceID | ConfigResource | ResourceID |
| VirtualLocationEntity | VirtualLocationID | VirtualLocation | VirtualLocationID |

</details>
