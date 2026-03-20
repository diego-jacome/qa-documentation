#!/usr/bin/env python3
"""
jira_ticket_detail.py
Ingresa un ID de ticket Jira y obtiene toda la información relacionada.
Uso:
    python jira_ticket_detail.py DD-1234
    python jira_ticket_detail.py          ← pide el ID interactivamente
"""
import os
import sys
import textwrap
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_URL       = os.getenv("JIRA_URL", "https://archeiojira.atlassian.net").rstrip("/")
JIRA_EMAIL     = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

DIVIDER      = "─" * 70
THIN_DIVIDER = "·" * 70


# ── helpers ──────────────────────────────────────────────────────────────────

def build_auth():
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("❌  Faltan JIRA_EMAIL y/o JIRA_API_TOKEN en el entorno (.env).")
        sys.exit(1)
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN), {"Accept": "application/json"}


def get(auth, headers, url, params=None):
    """GET con manejo básico de errores."""
    r = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
    if not r.ok:
        print(f"   ⚠  HTTP {r.status_code} → {url}")
        try:
            print("   ", r.json().get("errorMessages") or r.json())
        except Exception:
            pass
        return None
    return r.json()


def safe(value, fallback="—"):
    return value if value not in (None, "", []) else fallback


def adf_to_text(node, indent=0):
    """Convierte nodos de Atlassian Document Format (ADF) a texto plano."""
    if node is None:
        return ""
    t = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")

    if t == "text":
        return text
    if t in ("paragraph", "blockquote"):
        inner = "".join(adf_to_text(c) for c in content)
        return inner + "\n"
    if t == "hardBreak":
        return "\n"
    if t == "heading":
        level = node.get("attrs", {}).get("level", 1)
        inner = "".join(adf_to_text(c) for c in content)
        return f"\n{'#' * level} {inner}\n"
    if t == "bulletList":
        return "".join("  • " + adf_to_text(c) for c in content)
    if t == "orderedList":
        return "".join(f"  {i+1}. " + adf_to_text(c) for i, c in enumerate(content))
    if t == "listItem":
        return "".join(adf_to_text(c) for c in content)
    if t == "codeBlock":
        inner = "".join(adf_to_text(c) for c in content)
        return f"\n```\n{inner}\n```\n"
    if t == "inlineCard":
        return node.get("attrs", {}).get("url", "")
    # fallback: recursivo
    return "".join(adf_to_text(c) for c in content)


def print_section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ── secciones ────────────────────────────────────────────────────────────────

def print_basic_info(issue):
    fields  = issue.get("fields", {})
    key     = issue.get("key", "")
    url     = f"{JIRA_URL}/browse/{key}"
    summary = safe(fields.get("summary"))

    status        = (fields.get("status") or {}).get("name", "—")
    issue_type    = (fields.get("issuetype") or {}).get("name", "—")
    priority      = (fields.get("priority") or {}).get("name", "—")
    resolution    = (fields.get("resolution") or {}).get("name", "Sin resolución")
    assignee_obj  = fields.get("assignee") or {}
    assignee      = assignee_obj.get("displayName", "Sin asignar")
    reporter_obj  = fields.get("reporter") or {}
    reporter      = reporter_obj.get("displayName", "—")
    created       = (fields.get("created") or "—")[:10]
    updated       = (fields.get("updated") or "—")[:10]
    due_date      = safe(fields.get("duedate"))
    labels        = ", ".join(fields.get("labels") or []) or "—"
    fix_versions  = ", ".join(v.get("name", "") for v in (fields.get("fixVersions") or []))  or "—"
    affects_vers  = ", ".join(v.get("name", "") for v in (fields.get("versions") or []))     or "—"
    components    = ", ".join(c.get("name", "") for c in (fields.get("components") or []))   or "—"
    environment   = safe(fields.get("environment"))

    # Time tracking
    tt            = fields.get("timetracking") or {}
    time_est      = safe(tt.get("originalEstimate"))
    time_spent    = safe(tt.get("timeSpent"))
    time_remain   = safe(tt.get("remainingEstimate"))

    # Story points (campo customfield_10016 en Jira Cloud moderno / Next-gen)
    story_points  = (
        fields.get("story_points")
        or fields.get("customfield_10016")
        or fields.get("customfield_10028")
        or "—"
    )

    print_section("📋  INFORMACIÓN BÁSICA")
    print(f"  Ticket:        {key}")
    print(f"  URL:           {url}")
    print(f"  Resumen:       {summary}")
    print(f"  Tipo:          {issue_type}")
    print(f"  Estado:        {status}")
    print(f"  Prioridad:     {priority}")
    print(f"  Resolución:    {resolution}")
    print(f"  Asignado a:    {assignee}")
    print(f"  Reportado por: {reporter}")
    print(f"  Creado:        {created}")
    print(f"  Actualizado:   {updated}")
    print(f"  Vencimiento:   {due_date}")
    print(f"  Etiquetas:     {labels}")
    print(f"  Componentes:   {components}")
    print(f"  Fix Versions:  {fix_versions}")
    print(f"  Afecta a:      {affects_vers}")
    print(f"  Entorno:       {environment}")
    print(f"  Story Points:  {story_points}")
    print(f"  Tiempo est.:   {time_est}")
    print(f"  Tiempo usado:  {time_spent}")
    print(f"  Tiempo rest.:  {time_remain}")


