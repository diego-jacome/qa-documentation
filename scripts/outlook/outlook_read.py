"""
Outlook Read — Listar y leer correos via Graph API
Uso:
  python outlook_read.py                     # últimos 10 correos
  python outlook_read.py --top 20            # últimos 20
  python outlook_read.py --unread            # solo no leídos
  python outlook_read.py --today             # solo de hoy
  python outlook_read.py --id <message_id>   # cuerpo completo de un correo
  python outlook_read.py --important         # solo marcados como importantes
"""
import argparse, json, textwrap
from datetime import datetime, timezone
import requests
from outlook_auth import get_token

GRAPH = 'https://graph.microsoft.com/v1.0'


def list_messages(top=10, unread=False, today=False, important=False):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}

    filters = []
    if unread:
        filters.append('isRead eq false')
    if today:
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        filters.append(f'receivedDateTime ge {today_str}T00:00:00Z')
    if important:
        filters.append("importance eq 'high'")

    params = {
        '$top': top,
        '$orderby': 'receivedDateTime desc',
        '$select': 'id,subject,from,receivedDateTime,isRead,importance,bodyPreview',
    }
    if filters:
        params['$filter'] = ' and '.join(filters)

    r = requests.get(f'{GRAPH}/me/messages', headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get('value', [])


def get_message_body(message_id: str):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(
        f'{GRAPH}/me/messages/{message_id}',
        headers=headers,
        params={'$select': 'id,subject,from,receivedDateTime,body,toRecipients,ccRecipients'},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def print_messages(messages):
    if not messages:
        print("No se encontraron correos.")
        return
    print(f"\n{'='*70}")
    for i, m in enumerate(messages, 1):
        read_marker = '' if m['isRead'] else '[NO LEÍDO] '
        importance  = ' ⚡IMPORTANTE' if m.get('importance') == 'high' else ''
        from_addr   = m['from']['emailAddress']
        received    = m['receivedDateTime'][:16].replace('T', ' ')
        print(f"\n#{i} {read_marker}{importance}")
        print(f"  ID      : {m['id'][:40]}...")
        print(f"  De      : {from_addr['name']} <{from_addr['address']}>")
        print(f"  Asunto  : {m['subject']}")
        print(f"  Recibido: {received}")
        print(f"  Preview : {textwrap.shorten(m['bodyPreview'], width=100)}")
    print(f"\n{'='*70}")


def print_full_message(msg):
    from_addr = msg['from']['emailAddress']
    to_list   = [r['emailAddress']['address'] for r in msg.get('toRecipients', [])]
    received  = msg['receivedDateTime'][:16].replace('T', ' ')

    print(f"\n{'='*70}")
    print(f"De      : {from_addr['name']} <{from_addr['address']}>")
    print(f"Para    : {', '.join(to_list)}")
    print(f"Asunto  : {msg['subject']}")
    print(f"Recibido: {received}")
    print(f"{'-'*70}")

    # Extraer texto plano del body
    body_type    = msg['body']['contentType']
    body_content = msg['body']['content']
    if body_type == 'html':
        try:
            from html.parser import HTMLParser
            class _P(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                def handle_data(self, data):
                    self.text.append(data)
            p = _P()
            p.feed(body_content)
            body_content = '\n'.join(t.strip() for t in p.text if t.strip())
        except Exception:
            pass
    print(body_content)
    print(f"{'='*70}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Leer correos de Outlook')
    parser.add_argument('--top',       type=int, default=10)
    parser.add_argument('--unread',    action='store_true')
    parser.add_argument('--today',     action='store_true')
    parser.add_argument('--important', action='store_true')
    parser.add_argument('--id',        type=str, help='ID del mensaje para ver cuerpo completo')
    parser.add_argument('--json',      action='store_true', help='Output en JSON crudo')
    args = parser.parse_args()

    if args.id:
        msg = get_message_body(args.id)
        if args.json:
            print(json.dumps(msg, indent=2, ensure_ascii=False))
        else:
            print_full_message(msg)
    else:
        messages = list_messages(
            top=args.top,
            unread=args.unread,
            today=args.today,
            important=args.important,
        )
        if args.json:
            print(json.dumps(messages, indent=2, ensure_ascii=False))
        else:
            print_messages(messages)
