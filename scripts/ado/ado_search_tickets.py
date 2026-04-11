#!/usr/bin/env python3
"""
ado_search_tickets.py
Busca work items en Azure DevOps via REST API usando WIQL (Work Item Query Language).

Uso:
    python ado_search_tickets.py
    python ado_search_tickets.py "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active'"

Autenticacion:
    Requiere las siguientes variables en el archivo .env (en la misma carpeta):
        ADO_URL         — URL base de la organización (ej: https://dev.azure.com/mi-org)
        ADO_PROJECT     — Nombre del proyecto (ej: MyProject)
        ADO_PAT         — Personal Access Token generado en Azure DevOps

    Cómo generar un PAT:
        1. Ve a Azure DevOps → tu perfil (esquina superior derecha)
        2. User Settings → Personal access tokens
        3. New Token → selecciona scopes: Work Items (Read)
        4. Copia el token generado y pégalo en ADO_PAT del .env

Ejemplos de WIQL:
    SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active' ORDER BY [System.ChangedDate] DESC
    SELECT [System.Id] FROM WorkItems WHERE [System.WorkItemType] = 'Bug' AND [System.State] <> 'Closed'
    SELECT [System.Id] FROM WorkItems WHERE [System.AssignedTo] = @Me
    SELECT [System.Id] FROM WorkItems WHERE [System.IterationPath] UNDER @CurrentIteration
    SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'regression'
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Buscar .env en la misma carpeta que el script
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(script_dir, ".env"))

ADO_URL     = os.getenv("ADO_URL", "").rstrip("/")
ADO_PROJECT = os.getenv("ADO_PROJECT", "")
ADO_PAT     = os.getenv("ADO_PAT", "")
API_VERSION = "7.1"
MAX_RESULTS = 50

DIVIDER = "─" * 70

# Campos a traer en el batch de work items
WORK_ITEM_FIELDS = [
    "System.Id",
    "System.Title",
    "System.State",
    "System.WorkItemType",
    "System.AssignedTo",
    "System.CreatedDate",
    "System.ChangedDate",
    "Microsoft.VSTS.Common.Priority",
    "System.Tags",
    "System.IterationPath",
    "System.AreaPath",
]


# ── helpers ──────────────────────────────────────────────────────────────────

def build_auth():
    if not ADO_URL or not ADO_PROJECT or not ADO_PAT:
        print("❌  Faltan variables en el .env: ADO_URL, ADO_PROJECT y/o ADO_PAT.")
        sys.exit(1)
    # Azure DevOps: user vacío, PAT como contraseña
    return HTTPBasicAuth("", ADO_PAT), {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def run_wiql(wiql: str, max_results: int = MAX_RESULTS) -> list[int]:
    """Ejecuta una consulta WIQL y devuelve la lista de IDs."""
    auth, headers = build_auth()
    url = f"{ADO_URL}/{ADO_PROJECT}/_apis/wit/wiql?api-version={API_VERSION}&$top={max_results}"
    payload = {"query": wiql}
    r = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
    if not r.ok:
        try:
            msg = r.json().get("message", r.text)
        except Exception:
            msg = r.text
        raise requests.exceptions.HTTPError(
            f"HTTP {r.status_code}: {msg}", response=r
        )
    work_items = r.json().get("workItems", [])
    return [wi["id"] for wi in work_items]


def fetch_work_items_batch(ids: list[int]) -> list[dict]:
    """Trae los detalles de una lista de IDs en una sola llamada batch."""
    if not ids:
        return []
    auth, headers = build_auth()
    url = (
        f"{ADO_URL}/{ADO_PROJECT}/_apis/wit/workitems"
        f"?ids={','.join(str(i) for i in ids)}"
        f"&fields={','.join(WORK_ITEM_FIELDS)}"
        f"&api-version={API_VERSION}"
    )
    r = requests.get(url, headers=headers, auth=auth, timeout=30)
    if not r.ok:
        try:
            msg = r.json().get("message", r.text)
        except Exception:
            msg = r.text
        raise requests.exceptions.HTTPError(
            f"HTTP {r.status_code}: {msg}", response=r
        )
    return r.json().get("value", [])


def format_work_item(wi: dict) -> str:
    fields  = wi.get("fields", {})
    wi_id   = wi.get("id", "N/A")
    title   = fields.get("System.Title", "")
    state   = fields.get("System.State", "—")
    wi_type = fields.get("System.WorkItemType", "—")
    priority = fields.get("Microsoft.VSTS.Common.Priority", "—")
    assigned = (fields.get("System.AssignedTo") or {}).get("displayName", "Sin asignar")
    created  = (fields.get("System.CreatedDate") or "")[:10]
    updated  = (fields.get("System.ChangedDate") or "")[:10]
    tags     = fields.get("System.Tags", "—") or "—"
    iteration = fields.get("System.IterationPath", "—")
    url      = f"{ADO_URL}/{ADO_PROJECT}/_workitems/edit/{wi_id}"

    return (
        f"\n{DIVIDER}\n"
        f"  [#{wi_id}] {title}\n"
        f"  URL:         {url}\n"
        f"  Tipo:        {wi_type}  |  Estado: {state}  |  Prioridad: {priority}\n"
        f"  Asignado a:  {assigned}\n"
        f"  Creado:      {created}  |  Actualizado: {updated}\n"
        f"  Iteración:   {iteration}\n"
        f"  Tags:        {tags}"
    )


# ── main ─────────────────────────────────────────────────────────────────────

def run_query(wiql: str):
    try:
        ids = run_wiql(wiql)
        total = len(ids)
        fetched_ids = ids[:MAX_RESULTS]
        work_items = fetch_work_items_batch(fetched_ids)

        print(f"\n✅ Resultados: {len(work_items)} de {total} work item(s) encontrado(s)")

        if not work_items:
            print("  (Sin resultados para esa consulta)")
            return

        for wi in work_items:
            print(format_work_item(wi))

        print(f"\n{DIVIDER}")

        if total > MAX_RESULTS:
            print(f"  ⚠️  Mostrando {MAX_RESULTS} de {total} resultados.")

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        if code == 401:
            print("❌ Error 401 — PAT inválido o expirado. Verifica ADO_PAT en .env.")
        elif code == 400:
            print(f"❌ Error 400 — WIQL inválido: {e}")
        elif code == 404:
            print(f"❌ Error 404 — Proyecto no encontrado. Verifica ADO_URL y ADO_PROJECT.")
        else:
            print(f"❌ HTTP Error {code}: {e}")
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {ADO_URL}. Verifica tu conexión y la URL.")
    except requests.exceptions.Timeout:
        print("❌ Timeout — La solicitud tardó demasiado.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def main():
    print("=" * 70)
    print(" Búsqueda de Work Items en Azure DevOps — WIQL Search")
    print(f" Organización: {ADO_URL}")
    print(f" Proyecto:     {ADO_PROJECT}")
    print("=" * 70)

    if len(sys.argv) > 1:
        wiql = " ".join(sys.argv[1:])
        print(f"\n  → Ejecutando: {wiql}")
        run_query(wiql)
        return

    ejemplos = [
        "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active' ORDER BY [System.ChangedDate] DESC",
        "SELECT [System.Id] FROM WorkItems WHERE [System.WorkItemType] = 'Bug' AND [System.State] <> 'Closed'",
        "SELECT [System.Id] FROM WorkItems WHERE [System.AssignedTo] = @Me ORDER BY [System.ChangedDate] DESC",
        "SELECT [System.Id] FROM WorkItems WHERE [System.IterationPath] = @CurrentIteration",
        "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active' AND [System.WorkItemType] = 'Task'",
    ]

    print("\nEjemplos de WIQL:")
    for i, ej in enumerate(ejemplos, 1):
        print(f"  {i}. {ej}")
    print("\nEscribe tu WIQL (o el número del ejemplo), o 'q' para salir.")

    while True:
        print()
        try:
            user_input = input("WIQL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if not user_input or user_input.lower() in ("q", "quit", "exit", "salir"):
            print("Saliendo...")
            break

        if user_input.isdigit() and 1 <= int(user_input) <= len(ejemplos):
            wiql = ejemplos[int(user_input) - 1]
            print(f"  → Ejecutando: {wiql}")
        else:
            wiql = user_input

        run_query(wiql)


if __name__ == "__main__":
    main()
