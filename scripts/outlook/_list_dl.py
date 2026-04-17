"""Lista listas de distribucion desde Outlook COM."""
import sys
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

try:
    ol = win32com.client.GetActiveObject("Outlook.Application")
except Exception:
    print("ERROR: Outlook no esta abierto.")
    sys.exit(1)

ns = ol.GetNamespace("MAPI")
contacts = ns.GetDefaultFolder(10)  # olFolderContacts

dist_lists = []
for item in contacts.Items:
    if item.Class == 69:  # olDistributionList
        members = []
        for i in range(1, item.MemberCount + 1):
            try:
                m = item.GetMember(i)
                members.append({"name": m.Name, "address": m.Address})
            except Exception:
                pass
        dist_lists.append({
            "name": item.DLName,
            "count": item.MemberCount,
            "members": members,
        })

dist_lists.sort(key=lambda x: x["name"].lower())

if not dist_lists:
    print("No se encontraron listas de distribucion en Contactos.")
else:
    print(f"Se encontraron {len(dist_lists)} lista(s):\n")
    for dl in dist_lists:
        print(f"  [{dl['count']} miembros]  {dl['name']}")
        for m in dl["members"]:
            addr = m["address"] if m["address"] else "(sin email)"
            print(f"    - {m['name']} <{addr}>")
        print()
