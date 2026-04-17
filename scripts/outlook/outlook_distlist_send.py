"""
outlook_distlist_send.py — Lista listas de distribución de Outlook y envía correos a sus miembros.

Uso interactivo:
  python scripts/outlook/outlook_distlist_send.py

Uso directo (sin prompts):
  python scripts/outlook/outlook_distlist_send.py --list "Nombre de la lista" \
      --subject "Asunto" --body "Cuerpo del mensaje" [--html] [--draft] [--cc "a@x.com;b@x.com"]

Requisitos:
  - Outlook instalado y abierto
  - pip install pywin32
"""

import argparse
import sys
import textwrap
import win32com.client


# ── Outlook helpers ──────────────────────────────────────────────────────────

def get_outlook():
    try:
        return win32com.client.GetActiveObject("Outlook.Application")
    except Exception:
        raise RuntimeError("Outlook no está abierto. Ábrelo e intenta de nuevo.")


def get_distribution_lists():
    """Retorna lista de dicts con info de cada DistList en la carpeta Contactos."""
    ol = get_outlook()
    ns = ol.GetNamespace("MAPI")
    contacts_folder = ns.GetDefaultFolder(10)  # 10 = olFolderContacts

    dist_lists = []
    for item in contacts_folder.Items:
        if item.Class == 69:  # 69 = olDistributionList
            members = []
            for i in range(1, item.MemberCount + 1):
                try:
                    m = item.GetMember(i)
                    members.append({"name": m.Name, "address": m.Address})
                except Exception:
                    pass
            dist_lists.append({
                "name":    item.DLName,
                "count":   item.MemberCount,
                "members": members,
            })

    return sorted(dist_lists, key=lambda x: x["name"].lower())


def send_to_list(dist_list: dict, subject: str, body: str,
                 cc: list = None, is_html: bool = False, draft: bool = False):
    """Crea y envía (o guarda como borrador) un correo a todos los miembros de la lista."""
    ol = get_outlook()

    # Construir destinatarios desde los miembros de la lista
    addresses = [m["address"] for m in dist_list["members"] if m["address"]]
    if not addresses:
        print("ERROR: La lista no tiene miembros con dirección de correo válida.")
        sys.exit(1)

    mail = ol.CreateItem(0)  # 0 = MailItem
    mail.To      = "; ".join(addresses)
    mail.Subject = subject

    if is_html:
        mail.HTMLBody = body
    else:
        mail.Body = body

    if cc:
        mail.CC = "; ".join(cc)

    if draft:
        mail.Save()
        print(f"  Borrador guardado: '{subject}'")
        print(f"  Para: {len(addresses)} destinatario(s)")
    else:
        mail.Send()
        print(f"  Correo enviado a {len(addresses)} destinatario(s): '{subject}'")
        for addr in addresses:
            print(f"    → {addr}")


# ── Modo interactivo ─────────────────────────────────────────────────────────

