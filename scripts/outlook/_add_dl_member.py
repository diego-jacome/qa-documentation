"""Agrega un miembro a una lista de distribucion en Outlook COM."""
import sys
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

DL_NAME       = "Regression Reports [DD Team]"
MEMBER_EMAIL  = "william.garcia@quorumsoftware.com"

try:
    ol = win32com.client.GetActiveObject("Outlook.Application")
except Exception:
    print("ERROR: Outlook no esta abierto.")
    sys.exit(1)

ns = ol.GetNamespace("MAPI")
contacts = ns.GetDefaultFolder(10)  # olFolderContacts

# Buscar la lista
dl_item = None
for item in contacts.Items:
    if item.Class == 69 and item.DLName == DL_NAME:
        dl_item = item
        break

if not dl_item:
    print(f"ERROR: No se encontro la lista '{DL_NAME}'.")
    sys.exit(1)

# Verificar que no exista ya
for i in range(1, dl_item.MemberCount + 1):
    try:
        m = dl_item.GetMember(i)
        if m.Address.lower() == MEMBER_EMAIL.lower():
            print(f"Ya existe '{MEMBER_EMAIL}' en la lista.")
            sys.exit(0)
    except Exception:
        pass

# Crear recipient y agregar
recipient = ol.Session.CreateRecipient(MEMBER_EMAIL)
recipient.Resolve()

if not recipient.Resolved:
    print(f"ADVERTENCIA: No se pudo resolver '{MEMBER_EMAIL}' en el GAL. Agregando de todas formas...")

dl_item.AddMember(recipient)
dl_item.Save()
print(f"OK — '{MEMBER_EMAIL}' agregado a '{DL_NAME}'.")
print(f"Miembros totales: {dl_item.MemberCount}")
