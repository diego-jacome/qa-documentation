"""
Outlook Send — Enviar y responder correos via Graph API
Uso:
  # Correo nuevo
  python outlook_send.py --to "user@company.com" --subject "Hola" --body "Mensaje"

  # Responder un correo existente
  python outlook_send.py --reply <message_id> --body "Mi respuesta"

  # Reply All
  python outlook_send.py --reply-all <message_id> --body "Mi respuesta"

  # Con CC
  python outlook_send.py --to "a@x.com" --cc "b@x.com" --subject "Test" --body "..."

  # Guardar como borrador (no enviar)
  python outlook_send.py --to "a@x.com" --subject "Draft" --body "..." --draft
"""
import argparse, json
import requests
from outlook_auth import get_token

GRAPH = 'https://graph.microsoft.com/v1.0'


def _headers():
    return {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json',
    }


def send_new(to: list[str], subject: str, body: str, cc: list[str] = None, draft=False):
    payload = {
        'message': {
            'subject': subject,
            'body': {'contentType': 'Text', 'content': body},
            'toRecipients': [{'emailAddress': {'address': a}} for a in to],
        }
    }
    if cc:
        payload['message']['ccRecipients'] = [{'emailAddress': {'address': a}} for a in cc]

    if draft:
        r = requests.post(f'{GRAPH}/me/messages', headers=_headers(),
                          data=json.dumps(payload['message']), timeout=30)
        r.raise_for_status()
        print(f"Borrador guardado. ID: {r.json()['id'][:40]}...")
    else:
        r = requests.post(f'{GRAPH}/me/sendMail', headers=_headers(),
                          data=json.dumps(payload), timeout=30)
        r.raise_for_status()
        print(f"Correo enviado a: {', '.join(to)}")


def reply(message_id: str, body: str, reply_all=False):
    endpoint = 'replyAll' if reply_all else 'reply'
    payload  = {'message': {}, 'comment': body}
    r = requests.post(
        f'{GRAPH}/me/messages/{message_id}/{endpoint}',
        headers=_headers(),
        data=json.dumps(payload),
        timeout=30,
    )
    r.raise_for_status()
    action = 'Reply All' if reply_all else 'Reply'
    print(f"{action} enviado correctamente.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enviar correos con Outlook')
    parser.add_argument('--to',        nargs='+', help='Destinatarios')
    parser.add_argument('--cc',        nargs='+', help='CC')
    parser.add_argument('--subject',   type=str)
    parser.add_argument('--body',      type=str, required=True)
    parser.add_argument('--reply',     type=str, help='ID del mensaje al que responder')
    parser.add_argument('--reply-all', type=str, dest='reply_all',
                        help='ID del mensaje para Reply All')
    parser.add_argument('--draft',     action='store_true', help='Guardar como borrador')
    args = parser.parse_args()

    if args.reply:
        reply(args.reply, args.body, reply_all=False)
    elif args.reply_all:
        reply(args.reply_all, args.body, reply_all=True)
    elif args.to:
        if not args.subject:
            parser.error("--subject es requerido para correos nuevos")
        send_new(args.to, args.subject, args.body, cc=args.cc, draft=args.draft)
    else:
        parser.error("Debes especificar --to, --reply, o --reply-all")
