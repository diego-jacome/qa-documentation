"""
Verifica que una lista de tickets pertenecen a una versión/fix version de Jira.
"""
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv("scripts/jira/.env")

JIRA_URL       = os.getenv("JIRA_URL", "https://archeiojira.atlassian.net").rstrip("/")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

auth    = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

VERSION_ID   = "11429"
VERSION_NAME = "26.06"

TICKETS = [
    "DD-9013", "DD-8797", "DD-8758", "DD-8757", "DD-7573", "DD-4804",
    "DD-9014", "DD-9010", "DD-9020", "DD-9016",
]

print(f"Verificando tickets contra release {VERSION_NAME} (ID: {VERSION_ID})\n")

results = []
for ticket_id in TICKETS:
    url = f"{JIRA_URL}/rest/api/3/issue/{ticket_id}?fields=summary,fixVersions,status"
    r = requests.get(url, auth=auth, headers=headers, timeout=30)
    if not r.ok:
        results.append({"id": ticket_id, "summary": "ERROR", "fix_versions": [], "status": f"HTTP {r.status_code}", "match": False})
        continue

    data   = r.json()
    fields = data.get("fields", {})
    summary      = fields.get("summary", "—")
    fix_versions = [v.get("name", "") for v in fields.get("fixVersions", [])]
    status       = fields.get("status", {}).get("name", "—")
    match        = VERSION_NAME in fix_versions

    results.append({
        "id": ticket_id,
        "summary": summary,
        "fix_versions": fix_versions,
        "status": status,
        "match": match,
    })

# Mostrar resultado
col_w = 60
print(f"{'Ticket':<10} {'Match':<8} {'Status':<15} {'Fix Versions':<20} {'Summary'}")
print("-" * 120)
all_ok = True
for r in results:
    icon    = "✅" if r["match"] else "❌"
    fv      = ", ".join(r["fix_versions"]) if r["fix_versions"] else "(ninguna)"
    summary = r["summary"][:col_w]
    if not r["match"]:
        all_ok = False
    print(f"{r['id']:<10} {icon:<8} {r['status']:<15} {fv:<20} {summary}")

print()
if all_ok:
    print(f"✅ Todos los tickets están asignados al release {VERSION_NAME}.")
else:
    print(f"⚠️  Algunos tickets NO están en el release {VERSION_NAME}. Revisar los marcados con ❌.")
