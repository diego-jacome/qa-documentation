"""Elimina un miembro de una lista de distribucion en Outlook COM."""
import sys
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

DL_NAME          = "OD-811 Email Ingestion Changes"
MEMBER_EMAIL_KEY = "ODAQA1@test-inbox.ondemandquorum.com"

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

# Buscar el miembro por email
member_to_remove = None
for i in range(1, dl_item.MemberCount + 1):
    try:
        m = dl_item.GetMember(i)
        if m.Address.lower() == MEMBER_EMAIL_KEY.lower():
            member_to_remove = m
            print(f"Encontrado: {m.Name} <{m.Address}>")
            break
    except Exception:
        pass

if not member_to_remove:
    print(f"ERROR: No se encontro '{MEMBER_EMAIL_KEY}' en la lista.")
    sys.exit(1)

# Eliminar y guardar
dl_item.RemoveMember(member_to_remove)
dl_item.Save()
print(f"OK — '{member_to_remove.Name}' eliminado de '{DL_NAME}'.")
print(f"Miembros restantes: {dl_item.MemberCount}")
