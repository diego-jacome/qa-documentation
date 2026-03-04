# Análisis de la Base de Datos: DynamicDocsTest

**Servidor:** Dynamic Docs QA (qa-skywell-db.c2fif7x7ouda.us-west-2.rds.amazonaws.com)  
**Fecha de análisis:** 28 de febrero de 2026  
**Total de relaciones (Foreign Keys):** 252

---

## Índice

- [Resumen](#resumen)
- [1. Configuración y Multi-Tenancy (Núcleo)](#1-configuración-y-multi-tenancy-núcleo)
- [2. Usuarios, Roles y Permisos (RBAC)](#2-usuarios-roles-y-permisos-rbac)
- [3. Jerarquía de Ubicaciones (Department → Cabinet → Folder)](#3-jerarquía-de-ubicaciones-department--cabinet--folder)
- [4. Documentos y Contenido (Core del DMS)](#4-documentos-y-contenido-core-del-dms)
- [5. Templates y Atributos (Tipificación de documentos)](#5-templates-y-atributos-tipificación-de-documentos)
- [6. Packets / Proyectos](#6-packets--proyectos)
- [7. Entidades y Propiedades (Metadata dinámica)](#7-entidades-y-propiedades-metadata-dinámica)
- [8. OCR, Extracción de Datos y Análisis de Texto](#8-ocr-extracción-de-datos-y-análisis-de-texto)
- [9. Importación y Exportación de Documentos](#9-importación-y-exportación-de-documentos)
- [10. Email Ingestion (Capturas desde correo)](#10-email-ingestion-capturas-desde-correo)
- [11. Notificaciones y Mensajería](#11-notificaciones-y-mensajería)
- [12. Auditoría y Tracking](#12-auditoría-y-tracking)
- [13. Tablas Auxiliares y CDC](#13-tablas-auxiliares-y-cdc)
- [14. Atributos de Locación (Location Attributes)](#14-atributos-de-locación-location-attributes)
- [Diagrama de Relaciones Principales (Simplificado)](#diagrama-de-relaciones-principales-simplificado)
- [Relaciones Foreign Key Completas (252 total)](#relaciones-foreign-key-completas-252-total)

---

## Resumen

Es un sistema de **gestión documental (DMS)** multi-tenant. La arquitectura se basa en:
- **Multi-tenancy** filtrado por `ClientID`
- **RBAC granular** (permisos a nivel de departamento, gabinete, carpeta, template y proyecto)
- Soporte para **OCR, extracción de datos, importación/exportación automatizada y captura de email**

---

## 1. CONFIGURACIÓN Y MULTI-TENANCY (Núcleo)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **ConfigClient** | Tabla central de clientes/tenants. Casi todas las tablas apuntan aquí via `ClientID` |
| **ConfigState** | Catálogo de estados (geográficos). Referenciado por `ConfigClient` y `ConfigUser` |
| **ConfigModule** | Módulos funcionales del sistema |
| **ClientModule** | Relación N:N entre clientes y módulos habilitados |
| **ClientSetting** | Configuraciones específicas por cliente (tipo de búsqueda, etc.) |
| **ClientUserTab** | Tabs personalizados por cliente |

</details>

---

## 2. USUARIOS, ROLES Y PERMISOS (RBAC)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **ConfigUser** | Usuarios del sistema → pertenecen a `ConfigClient`, tienen `UserType` y `UserCategory` |
| **ConfigUserType** | Tipos de usuario |
| **ConfigUserCathegory** | Categorías de usuario |
| **ConfigRole** | Roles definidos por cliente |
| **ConfigUserRole** | Relación N:N entre usuarios y roles |
| **ConfigAction** | Acciones posibles (ver, editar, borrar, etc.) |
| **ConfigResource** | Recursos del sistema sobre los que se aplican permisos |
| **ConfigResourceAction** | Relación N:N entre recursos y acciones permitidas |
| **ConfigPermission** | Permisos = combinación de `Resource` + `Action` |
| **ConfigRolePermission** | Permisos asignados a roles |
| **ConfigUserPermission** | Permisos asignados directamente a usuarios |
| **ConfigQuestion / ConfigUserQuestion** | Preguntas de seguridad para usuarios |

</details>

---

## 3. JERARQUÍA DE UBICACIONES (Department → Cabinet → Folder)

<details>
<summary>Mostrar contenido</summary>

```
Department (ej: "Contabilidad")
  └── Cabinet (ej: "Facturas 2025")
       └── Folder (ej: "Enero")
            └── Content (documentos)
```

| Tabla | Propósito |
|-------|-----------|
| **Department** | Nivel más alto de organización → pertenece a `ConfigClient` |
| **Cabinet** | Contenedor dentro de un departamento |
| **Folder** | Carpeta dentro de un gabinete |
| **DepartmentConfigPermission** | Permisos sobre departamentos (Role/User + Action) |
| **CabinetConfigPermission** | Permisos sobre gabinetes |
| **FolderConfigPermission** | Permisos sobre carpetas |
| **RootLocationConfigPermission** | Permisos en nivel raíz de ubicaciones |
| **DepartmentSpecialLocation** | Ubicaciones especiales por departamento |
| **FrozenFolder** | Carpetas congeladas (no modificables) |
| **DefaultFolder** | Carpetas por defecto por cliente |

</details>

---

## 4. DOCUMENTOS Y CONTENIDO (Core del DMS)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **Content** | **Tabla central de documentos**. Referencia a `Folder`, `Template` y `LockedBy` (usuario) |
| **ContentVersion** | Versiones de un documento → referencia `Content`, `ConfigUser`, `OcrStatus`, `AnalysisStatus` |
| **ContentVersionComment** | Comentarios en versiones de documentos |
| **ContentAttribute** | Valores de atributos/metadatos asignados a un documento |
| **ContentEntity** | Entidades asociadas a un contenido |
| **ContentHashtag** | Relación N:N entre contenido y hashtags |
| **ContentDeleted** | Registro de documentos eliminados (quién los borró) |
| **ContentNotification** | Notificaciones ligadas a documentos y versiones |
| **ContentReminder** | Recordatorios sobre documentos (con usuario origen/destino y rol) |
| **ContentReminderExclude** | Usuarios excluidos de recordatorios |
| **LinkedContent** | Documentos vinculados a otras carpetas (accesos directos) |
| **FixedContent** | Documentos fijados/pinneados |
| **TemporaryContent** | Contenido temporal (en proceso de carga) |

</details>

---

## 5. TEMPLATES Y ATRIBUTOS (Tipificación de documentos)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **Template** | Tipos de documento (ej: "Factura", "Contrato") → por cliente |
| **Attribute** | Definición de atributos/metadatos (nombre, tipo) → por cliente |
| **AttributeType** | Catálogo de tipos de atributo (texto, número, fecha, lista, etc.) |
| **TemplateAttribute** | Relación N:N: qué atributos tiene cada template |
| **AttributeValueOption** | Opciones predefinidas para atributos tipo lista |
| **AttributeColumn** | Configuración de columnas de atributos |
| **TemplateFolder** | Relación entre templates y carpetas |
| **TemplateConfigPermission** | Permisos sobre templates (Role/User + Action) |
| **RootTemplateConfigPermission** | Permisos raíz sobre templates |
| **DefaultAttributesForRoles** | Atributos predeterminados por rol |
| **DefaultAttributesForUpload** | Atributos predeterminados al subir documentos |

</details>

---

## 6. PACKETS / PROYECTOS

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **Packet** | Paquetes/proyectos → por cliente, creados por un usuario |
| **PacketContent** | Relación N:N: documentos dentro de un paquete |
| **PacketEntity** | Entidades asociadas a paquetes |
| **ProjectConfigPermission** | Permisos sobre proyectos |
| **RootProjectConfigPermission** | Permisos raíz de proyectos |
| **ProjectCreationRole** | Roles que pueden crear proyectos |
| **ProjectAutopopulationRole** | Roles para auto-populación de proyectos |
| **RoleDefaultProject** | Proyecto por defecto por rol |

</details>

---

## 7. ENTIDADES Y PROPIEDADES (Metadata dinámica)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **EntityProperties** | Definición de propiedades por entidad → referencia `ConfigClient` y `ConfigResource` |
| **Properties** | Propiedades específicas dentro de una entidad |
| **PropertyValue** | Valores de las propiedades |
| **EntityLinking** | Vinculación entre entidades |
| **EntityAttributesForRoles** | Atributos de entidad por rol |
| **DefaultEntityAttributesForRoles** | Atributos de entidad por defecto por rol |

</details>

---

## 8. OCR, EXTRACCIÓN DE DATOS Y ANÁLISIS DE TEXTO

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **OcrStatus** | Estados del procesamiento OCR |
| **DataExtractionEngine** | Motores de extracción de datos |
| **DataExtractionResult** | Resultados de extracción → por contenido, versión, motor y cliente |
| **TemplateDataExtractionEngine** | Relación N:N entre templates y motores de extracción |
| **AnalysisStatus / AnalysisType** | Catálogos para análisis de texto |
| **TextAnalysisJob** | Trabajos de análisis de texto |
| **TextAnalysisEntitiesResult** | Entidades encontradas por análisis |
| **TextAnalysisKeyPhrasesResult** | Frases clave encontradas por análisis |

</details>

---

## 9. IMPORTACIÓN Y EXPORTACIÓN DE DOCUMENTOS

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **JobContentImport** | Jobs de importación de contenido |
| **JobContentImportRunDetails** | Detalles de ejecución de imports |
| **ImportJobSettings / ImportJobFtpSettings / ImportJobS3Settings** | Configuraciones de importación (local, FTP, S3) |
| **ImportHistory / ImportStatus / ImportTypes** | Historial y catálogos de importación |
| **ExportServiceConfig** | Configuración de servicios de exportación |
| **ExportServiceRun** | Ejecuciones de exportación |
| **ExportServiceType / ExportStatus** | Catálogos de exportación |
| **ExportToCloudSettings** | Configuración para exportar a Box/Dropbox |
| **ExportToFtpSettings** | Configuración para exportar via FTP |
| **ExportContentInProcess / ExportContentRunDetails** | Exportaciones en proceso |
| **FileUploads / DocumentBatches / UploadStatus** | Gestión de uploads por lotes |

</details>

---

## 10. EMAIL INGESTION (Capturas desde correo)

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **JobEmailIngestionMailSetup** | Configuración de buzones de correo |
| **JobEmailIngestionRules** | Reglas de clasificación (a qué Department/Cabinet/Folder/Template va) |
| **JobEmailIngestionHandledMessages** | Mensajes ya procesados |
| **JobEmailIngestionNotifyUsers** | Usuarios a notificar |
| **JobEmailIngestionRunDetail** | Detalles de ejecución |

</details>

---

## 11. NOTIFICACIONES Y MENSAJERÍA

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **ConfigNotification** | Configuración de notificaciones por usuario |
| **ConfigNotificationType** | Tipos de notificación |
| **NotificationDeliveryType** | Tipos de entrega (email, in-app, etc.) |
| **Notification** | Notificaciones enviadas |
| **NotificationHistory** | Historial de entregas |
| **Message** | Mensajes entre usuarios (con sender/receiver) |
| **UserReadMessage** | Registro de mensajes leídos |

</details>

---

## 12. AUDITORÍA Y TRACKING

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **TrackContent** | Tracking de acciones sobre documentos |
| **TrackLocation** | Tracking de acciones sobre ubicaciones |
| **TrackPacket** | Tracking de acciones sobre paquetes |
| **UserSessionInfo** | Información de sesiones de usuario |
| **UserFeed** | Feed de actividad del usuario |
| **UserRetrieval** | Historial de documentos recuperados |
| **UserTrackItem** | Items en seguimiento por usuario |

</details>

---

## 13. TABLAS AUXILIARES Y CDC

<details>
<summary>Mostrar contenido</summary>

| Tabla | Propósito |
|-------|-----------|
| **cdc.\*** | Tablas de Change Data Capture (Debezium) para sincronización |
| **DebeziumHeartbeat** | Heartbeat para CDC |
| **VirtualLocation / VirtualLocationEntity** | Ubicaciones virtuales |
| **SavedSearch** | Búsquedas guardadas por usuario |
| **UserCart** | Carrito de documentos del usuario |
| **ScannerConfigurations** | Configuraciones de escáner |
| **DBVersion / VersionInfo** | Control de versiones de la BD |
| **ColumnConfig / ColumnDisplayOrder** | Configuración de columnas visibles |

</details>

---

## 14. Atributos de Locación (Location Attributes)

<details>
<summary>Mostrar contenido</summary>

Los **atributos de locación** (metadata/propiedades asociadas a *ubicaciones* como Department/Cabinet/Folder) se encuentran en el bloque de **Entidades y Propiedades (Metadata dinámica)**, usando **`ConfigResource`** para identificar el recurso "Location".

En esta BD, el patrón es:

- **Definición de "qué atributos existen" para un recurso**  
  → `EntityProperties` (por `ClientID` + `ResourceID`)
- **Lista de propiedades/atributos dentro de esa entidad**  
  → `Properties` (por `EntityPropertiesID`)
- **Valores capturados**  
  → `PropertyValue` (por `PropertyId`)

### Tablas clave (donde mirar)

```text
EntityProperties   -> define el set de propiedades por recurso (ej. Location) y cliente
Properties         -> catálogo de propiedades/atributos (nombre, etc.) dentro de EntityProperties
PropertyValue      -> valores guardados de esas propiedades
ConfigResource     -> catálogo de recursos; aquí buscas el Resource que representa Location
```

### Cómo ubicarlos concretamente

1) **Encuentra el ResourceID de "Location"** en `ConfigResource`.  
   (A veces se llama `Location`, `Locations`, `VirtualLocation` o similar; depende del naming real en tu instancia.)

2) Con ese `ResourceID`, busca en `EntityProperties` las filas del cliente (`ClientID`) para ese recurso.

3) Con `EntityPropertiesID`, listás las propiedades en `Properties`.

4) Los valores van en `PropertyValue` enlazando por `PropertyId`.

### Ejemplo de consulta guía

```sql
-- 1) ubicar el ResourceID para "Location"
SELECT *
FROM ConfigResource
WHERE Name LIKE '%Location%';

-- 2) ver definiciones de propiedades para ese recurso y cliente
SELECT *
FROM EntityProperties
WHERE ResourceID = <ResourceID_Location>
  AND ClientID = <ClientID>;

-- 3) listar atributos (propiedades) de esa entidad
SELECT p.*
FROM Properties p
JOIN EntityProperties ep ON ep.EntityPropertiesID = p.EntityPropertiesID
WHERE ep.ResourceID = <ResourceID_Location>
  AND ep.ClientID = <ClientID>;

-- 4) ver valores capturados
SELECT pv.*
FROM PropertyValue pv
JOIN Properties p ON p.PropertyID = pv.PropertyId
JOIN EntityProperties ep ON ep.EntityPropertiesID = p.EntityPropertiesID
WHERE ep.ResourceID = <ResourceID_Location>
  AND ep.ClientID = <ClientID>;
```

### Nota: permisos de locación ≠ atributos de locación

Las tablas como `DepartmentConfigPermission`, `CabinetConfigPermission`, `FolderConfigPermission`, `RootLocationConfigPermission` son **permisos**, no metadata.

</details>

---

## Diagrama de Relaciones Principales (Simplificado)

<details>
<summary>Mostrar contenido</summary>

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

## Relaciones Foreign Key Completas (252 total)

<details>
<summary>Mostrar contenido</summary>

| Tabla Origen | Columna | Tabla Referenciada | Columna Referenciada |
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