def print_description(issue):
    fields = issue.get("fields", {})
    desc   = fields.get("description")
    print_section("📝  DESCRIPCIÓN")
    if desc is None:
        print("  (sin descripción)")
    elif isinstance(desc, str):
        print(textwrap.indent(desc.strip(), "  "))
    else:
        # Atlassian Document Format
        text = adf_to_text(desc).strip()
        print(textwrap.indent(text or "(sin contenido)", "  "))


def print_sprint(issue):
    fields  = issue.get("fields", {})
    # El campo de sprint puede estar en customfield_10020
    sprints = fields.get("customfield_10020") or []
    if not sprints:
        return
    print_section("🏃  SPRINT")
    for sp in sprints:
        if not isinstance(sp, dict):
            continue
        print(f"  Nombre:  {sp.get('name', '—')}")
        print(f"  Estado:  {sp.get('state', '—')}")
        start = (sp.get("startDate") or "—")[:10]
        end   = (sp.get("endDate")   or "—")[:10]
        print(f"  Período: {start} → {end}")
        print(THIN_DIVIDER)


def print_parent_epic(issue):
    fields = issue.get("fields", {})
    parent = fields.get("parent")
    epic   = fields.get("customfield_10014")  # Epic Link (company-managed)

    if parent or epic:
        print_section("🔗  ÉPICA / PADRE")
    if parent and isinstance(parent, dict):
        pk = parent.get("key", "—")
        ps = parent.get("fields", {}).get("summary", "—")
        pt = parent.get("fields", {}).get("issuetype", {}).get("name", "—")
        print(f"  [{pk}] ({pt}) {ps}")
    if epic:
        print(f"  Epic Link: {epic}")


def print_subtasks(issue):
    fields   = issue.get("fields", {})
    subtasks = fields.get("subtasks") or []
    if not subtasks:
        return
    print_section(f"🔽  SUBTAREAS ({len(subtasks)})")
    for sub in subtasks:
        sk  = sub.get("key", "—")
        ss  = sub.get("fields", {}).get("status", {}).get("name", "—")
        sm  = sub.get("fields", {}).get("summary", "—")
        print(f"  [{sk}] [{ss}] {sm}")


def print_linked_issues(issue):
    fields = issue.get("fields", {})
    links  = fields.get("issuelinks") or []
    if not links:
        return
    print_section(f"🔀  ISSUES VINCULADOS ({len(links)})")
    for link in links:
        link_type = (link.get("type") or {}).get("name", "—")
        direction = "outward" if "outwardIssue" in link else "inward"
        related   = link.get("outwardIssue") or link.get("inwardIssue") or {}
        rk        = related.get("key", "—")
        rs        = related.get("fields", {}).get("status", {}).get("name", "—")
        rm        = related.get("fields", {}).get("summary", "—")
        arrow     = "→" if direction == "outward" else "←"
        print(f"  {arrow} [{link_type}]  [{rk}] [{rs}] {rm}")


def print_comments(auth, headers, issue_key, max_comments=20):
    url  = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
    data = get(auth, headers, url, params={"maxResults": max_comments, "orderBy": "created"})
    if data is None:
        return
    comments = data.get("comments", [])
    total    = data.get("total", 0)
    print_section(f"💬  COMENTARIOS ({total} total, mostrando {len(comments)})")
    if not comments:
        print("  (sin comentarios)")
        return
    for c in comments:
        author  = (c.get("author") or {}).get("displayName", "—")
        created = (c.get("created") or "—")[:10]
        body    = c.get("body")
        if isinstance(body, str):
            text = body.strip()
        else:
            text = adf_to_text(body).strip()
        print(f"\n  [{created}] {author}:")
        print(textwrap.indent(text or "(vacío)", "    "))
        print(f"  {THIN_DIVIDER}")


