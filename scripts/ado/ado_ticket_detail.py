#!/usr/bin/env python3
"""
ado_ticket_detail.py
Obtiene el detalle completo de un Work Item de Azure DevOps.

Uso:
    python ado_ticket_detail.py 1234
    python ado_ticket_detail.py          ← pide el ID interactivamente

Autenticacion:
    Requiere las siguientes variables en el archivo .env (en la misma carpeta):
        ADO_URL         — URL base de la organización (ej: https://dev.azure.com/mi-org)
        ADO_PROJECT     — Nombre del proyecto (ej: MyProject)
        ADO_PAT         — Personal Access Token de Azure DevOps
"""

import os
import sys
import textwrap
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(script_dir, ".env"))

ADO_URL     = os.getenv("ADO_URL", "").rstrip("/")
ADO_PROJECT = os.getenv("ADO_PROJECT", "")
ADO_PAT     = os.getenv("ADO_PAT", "")
API_VERSION = "7.1"

DIVIDER      = "─" * 70
THIN_DIVIDER = "·" * 70


# ── helpers ──────────────────────────────────────────────────────────────────

def build_auth():
    if not ADO_URL or not ADO_PROJECT or not ADO_PAT:
        print("❌  Faltan variables en el .env: ADO_URL, ADO_PROJECT y/o ADO_PAT.")
        sys.exit(1)
    return HTTPBasicAuth("", ADO_PAT), {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get(auth, headers, url, params=None):
    r = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
    if not r.ok:
        print(f"   ⚠  HTTP {r.status_code} → {url}")
        try:
            print("   ", r.json().get("message", r.json()))
        except Exception:
            print("   ", r.text)
        return None
    return r.json()


def safe(value, fallback="—"):
    return value if value not in (None, "", [], {}) else fallback


def strip_html(text: str) -> str:
    """Elimina tags HTML básicos para mostrar el texto plano."""
    import re
    # Reemplaza <br>, </p>, </div>, </li> por saltos de línea
    text = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", text, flags=re.IGNORECASE)
    # Reemplaza <li> por viñeta
    text = re.sub(r"<li[^>]*>", "  • ", text, flags=re.IGNORECASE)
    # Elimina todos los demás tags
    text = re.sub(r"<[^>]+>", "", text)
    # Colapsa líneas en blanco múltiples
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def print_section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ── secciones ────────────────────────────────────────────────────────────────

def print_basic_info(wi: dict):
    fields  = wi.get("fields", {})
    wi_id   = wi.get("id", "—")
    url     = f"{ADO_URL}/{ADO_PROJECT}/_workitems/edit/{wi_id}"

    title      = safe(fields.get("System.Title"))
    state      = safe(fields.get("System.State"))
    wi_type    = safe(fields.get("System.WorkItemType"))
    priority   = safe(fields.get("Microsoft.VSTS.Common.Priority"))
    reason     = safe(fields.get("System.Reason"))
    assigned   = (fields.get("System.AssignedTo") or {}).get("displayName", "Sin asignar")
    created_by = (fields.get("System.CreatedBy") or {}).get("displayName", "—")
    area_path  = safe(fields.get("System.AreaPath"))
    iteration  = safe(fields.get("System.IterationPath"))
    created    = safe(fields.get("System.CreatedDate", ""))[:10]
    updated    = safe(fields.get("System.ChangedDate", ""))[:10]
    tags       = safe(fields.get("System.Tags"))
    story_pts  = safe(fields.get("Microsoft.VSTS.Scheduling.StoryPoints"))
    effort     = safe(fields.get("Microsoft.VSTS.Scheduling.Effort"))
    original_estimate = safe(fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate"))
    remaining  = safe(fields.get("Microsoft.VSTS.Scheduling.RemainingWork"))
    completed  = safe(fields.get("Microsoft.VSTS.Scheduling.CompletedWork"))
    severity   = safe(fields.get("Microsoft.VSTS.Common.Severity"))
    acceptance = strip_html(fields.get("Microsoft.VSTS.Common.AcceptanceCriteria") or "") or "—"
    repro_steps = strip_html(fields.get("Microsoft.VSTS.TCM.ReproSteps") or "") or None

    print_section("📋  INFORMACIÓN BÁSICA")
    print(f"  ID:            #{wi_id}")
    print(f"  URL:           {url}")
    print(f"  Título:        {title}")
    print(f"  Tipo:          {wi_type}")
    print(f"  Estado:        {state}  (Razón: {reason})")
    print(f"  Prioridad:     {priority}")
    if severity != "—":
        print(f"  Severidad:     {severity}")
    print(f"  Asignado a:    {assigned}")
    print(f"  Creado por:    {created_by}")
    print(f"  Creado:        {created}  |  Actualizado: {updated}")
    print(f"  Área:          {area_path}")
    print(f"  Iteración:     {iteration}")
    print(f"  Tags:          {tags}")
    print(f"  Story Points:  {story_pts}")
    if effort != "—":
        print(f"  Esfuerzo:      {effort}")
    print(f"  Estimado:      {original_estimate}")
    print(f"  Restante:      {remaining}")
    print(f"  Completado:    {completed}")

    if acceptance != "—":
        print_section("✅  CRITERIOS DE ACEPTACIÓN")
        print(textwrap.indent(acceptance, "  "))

    if repro_steps:
        print_section("🐛  PASOS DE REPRODUCCIÓN")
        print(textwrap.indent(repro_steps, "  "))


def print_description(wi: dict):
    fields = wi.get("fields", {})
    desc   = fields.get("System.Description") or ""
    print_section("📝  DESCRIPCIÓN")
    if not desc:
        print("  (sin descripción)")
    else:
        print(textwrap.indent(strip_html(desc), "  "))


def print_relations(wi: dict):
    relations = wi.get("relations", [])
    if not relations:
        return

    # Separar por tipo de relación
    parents, children, related, attachments_rel, other = [], [], [], [], []
    for rel in relations:
        rel_type = rel.get("rel", "")
        url      = rel.get("url", "")
        attrs    = rel.get("attributes", {})
        name     = attrs.get("name", rel_type)
        comment  = attrs.get("comment", "")

        if "Hierarchy-Reverse" in rel_type:
            parents.append((name, url, comment))
        elif "Hierarchy-Forward" in rel_type:
            children.append((name, url, comment))
        elif rel_type == "AttachedFile":
            attachments_rel.append(rel)
        elif "Related" in rel_type or "Dependency" in rel_type:
            related.append((name, url, comment))
        else:
            other.append((name, url, comment))

    if parents:
        print_section(f"⬆️   PADRE / ÉPICA ({len(parents)})")
        for name, url, comment in parents:
            wi_id = url.split("/")[-1] if url else "—"
            print(f"  [{name}] #{wi_id}   {comment}")

    if children:
        print_section(f"⬇️   HIJOS / SUBTAREAS ({len(children)})")
        for name, url, comment in children:
            wi_id = url.split("/")[-1] if url else "—"
            print(f"  [{name}] #{wi_id}   {comment}")

    if related:
        print_section(f"🔀  VÍNCULOS RELACIONADOS ({len(related)})")
        for name, url, comment in related:
            wi_id = url.split("/")[-1] if url else "—"
            print(f"  [{name}] #{wi_id}   {comment}")

    if other:
        print_section(f"🔗  OTROS VÍNCULOS ({len(other)})")
        for name, url, comment in other:
            print(f"  [{name}] {url}   {comment}")

    return attachments_rel


def print_comments(auth, headers, wi_id: int):
    url  = f"{ADO_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}/comments?api-version={API_VERSION}-preview.3"
    data = get(auth, headers, url)
    if data is None:
        return
    comments = data.get("comments", [])
    total    = data.get("totalCount", 0)
    print_section(f"💬  COMENTARIOS ({total} total, mostrando {len(comments)})")
    if not comments:
        print("  (sin comentarios)")
        return
    for c in comments:
        author  = (c.get("createdBy") or {}).get("displayName", "—")
        created = (c.get("createdDate") or "—")[:10]
        text    = strip_html(c.get("text") or "")
        print(f"\n  [{created}] {author}:")
        print(textwrap.indent(text or "(vacío)", "    "))
        print(f"  {THIN_DIVIDER}")


def print_attachments(auth, headers, relations: list, wi_id: int, download: bool = True):
    attachments = [r for r in (relations or []) if r.get("rel") == "AttachedFile"]
    if not attachments:
        return

    print_section(f"📎  ADJUNTOS ({len(attachments)})")
    for att in attachments:
        url     = att.get("url", "")
        attrs   = att.get("attributes", {})
        name    = attrs.get("name", "archivo")
        size    = attrs.get("resourceSize", 0)
        size_kb = f"{size / 1024:.1f} KB" if size else "—"
        print(f"  📄 {name}  ({size_kb})")
        print(f"     {url}")

    if download:
        dest_folder = os.path.join(script_dir, "attachments", str(wi_id))
        os.makedirs(dest_folder, exist_ok=True)
        print_section(f"⬇️   DESCARGANDO ADJUNTOS → {dest_folder}")
        for att in attachments:
            url  = att.get("url", "")
            name = (att.get("attributes") or {}).get("name", "attachment")
            if not url:
                continue
            dest_path = os.path.join(dest_folder, name)
            try:
                r = requests.get(url, auth=auth, timeout=60, stream=True)
                if r.ok:
                    with open(dest_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    size_kb = os.path.getsize(dest_path) / 1024
                    print(f"  ✅ {name}  ({size_kb:.1f} KB)  →  {dest_path}")
                else:
                    print(f"  ❌ {name}  →  HTTP {r.status_code}")
            except Exception as e:
                print(f"  ❌ {name}  →  {e}")


def print_history(auth, headers, wi_id: int, max_entries: int = 15):
    url  = f"{ADO_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}/revisions?api-version={API_VERSION}&$top={max_entries}&$expand=fields"
    data = get(auth, headers, url)
    if data is None:
        return
    revisions = data.get("value", [])
    total     = data.get("count", len(revisions))

    print_section(f"📜  HISTORIAL DE CAMBIOS ({total} revisión(es), mostrando {len(revisions)})")
    if not revisions:
        print("  (sin historial)")
        return

    # Mostrar los campos que cambiaron entre revisiones
    TRACK_FIELDS = [
        "System.State", "System.AssignedTo", "System.Title",
        "Microsoft.VSTS.Common.Priority", "System.IterationPath",
    ]

    prev_fields: dict = {}
    for rev in revisions:
        fields   = rev.get("fields", {})
        rev_num  = fields.get("System.Rev", "—")
        changed  = (fields.get("System.ChangedDate") or "—")[:10]
        changed_by = (fields.get("System.ChangedBy") or {}).get("displayName", "—")

        changes = []
        for f in TRACK_FIELDS:
            old = prev_fields.get(f)
            new = fields.get(f)
            if isinstance(new, dict):
                new = new.get("displayName", new)
            if isinstance(old, dict):
                old = old.get("displayName", old)
            if old is not None and old != new:
                changes.append(f"{f.split('.')[-1]}: «{old}» → «{new}»")

        prev_fields = fields

        if changes:
            print(f"  [Rev {rev_num}] [{changed}] {changed_by}")
            for ch in changes:
                print(f"    · {ch}")


# ── main ─────────────────────────────────────────────────────────────────────

def fetch_ticket(wi_id: int):
    auth, headers = build_auth()

    url = (
        f"{ADO_URL}/{ADO_PROJECT}/_apis/wit/workitems/{wi_id}"
        f"?$expand=all&api-version={API_VERSION}"
    )
    data = get(auth, headers, url)
    if data is None:
        print(f"❌  No se pudo obtener el work item #{wi_id}.")
        return

    print(f"\n{'═' * 70}")
    print(f"  DETALLE DEL WORK ITEM — Azure DevOps")
    print(f"{'═' * 70}")

    print_basic_info(data)
    print_description(data)
    relations = print_relations(data) or []
    print_comments(auth, headers, wi_id)
    print_attachments(auth, headers, relations, wi_id)
    print_history(auth, headers, wi_id)

    print(f"\n{'═' * 70}\n")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lstrip("#")
    else:
        arg = input("Ingresa el ID del work item (ej: 1234): ").strip().lstrip("#")

    if not arg or not arg.isdigit():
        print("❌  ID inválido. Debe ser un número (ej: 1234).")
        sys.exit(1)

    try:
        fetch_ticket(int(arg))
    except requests.exceptions.ConnectionError:
        print("❌  No se pudo conectar. Verifica la URL y la red.")
    except requests.exceptions.Timeout:
        print("❌  Timeout al conectar a Azure DevOps.")
    except Exception as e:
        print(f"❌  Error inesperado: {e}")


if __name__ == "__main__":
    main()
