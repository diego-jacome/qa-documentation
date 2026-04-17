"""Lee el cuerpo HTML del template .oft guardado."""
import sys
import os
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

TEMPLATE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "Outlook Templates", "Dynamic_Docs_Release_26.05.oft")

try:
    ol = win32com.client.GetActiveObject("Outlook.Application")
except Exception:
    print("ERROR: Outlook no esta abierto.")
    sys.exit(1)

mail = ol.CreateItemFromTemplate(TEMPLATE_PATH)

print("=== SUBJECT ===")
print(mail.Subject)
print()
print("=== TO ===")
print(mail.To)
print()
print("=== BODY (HTML) ===")
print(mail.HTMLBody)