def print_attachments(issue):
    fields      = issue.get("fields", {})
    attachments = fields.get("attachment") or []
    if not attachments:
        return
    print_section(f"📎  ADJUNTOS ({len(attachments)})")
    for att in attachments:
        name    = att.get("filename", "—")
        size    = att.get("size", 0)
        author  = (att.get("author") or {}).get("displayName", "—")
        created = (att.get("created") or "—")[:10]
        url     = att.get("content", "—")
        size_kb = f"{size / 1024:.1f} KB" if size else "—"
        print(f"  📄 {name}  ({size_kb})  subido por {author} el {created}")
        print(f"     {url}")


def download_attachments(auth, headers, issue):
    """Descarga todos los adjuntos del ticket a attachments/<TICKET-ID>/"""
    fields      = issue.get("fields", {})
    attachments = fields.get("attachment") or []
    if not attachments:
        return

    ticket_id   = issue.get("key", "UNKNOWN")
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    dest_folder = os.path.join(script_dir, "attachments", ticket_id)
    os.makedirs(dest_folder, exist_ok=True)

    print_section(f"⬇️   DESCARGANDO ADJUNTOS → {dest_folder}")
    for att in attachments:
        name = att.get("filename", "attachment")
        url  = att.get("content")
        if not url:
            print(f"  ⚠  Sin URL para: {name}")
            continue
        dest_path = os.path.join(dest_folder, name)
        try:
            r = requests.get(url, headers=headers, auth=auth, timeout=60, stream=True)
            if r.ok:
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                size_kb = os.path.getsize(dest_path) / 1024
                print(f"  ✅ {name}  ({size_kb:.1f} KB)")
                print(f"     {dest_path}")
            else:
                print(f"  ❌ {name}  →  HTTP {r.status_code}")
        except Exception as e:
            print(f"  ❌ {name}  →  {e}")


def print_changelog(auth, headers, issue_key, max_entries=15):
    url  = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/changelog"
    data = get(auth, headers, url, params={"maxResults": max_entries})
    if data is None:
        return
    entries = data.get("values", [])
    total   = data.get("total", 0)
    print_section(f"📜  HISTORIAL DE CAMBIOS ({total} total, mostrando {len(entries)})")
    if not entries:
        print("  (sin historial)")
        return
    for entry in reversed(entries):
        author  = (entry.get("author") or {}).get("displayName", "—")
        created = (entry.get("created") or "—")[:10]
        items   = entry.get("items", [])
        for item in items:
            field    = item.get("field", "—")
            from_val = item.get("fromString") or "—"
            to_val   = item.get("toString")   or "—"
            print(f"  [{created}] {author}  ·  {field}: «{from_val}» → «{to_val}»")


# ── main ─────────────────────────────────────────────────────────────────────

def fetch_ticket(ticket_id: str):
    auth, headers = build_auth()

    # Campos a solicitar (ampliado)
    fields = ",".join([
        "summary", "description", "status", "issuetype", "priority",
        "resolution", "assignee", "reporter", "created", "updated",
        "duedate", "labels", "components", "fixVersions", "versions",
        "environment", "timetracking", "story_points",
        "customfield_10016", "customfield_10028",  # story points
        "customfield_10014",                        # epic link
        "customfield_10020",                        # sprint
        "parent", "subtasks", "issuelinks", "attachment",
    ])

    url  = f"{JIRA_URL}/rest/api/3/issue/{ticket_id}"
    data = get(auth, headers, url, params={"fields": fields, "expand": "changelog"})

    if data is None:
        print(f"❌  No se pudo obtener el ticket «{ticket_id}».")
        return

    print(f"\n{'═' * 70}")
    print(f"  DETALLE DEL TICKET JIRA")
    print(f"{'═' * 70}")

    print_basic_info(data)
    print_description(data)
    print_sprint(data)
    print_parent_epic(data)
    print_subtasks(data)
    print_linked_issues(data)
    print_attachments(data)
    print_comments(auth, headers, ticket_id)
    print_changelog(auth, headers, ticket_id)
    download_attachments(auth, headers, data)

    print(f"\n{'═' * 70}\n")


def main():
    if len(sys.argv) > 1:
        ticket_id = sys.argv[1].strip().upper()
    else:
        ticket_id = input("Ingresa el ID del ticket (ej: DD-1234): ").strip().upper()

    if not ticket_id:
        print("❌  ID de ticket vacío.")
        sys.exit(1)

    try:
        fetch_ticket(ticket_id)
    except requests.exceptions.ConnectionError:
        print("❌  No se pudo conectar (verifica la URL y la red).")
    except requests.exceptions.Timeout:
        print("❌  Timeout al conectar a Jira.")
    except Exception as e:
        print(f"❌  Error inesperado: {e}")


if __name__ == "__main__":
    main()