def interactive_mode():
    print("\n=== Outlook — Envío a Lista de Distribución ===\n")

    # 1. Obtener listas
    print("Cargando listas de distribución desde Contactos...")
    try:
        lists = get_distribution_lists()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not lists:
        print("No se encontraron listas de distribución en tu carpeta de Contactos.")
        sys.exit(0)

    # 2. Mostrar listas disponibles
    print(f"\nListas encontradas ({len(lists)}):\n")
    for i, dl in enumerate(lists, 1):
        print(f"  [{i:2d}] {dl['name']}  ({dl['count']} miembros)")

    # 3. Seleccionar lista
    print()
    while True:
        raw = input("Selecciona el número de la lista (o 'q' para salir): ").strip()
        if raw.lower() == 'q':
            sys.exit(0)
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(lists):
                selected = lists[idx]
                break
            else:
                print(f"  Número inválido. Elige entre 1 y {len(lists)}.")
        except ValueError:
            print("  Entrada inválida. Ingresa un número.")

    # 4. Mostrar miembros
    print(f"\nMiembros de '{selected['name']}':")
    for m in selected["members"]:
        print(f"  → {m['name']} <{m['address']}>")

    confirm = input("\n¿Continuar con esta lista? [s/n]: ").strip().lower()
    if confirm != 's':
        print("Cancelado.")
        sys.exit(0)

    # 5. Asunto
    print()
    subject = input("Asunto: ").strip()
    if not subject:
        print("ERROR: El asunto no puede estar vacío.")
        sys.exit(1)

    # 6. CC opcional
    cc_raw = input("CC (opcional, separado por ';' — Enter para omitir): ").strip()
    cc_list = [x.strip() for x in cc_raw.split(';') if x.strip()] if cc_raw else []

    # 7. Formato del cuerpo
    fmt = input("Formato del cuerpo — [1] Texto plano  [2] HTML (default: 1): ").strip()
    is_html = fmt == '2'

    # 8. Cuerpo
    if is_html:
        print("Escribe el cuerpo HTML (termina con una línea que contenga solo 'FIN'):")
    else:
        print("Escribe el cuerpo del mensaje (termina con una línea que contenga solo 'FIN'):")

    lines = []
    while True:
        line = input()
        if line.strip() == 'FIN':
            break
        lines.append(line)
    body = "\n".join(lines)

    if not body.strip():
        print("ERROR: El cuerpo del mensaje no puede estar vacío.")
        sys.exit(1)

    # 9. Borrador o envío
    mode = input("\n¿Enviar ahora o guardar como borrador? [e=Enviar / d=Borrador]: ").strip().lower()
    draft = mode == 'd'

    # 10. Confirmación final
    print(f"\nResumen:")
    print(f"  Lista:    {selected['name']} ({selected['count']} miembros)")
    print(f"  Asunto:   {subject}")
    if cc_list:
        print(f"  CC:       {'; '.join(cc_list)}")
    print(f"  Formato:  {'HTML' if is_html else 'Texto plano'}")
    print(f"  Acción:   {'Guardar borrador' if draft else 'ENVIAR'}")

    go = input("\n¿Confirmar? [s/n]: ").strip().lower()
    if go != 's':
        print("Cancelado.")
        sys.exit(0)

    # 11. Enviar
    print()
    send_to_list(selected, subject, body, cc=cc_list, is_html=is_html, draft=draft)
    print("\nListo.")


# ── CLI (modo directo) ───────────────────────────────────────────────────────

def cli_mode():
    parser = argparse.ArgumentParser(
        description="Envía un correo a los miembros de una lista de distribución de Outlook."
    )
    parser.add_argument("--list",    required=True, help="Nombre exacto de la lista de distribución")
    parser.add_argument("--subject", required=True, help="Asunto del correo")
    parser.add_argument("--body",    required=True, help="Cuerpo del mensaje")
    parser.add_argument("--cc",      default="",    help="CC separado por ';'")
    parser.add_argument("--html",    action="store_true", help="Tratar el body como HTML")
    parser.add_argument("--draft",   action="store_true", help="Guardar como borrador en lugar de enviar")
    args = parser.parse_args()

    lists = get_distribution_lists()
    match = next((dl for dl in lists if dl["name"].lower() == args.list.lower()), None)

    if not match:
        available = "\n".join(f"  - {dl['name']}" for dl in lists)
        print(f"ERROR: No se encontró la lista '{args.list}'.\nListas disponibles:\n{available}")
        sys.exit(1)

    cc_list = [x.strip() for x in args.cc.split(';') if x.strip()] if args.cc else []

    print(f"Enviando a lista '{match['name']}' ({match['count']} miembros)...")
    send_to_list(match, args.subject, args.body, cc=cc_list,
                 is_html=args.html, draft=args.draft)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Si se pasan argumentos → modo CLI; si no → modo interactivo
    if len(sys.argv) > 1:
        cli_mode()
    else:
        interactive_mode()
