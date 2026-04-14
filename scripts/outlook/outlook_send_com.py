"""
Outlook Send (COM) — Envía correos directamente desde Outlook instalado
No requiere Azure AD ni permisos de admin. Requiere Outlook abierto.

Uso:
  # Correo nuevo
  python outlook_send_com.py --to "user@company.com" --subject "Hola" --body "Mensaje"

  # Responder un correo (necesitas el EntryID del mensaje original)
  python outlook_send_com.py --reply <entryID> --body "Mi respuesta"

  # Con CC
  python outlook_send_com.py --to "a@x.com" --cc "b@x.com" --subject "Test" --body "..."

  # Guardar como borrador (no enviar)
  python outlook_send_com.py --to "a@x.com" --subject "Draft" --body "..." --draft
"""
import argparse
import win32com.client


def get_outlook():
    """Conecta a la instancia de Outlook ya abierta. No crea una nueva."""
    try:
        return win32com.client.GetActiveObject("Outlook.Application")
    except Exception:
        raise RuntimeError("Outlook no está abierto. Ábrelo e intenta de nuevo.")


def send_new(to: list, subject: str, body: str, cc: list = None, draft=False):
    outlook = get_outlook()
    mail    = outlook.CreateItem(0)  # 0 = MailItem

    mail.To      = '; '.join(to)
    mail.Subject = subject
    mail.Body    = body
    if cc:
        mail.CC = '; '.join(cc)

    if draft:
        mail.Save()
        print(f"Borrador guardado: '{subject}'")
    else:
        mail.Send()
        print(f"Correo enviado a: {', '.join(to)}")


def reply_message(entry_id: str, body: str, reply_all=False):
    outlook = get_outlook()
    ns      = outlook.GetNamespace("MAPI")
    item    = ns.GetItemFromID(entry_id)

    reply = item.ReplyAll() if reply_all else item.Reply()
    reply.Body = body + "\n\n" + reply.Body
    reply.Send()

    action = "Reply All" if reply_all else "Reply"
    print(f"{action} enviado: '{item.Subject}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enviar correos con Outlook (COM)')
    parser.add_argument('--to',        nargs='+')
    parser.add_argument('--cc',        nargs='+')
    parser.add_argument('--subject',   type=str)
    parser.add_argument('--body',      type=str, required=True)
    parser.add_argument('--reply',     type=str, help='EntryID del mensaje a responder')
    parser.add_argument('--reply-all', type=str, dest='reply_all')
    parser.add_argument('--draft',     action='store_true')
    args = parser.parse_args()

    if args.reply:
        reply_message(args.reply, args.body, reply_all=False)
    elif args.reply_all:
        reply_message(args.reply_all, args.body, reply_all=True)
    elif args.to:
        if not args.subject:
            parser.error("--subject es requerido para correos nuevos")
        send_new(args.to, args.subject, args.body, cc=args.cc, draft=args.draft)
    else:
        parser.error("Debes especificar --to, --reply, o --reply-all")
