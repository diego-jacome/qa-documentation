"""
Outlook Read (COM) — Lee correos directamente desde Outlook instalado
No requiere Azure AD ni permisos de admin. Requiere Outlook abierto.

Uso:
  python outlook_read_com.py                  # últimos 10 correos
  python outlook_read_com.py --top 20         # últimos 20
  python outlook_read_com.py --unread         # solo no leídos
  python outlook_read_com.py --today          # solo de hoy
  python outlook_read_com.py --important      # solo importantes
  python outlook_read_com.py --id <entryID>   # cuerpo completo
"""
import argparse, textwrap
from datetime import datetime, date
import win32com.client

IMPORTANCE_HIGH = 2


def get_outlook():
    """Conecta a la instancia de Outlook ya abierta. No crea una nueva."""
    try:
        return win32com.client.GetActiveObject("Outlook.Application")
    except Exception:
        raise RuntimeError("Outlook no está abierto. Ábrelo e intenta de nuevo.")


def get_inbox():
    outlook = get_outlook()
    ns      = outlook.GetNamespace("MAPI")
    return ns.GetDefaultFolder(6)  # 6 = Inbox


def list_messages(top=10, unread=False, today=False, important=False):
    inbox = get_inbox()
    items = inbox.Items
    items.Sort("[ReceivedTime]", True)  # más recientes primero

    results = []
    for item in items:
        if len(results) >= top:
            break
        try:
            if unread and item.UnRead is False:
                continue
            if today and item.ReceivedTime.date() != date.today():
                continue
            if important and item.Importance != IMPORTANCE_HIGH:
                continue
            results.append(item)
        except Exception:
            continue
    return results


def print_messages(messages):
    if not messages:
        print("No se encontraron correos.")
        return
    print(f"\n{'='*70}")
    for i, m in enumerate(messages, 1):
        read_marker = '[NO LEÍDO] ' if m.UnRead else ''
        importance  = ' ⚡IMPORTANTE' if m.Importance == IMPORTANCE_HIGH else ''
        received    = m.ReceivedTime.strftime('%Y-%m-%d %H:%M')
        preview     = textwrap.shorten(m.Body.replace('\n', ' '), width=100)
        print(f"\n#{i} {read_marker}{importance}")
        print(f"  EntryID : {m.EntryID[:40]}...")
        print(f"  De      : {m.SenderName} <{m.SenderEmailAddress}>")
        print(f"  Asunto  : {m.Subject}")
        print(f"  Recibido: {received}")
        print(f"  Preview : {preview}")
    print(f"\n{'='*70}")


def print_full_message(entry_id: str):
    outlook = get_outlook()
    ns      = outlook.GetNamespace("MAPI")
    item    = ns.GetItemFromID(entry_id)
    received = item.ReceivedTime.strftime('%Y-%m-%d %H:%M')
    print(f"\n{'='*70}")
    print(f"De      : {item.SenderName} <{item.SenderEmailAddress}>")
    print(f"Para    : {item.To}")
    print(f"Asunto  : {item.Subject}")
    print(f"Recibido: {received}")
    print(f"{'-'*70}")
    print(item.Body)
    print(f"{'='*70}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Leer correos de Outlook (COM)')
    parser.add_argument('--top',       type=int, default=10)
    parser.add_argument('--unread',    action='store_true')
    parser.add_argument('--today',     action='store_true')
    parser.add_argument('--important', action='store_true')
    parser.add_argument('--id',        type=str, help='EntryID del mensaje')
    args = parser.parse_args()

    if args.id:
        print_full_message(args.id)
    else:
        messages = list_messages(
            top=args.top,
            unread=args.unread,
            today=args.today,
            important=args.important,
        )
        print_messages(messages)
