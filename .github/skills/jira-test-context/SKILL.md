---
name: jira-test-context
description: 'Genera un resumen de contexto de un ticket de Jira para facilitar su testing. Usar cuando el usuario mencione frases como: "necesito testear el ticket", "analiza el ticket", "dame contexto del ticket", "voy a testear DD-XXXX", o cuando proporcione un ID de ticket Jira (ej: DD-1234, QA-567). El flujo incluye obtener datos del ticket via API y analizar capturas de pantalla adjuntas.'
argument-hint: 'ID del ticket Jira (ej: DD-1234)'
---

# Jira Test Context

## Propósito
Generar un resumen estructurado de un ticket de Jira para facilitar su testing, combinando datos de la API con análisis visual de capturas de pantalla.

## Cuándo activarse
- El usuario menciona un ID de ticket (patrón: letras mayúsculas + guión + número, ej: `DD-1234`, `QA-567`)
- El usuario dice "testear", "analizar", "dame contexto" + un ticket
- El usuario quiere preparar casos de prueba para un ticket

## Procedimiento

### Paso 1 — Obtener datos del ticket
Ejecutar el script de Jira con el ID del ticket:

```
python scripts/jira/jira_ticket_detail.py <TICKET-ID>
```

El script está en `scripts/jira/` y retorna:
- Información básica (estado, tipo, prioridad, asignado, sprint)
- Descripción completa
- Criterios de aceptación
- Comentarios
- Sub-tareas y tickets vinculados

### Paso 2 — Solicitar capturas de pantalla
Indicar al usuario:

> "Si tienes capturas de pantalla del ticket, puedes encontrarlas en `attachments/<TICKET-ID>/` o adjuntarlas directamente al chat para que las analice."

Las imágenes se guardan con el patrón: `attachments/<TICKET-ID>/image-YYYYMMDD-HHMMSS.png`

### Paso 3 — Generar el resumen de contexto
Con los datos del script (y las imágenes si el usuario las adjunta), producir un resumen con esta estructura:

---

## 🎫 Contexto de Testing: `<TICKET-ID>`

### Resumen
Descripción breve del objetivo del ticket en 2-3 oraciones.

### Información clave
| Campo | Valor |
|-------|-------|
| Tipo | Bug / Story / Task |
| Estado | En desarrollo / En QA / etc. |
| Prioridad | Alta / Media / Baja |
| Sprint | Nombre del sprint |
| Asignado | Nombre |

### ¿Qué se espera probar?
Explicación clara de la funcionalidad o fix que hay que validar, basada en la descripción y criterios de aceptación.

### Criterios de aceptación
Lista de los criterios de aceptación extraídos del ticket.

### Casos de prueba sugeridos
Lista de escenarios a probar, incluyendo:
- ✅ Happy path (caso exitoso)
- ❌ Edge cases (casos límite)
- 🔄 Regresiones relacionadas a considerar

### Análisis de capturas de pantalla
*(Solo si el usuario adjuntó imágenes)* — Descripción de lo que muestran las capturas y cómo se relacionan con los criterios de prueba.

### Notas adicionales
Observaciones de los comentarios del ticket, sub-tareas pendientes, o tickets vinculados relevantes para el testing.

---

## Notas de implementación
- Si el script falla por credenciales, recordar al usuario que necesita `.env` con `JIRA_EMAIL` y `JIRA_API_TOKEN`
- Si el ticket no existe, informar claramente y pedir confirmación del ID
- Las capturas de pantalla son opcionales — el resumen se genera con o sin ellas
