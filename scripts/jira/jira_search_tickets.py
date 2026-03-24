#!/usr/bin/env python3
"""
jira_search_tickets.py
Busca tickets en Jira via REST API usando JQL.

Uso:
    python jira_search_tickets.py
    python jira_search_tickets.py "sprint = '26.06' AND status = 'Ready for Testing'"

Autenticacion:
    Requiere las siguientes variables en el archivo .env (en la misma carpeta):
        JIRA_URL        — URL base de la instancia (ej: https://empresa.atlassian.net)
        JIRA_EMAIL      — Email de tu cuenta Jira
        JIRA_API_TOKEN  — API Token generado en https://id.atlassian.com/manage-profile/security/api-tokens

Ejemplos de JQL:
    project = "DD" AND status = "In Progress"
    assignee = currentUser() AND sprint in openSprints()
    issuetype = Bug AND priority = High AND created >= -7d
    text ~ "login error" ORDER BY created DESC
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL    = os.getenv("JIRA_URL", "https://archeiojira.atlassian.net").rstrip("/")
JIRA_EMAIL  = os.getenv("JIRA_EMAIL")
JIRA_TOKEN  = os.getenv("JIRA_API_TOKEN")
MAX_RESULTS = 50

FIELDS = [
    "summary", "status", "assignee", "priority",
    "issuetype", "created", "updated", "labels", "fixVersions",
]

DIVIDER = "─" * 70


# ── helpers ──────────────────────────────────────────────────────────────────

def build_auth():
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("❌  Faltan JIRA_EMAIL y/o JIRA_API_TOKEN en el entorno (.env).")
        sys.exit(1)
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN), {"Accept": "application/json"}


def search_jira(jql: str, max_results: int = MAX_RESULTS) -> dict:
    """Ejecuta una busqueda JQL en Jira y devuelve el JSON de respuesta."""
    auth, headers = build_auth()
    fields_csv = ",".join(FIELDS)

    attempts = []

    # 1) Jira Cloud nuevo
    url_v3 = f"{JIRA_URL}/rest/api/3/search/jql"
    r1 = requests.get(url_v3, headers=headers, auth=auth, timeout=30,
                      params={"jql": jql, "maxResults": max_results, "fields": fields_csv})
    if r1.ok:
        return r1.json()
    attempts.append(("v3/search/jql", r1))

    # 2) Fallback estable
    url_v2 = f"{JIRA_URL}/rest/api/2/search"
    r2 = requests.get(url_v2, headers=headers, auth=auth, timeout=30,
                      params={"jql": jql, "maxResults": max_results, "fields": fields_csv})
    if r2.ok:
        return r2.json()
    attempts.append(("v2/search", r2))

    details = []
    for name, resp in attempts:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        details.append(f"{name} -> {resp.status_code}: {body}")
    raise requests.exceptions.HTTPError(" | ".join(details), response=attempts[-1][1])


def format_issue(issue: dict) -> str:
    key    = issue.get("key", "N/A")
    fields = issue.get("fields", {})

    summary      = fields.get("summary", "")
    status       = (fields.get("status") or {}).get("name", "N/A")
    issue_type   = (fields.get("issuetype") or {}).get("name", "N/A")
    priority     = (fields.get("priority") or {}).get("name", "N/A") if fields.get("priority") else "N/A"
    assignee     = (fields.get("assignee") or {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned"
    created      = (fields.get("created") or "")[:10]
    updated      = (fields.get("updated") or "")[:10]
    labels       = ", ".join(fields.get("labels") or []) or "—"
    fix_versions = ", ".join(v.get("name", "") for v in (fields.get("fixVersions") or [])) or "—"
    url          = f"{JIRA_URL}/browse/{key}"

    return (
        f"\n{DIVIDER}\n"
        f"  [{key}] {summary}\n"
        f"  URL:         {url}\n"
        f"  Tipo:        {issue_type}  |  Estado: {status}  |  Prioridad: {priority}\n"
        f"  Asignado a:  {assignee}\n"
        f"  Creado:      {created}  |  Actualizado: {updated}\n"
        f"  Labels:      {labels}\n"
        f"  Fix Version: {fix_versions}"
    )


# ── main ─────────────────────────────────────────────────────────────────────

def run_query(jql: str):
    try:
        data    = search_jira(jql)
        total   = data.get("total", 0)
        issues  = data.get("issues", [])
        fetched = len(issues)

        print(f"\n✅ Resultados: {fetched} de {total} ticket(s) encontrado(s)")

        if not issues:
            print("  (Sin resultados para esa consulta)")
            return

        for issue in issues:
            print(format_issue(issue))

        print(f"\n{DIVIDER}")

        if total > fetched:
            print(f"  ⚠️  Mostrando {fetched} de {total} resultados. Ajusta MAX_RESULTS para ver mas.")

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        if code == 401:
            print("❌ Error 401 — Credenciales incorrectas. Verifica JIRA_EMAIL y JIRA_API_TOKEN en .env.")
        elif code == 400:
            print(f"❌ Error 400 — JQL invalido: {e}")
        else:
            print(f"❌ HTTP Error {code}: {e}")
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {JIRA_URL}. Verifica tu conexion y la URL.")
    except requests.exceptions.Timeout:
        print("❌ Timeout — La solicitud tardo demasiado.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def main():
    print("=" * 70)
    print(" Busqueda de tickets en Jira — JQL Search")
    print(f" Instancia: {JIRA_URL}")
    print("=" * 70)

    # Si se pasa JQL como argumento, ejecutar directamente
    if len(sys.argv) > 1:
        jql = " ".join(sys.argv[1:])
        print(f"\n  → Ejecutando: {jql}")
        run_query(jql)
        return

    # Modo interactivo
    ejemplos = [
        'sprint in openSprints() AND status = "Ready for Testing" ORDER BY priority ASC',
        'sprint in openSprints() AND status = "In Progress"',
        'issuetype = Bug AND created >= -7d ORDER BY created DESC',
        'assignee = currentUser() ORDER BY updated DESC',
        'text ~ "login" AND status != Done',
    ]

    print("\nEjemplos de JQL:")
    for i, ej in enumerate(ejemplos, 1):
        print(f"  {i}. {ej}")
    print("\nEscribe tu JQL (o el numero del ejemplo), o 'q' para salir.")

    while True:
        print()
        try:
            user_input = input("JQL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if not user_input or user_input.lower() in ("q", "quit", "exit", "salir"):
            print("Saliendo...")
            break

        if user_input.isdigit() and 1 <= int(user_input) <= len(ejemplos):
            jql = ejemplos[int(user_input) - 1]
            print(f"  → Ejecutando: {jql}")
        else:
            jql = user_input

        run_query(jql)


if __name__ == "__main__":
    main()
