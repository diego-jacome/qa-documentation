# Skill: Release Email — Dynamic Docs

## Cuándo usar este skill
Cuando el usuario diga: "crea el correo del release", "genera el email del release", "prepara el correo para el release XX.XX", o similares.

---

## Flujo completo

### 1. Obtener features y bug fixes
- El usuario proporciona una imagen o tabla con los ítems del release.
- Extraer cada ítem y su ID de Jira (ej: DD-9013).
- Limpiar los títulos: quitar brackets `[TAG]`, dejar mayúsculas solo en nombres de servicios/tecnologías (Vue.js, Email Service, Integrated Search, Drag & Drop, Settings, Client Admin, Export Service, etc.).

### 2. Verificar que los tickets estén en la versión correcta de Jira
- Usar el script: `python scripts/jira/_verify_release.py`
- El script consulta `fixVersions` de cada ticket via REST API de Jira.
- Credenciales: `scripts/jira/.env` → `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
- URL de release en Jira: `https://archeiojira.atlassian.net/projects/DD/versions/{VERSION_ID}/tab/release-report-all-issues`

### 3. Obtener resultados de regresión automatizada
- El usuario proporciona una imagen del reporte (ej: Pie Chart de ADO Test Plans).
- Extraer: % passed, # passed, # failed, # total, run ID.
- El usuario indica los failures conocidos y si hay tickets ADO asociados.
- Consultar título del ticket ADO si se proporciona ID: `python scripts/ado/ado_ticket_detail.py {ID}`

### 4. Leer el template del release anterior
- Template guardado en: `C:\Users\{user}\Documents\Outlook Templates\Dynamic_Docs_Release_{VERSION}.oft`
- Script para leerlo: `python scripts/outlook/_read_template.py`
- Replicar el estilo HTML: fuente Calibri 11pt, listas `<ul>`, mismo orden de secciones.

### 5. Generar el draft en Outlook
- Script: `python scripts/outlook/_draft_release_2606.py` (adaptar para cada release)
- **To:** `Regression Reports [Management]`
- **CC:** `Regression Reports [DD Team]` + `diego.jacome@quorumsoftware.com`
- Imagen embebida via CID: adjuntar PNG y asignar CID `regression_chart`, referenciar con `<img src="cid:regression_chart">`
- Imagen del reporte de regresión: `C:\Users\diego.jacome\OneDrive - Quorum Business Solutions\Pictures\Pie Chart Automation.png`
- Guardar como borrador: `mail.Save()`

### 6. Guardar el template del nuevo release
- Script: `python scripts/outlook/_save_template.py`
- Guardar en: `C:\Users\{user}\Documents\Outlook Templates\Dynamic_Docs_Release_{VERSION}.oft`

---

## Estructura del correo

```
Subject: Dynamic Docs Release {VERSION}

Hi Team. Version {VERSION} of Dynamic Docs has been released in the Staging environment.
[Si hay failures conocidos en regresión: mencionar brevemente + link al ADO ticket del fix]

New Features:
- {item 1}
- {item 2}
...

Bug fixes:
- {item 1}
...

Notes:
- The detailed list is here. [link a Jira release]
- Next release on Production: {fecha}

Testing Notes:
- Manual testing was performed on OnDemand QA1 and Encino tenants.
- Automated test run in QA was executed with {X}% pass rate ({passed} passed / {failed} failed / {total} total — run {RUN_ID}).
  - [Failures conocidos con link al ticket ADO si aplica]
  - [Trabajo pendiente en automation si aplica]
  [imagen del pie chart embebida]

If you have any questions, please reach out to the QA team.
```

---

## Scripts involucrados

| Script | Propósito |
|--------|-----------|
| `scripts/jira/_verify_release.py` | Verifica fixVersions en Jira |
| `scripts/outlook/_read_template.py` | Lee HTML del .oft anterior |
| `scripts/outlook/_draft_release_XXXX.py` | Crea el draft en Outlook |
| `scripts/outlook/_save_template.py` | Guarda el correo enviado como .oft |
| `scripts/outlook/_list_dl.py` | Lista listas de distribución |
| `scripts/outlook/_add_dl_member.py` | Agrega miembro a una lista |
| `scripts/outlook/_remove_dl_member.py` | Elimina miembro de una lista |
| `scripts/ado/ado_ticket_detail.py` | Detalle de ticket ADO |

---

## Listas de distribución

| Lista | Rol en correo |
|-------|--------------|
| `Regression Reports [Management]` | **To** |
| `Regression Reports [DD Team]` | **CC** |

---

## Notas importantes
- Siempre preguntar la **fecha del próximo release en Production** antes de generar el draft.
- Mostrar el borrador del cuerpo al usuario para aprobación antes de ejecutar el script.
- La imagen de regresión es un PNG en `OneDrive - Quorum Business Solutions\Pictures\`. Confirmar el nombre si cambia entre releases.
- Para embeber la imagen en el HTML de Outlook via COM: usar `mail.Attachments.Add()` + `PropertyAccessor.SetProperty` para asignar el CID.
