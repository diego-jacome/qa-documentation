# How to Test CMIS Integration

## References
- **Swagger**: https://api-qa.archeiotech.com/swagger/index.html
- **Postman Collection**: `DynamicDocsCMISAtomPub v2` (credentials stored in Authorization tab)

---

## Actions Reference

| Action | Folder | Endpoint | Parameter | Notes |
|--------|--------|----------|-----------|-------|
| Document Uploaded | Object Services | `createDocument` | folder ID | Posible cambiar nombre y tipo del documento en el request body. |
| Document Viewed | Object Services | `getObject` | document ID | Copiar el document ID desde Document menu. |
| Document Downloaded | Object Services | `getContentStream` | document ID | |
| Document Replaced | Object Services | `setContentStream` | document ID | |
| Document added to Project | Object Services | `updateProperties – project` | project ID | Project menu → Copy Project ID. En el body agregar: `<cmis:value>document-4216597</cmis:value>` |
| Document linked to Location | Multi-Filing Services | `addObjectToFolder` | folder ID | Insertar document ID en el request body: `<cmis:value>document-1216</cmis:value>` |
| Document unlinked from Location | Multi-Filing Services | `removeObjectFromFolder` | folder ID | Insertar document ID en el request body: `<cmis:value>document-1216</cmis:value>` |
| Document Deleted | Object Services | `deleteObject` | document ID | |

---

## Notas de uso

- Los **IDs de carpeta (folder ID)** se obtienen desde la UI (menú de carpeta → Copy folder ID).
- Los **IDs de documento (document ID)** se obtienen desde Document menu → Copy document ID.
- Los **IDs de proyecto (project ID)** se obtienen desde Project menu → Copy Project ID.
- Las colecciones de la API CMIS están en `scripts/dd-api/collections/cmis-api.<env>.openapi.json`.
