"""
Abre el link de confirmacion del correo que coincida con el asunto dado.

Uso:
  python extract_confirm_link.py                        # busca "confirm" en los ultimos 10 correos
  python extract_confirm_link.py --subject "Robin"      # filtra por asunto
  python extract_confirm_link.py --n 2                  # usa el correo #2 de la lista
"""
import argparse, re, webbrowser
import win32com.client

parser = argparse.ArgumentParser()
parser.add_argument("--subject", "-s", default=None, help="Texto a buscar en el asunto")
parser.add_argument("--n", "-n", type=int, default=None, help="Numero de correo (1-based) de la lista reciente")
parser.add_argument("--top", type=int, default=20, help="Cuantos correos recientes revisar")
args = parser.parse_args()

outlook = win32com.client.GetActiveObject("Outlook.Application")
ns = outlook.GetNamespace("MAPI")
inbox = ns.GetDefaultFolder(6)
items = inbox.Items
items.Sort("[ReceivedTime]", True)

# Recopilar correos recientes
emails = []
for item in items:
    if len(emails) >= args.top:
        break
    try:
        emails.append(item)
    except Exception:
        continue

# Seleccionar el correo objetivo
target = None
if args.n:
    idx = args.n - 1
    if 0 <= idx < len(emails):
        target = emails[idx]
    else:
        print(f"No existe correo #{args.n} (solo hay {len(emails)}).")
        exit(1)
elif args.subject:
    for m in emails:
        if re.search(args.subject, m.Subject, re.IGNORECASE):
            target = m
            break
    if not target:
        print(f"No se encontro ningun correo con asunto '{args.subject}'.")
        exit(1)
else:
    # Auto: primer correo que tenga un link con "confirm" en texto o URL
    for m in emails:
        html = m.HTMLBody
        pattern = re.compile(r'href="(https?://[^"]+)"[^>]*>([^<]{0,80})', re.IGNORECASE)
        for url, text in pattern.findall(html):
            if re.search(r'confirm', text.strip() + url, re.IGNORECASE):
                target = m
                break
        if target:
            break
    if not target:
        print("No se encontro ningun correo con link de confirmacion en los ultimos correos.")
        exit(1)

print(f"Correo: {target.Subject}")

# Extraer link de confirmacion
html = target.HTMLBody
pattern = re.compile(r'href="(https?://[^"]+)"[^>]*>([^<]{0,80})', re.IGNORECASE)
matches = pattern.findall(html)

confirm_link = None
for url, text in matches:
    if re.search(r'confirm', text.strip(), re.IGNORECASE):
        confirm_link = url
        print(f"Boton: [{text.strip()}]")
        break

if not confirm_link:
    # Fallback: cualquier link que contenga "confirm" en la URL
    all_links = re.findall(r'href="(https?://[^"]+)"', html)
    for url in all_links:
        if "confirm" in url.lower():
            confirm_link = url
            print(f"Link URL con 'confirm': {url}")
            break

if not confirm_link:
    # Fallback: primer link no-tracker del remitente
    sender_domain = target.SenderEmailAddress.split("@")[-1].lower() if "@" in target.SenderEmailAddress else ""
    all_links = re.findall(r'href="(https?://[^"]+)"', html)
    non_trackers = [u for u in all_links if "removebluelinks" not in u and "track" not in u.lower()]
    if non_trackers:
        confirm_link = non_trackers[0]
        print(f"Fallback primer link: {confirm_link}")

if confirm_link:
    print(f"\nAbriendo: {confirm_link}")
    webbrowser.open(confirm_link)
else:
    print("No se encontro ningun link de confirmacion.")
    exit(1)
