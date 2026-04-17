"""
Busca un correo en Enviados por fecha y subject, y lo guarda como template (.oft) en Outlook.
"""
import sys
import os
import win32com.client
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

SEARCH_SUBJECT = "Dynamic Docs Release 26.05"
SEARCH_DATE    = datetime(2026, 3, 24)  # March 24, 2026

# Carpeta donde guardar el template
TEMPLATE_DIR  = os.path.join(os.path.expanduser("~"), "Documents", "Outlook Templates")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

try:
    ol = win32com.client.GetActiveObject("Outlook.Application")
except Exception:
    print("ERROR: Outlook no esta abierto.")
    sys.exit(1)

ns = ol.GetNamespace("MAPI")
sent = ns.GetDefaultFolder(5)  # 5 = olFolderSentMail

print(f"Buscando en '{sent.Name}' — subject: '{SEARCH_SUBJECT}' — fecha: {SEARCH_DATE.strftime('%Y-%m-%d')}")
print()

found = None
for item in sent.Items:
    try:
        sent_on = item.SentOn
        # Comparar solo la fecha
        if (sent_on.year == SEARCH_DATE.year and
            sent_on.month == SEARCH_DATE.month and
            sent_on.day == SEARCH_DATE.day and
            SEARCH_SUBJECT.lower() in item.Subject.lower()):
            found = item
            break
    except Exception:
        pass

if not found:
    print(f"No se encontro ningun correo enviado el {SEARCH_DATE.strftime('%Y-%m-%d')} con subject '{SEARCH_SUBJECT}'.")
    sys.exit(1)

print(f"Encontrado:")
print(f"  Asunto : {found.Subject}")
print(f"  Para   : {found.To}")
print(f"  Fecha  : {found.SentOn.strftime('%Y-%m-%d %H:%M')}")
print()

# Guardar como .oft (Outlook Template)
safe_name = SEARCH_SUBJECT.replace(" ", "_").replace("/", "-").replace(":", "")
template_path = os.path.join(TEMPLATE_DIR, f"{safe_name}.oft")

found.SaveAs(template_path, 3)  # 3 = olTemplate (.oft)

print(f"Template guardado en:")
print(f"  {template_path}")
