"""
dd_api_logs.py
Consulta los últimos requests de DD API desde Application Insights (QA / STG / PROD).

Uso:
    python scripts/dd-api/dd_api_logs.py [--env qa|stg|prod] [--days N] [--limit N]
"""
import subprocess
import sys
import argparse
import requests
from urllib.parse import urlparse

APP_IDS = {
    'qa':   '18ed1843-beff-4b0f-8cff-6f3ddfcc0ff5',  # ai-dynamic-docs-api-test
    'stg':  '2b83f8fd-3d29-4471-bd89-7d5798c1fa90',  # ai-dynamic-docs-api-stg
    'prod': 'd406761d-32e1-490c-84cc-ef6d87c2bd14',  # ai-dynamic-docs-api-prod
}


def get_token():
    result = subprocess.check_output(
        'az account get-access-token --resource https://api.applicationinsights.io --query accessToken -o tsv',
        shell=True, stderr=subprocess.DEVNULL
    )
    return result.decode().strip()


def query_app_insights(token, kql_query, app_id=APP_IDS['qa']):
    r = requests.post(
        f'https://api.applicationinsights.io/v1/apps/{app_id}/query',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'query': kql_query},
        timeout=30
    )
    data = r.json()
    if 'error' in data:
        print('ERROR:', data['error']['message'])
        sys.exit(1)
    return data['tables'][0]


def main():
    parser = argparse.ArgumentParser(description='DD API — Application Insights logs')
    parser.add_argument('--env',   default='qa', choices=['qa', 'stg', 'prod'], help='Ambiente (default: qa)')
    parser.add_argument('--days',  type=int, default=7,   help='Cuántos días atrás buscar (default: 7)')
    parser.add_argument('--limit', type=int, default=50,  help='Máximo de resultados (default: 50)')
    parser.add_argument('--all',   action='store_true',   help='Incluir health checks (swagger, root)')
    parser.add_argument('--failures', action='store_true', help='Solo errores (resultCode >= 400)')
    args = parser.parse_args()

    app_id = APP_IDS[args.env]
    token = get_token()

    filters = [f'timestamp > ago({args.days}d)']
    if not args.all:
        filters.append("url !contains '/swagger'")
        filters.append("url !endswith '.net/'")
        filters.append("url !endswith '.net'")
    if args.failures:
        filters.append('toint(resultCode) >= 400')

    where_clause = '\n| where '.join(filters)

    query = f"""requests
| where {where_clause}
| project timestamp, name, url, resultCode, duration, success, client_IP
| order by timestamp desc
| take {args.limit}"""

    table = query_app_insights(token, query, app_id)
    rows = table['rows']

    if not rows:
        print('No se encontraron requests en el período especificado.')
        return

    label = 'reales' if not args.all else 'totales'
    print(f'\nUltimos {len(rows)} requests {label} — DD API {args.env.upper()} (últimos {args.days}d)\n')
    print(f"{'Timestamp':<22} | {'Path':<60} | {'Code':<6} | {'Duration':>9} | {'OK':<5} | IP")
    print('-' * 130)

    for row in rows:
        ts = str(row[0])[:19]
        url = str(row[2] or row[1] or '')
        try:
            path = urlparse(url).path or url
        except Exception:
            path = url
        path = ('…' + path[-58:]) if len(path) > 60 else path
        code = str(row[3])
        dur = f'{float(row[4]):.0f}ms' if row[4] is not None else ''
        ok = str(row[5])
        ip = str(row[6] or '')
        print(f'{ts:<22} | {path:<60} | {code:<6} | {dur:>9} | {ok:<5} | {ip}')

    print()


def detail_batch_download(days=30, limit=20, env='qa'):
    """Show last N batch-download requests with full trace detail."""
    app_id = APP_IDS.get(env, APP_IDS['qa'])
    token = get_token()

    # Get requests
    req_query = f"""requests
| where timestamp > ago({days}d)
| where url contains '/document-batches/batch-download'
| where toint(resultCode) != 400 or duration > 100
| project timestamp, operation_Id, resultCode, duration, client_City, client_CountryOrRegion, user_AuthenticatedId, user_Id
| order by timestamp desc
| take {limit}"""

    tbl = query_app_insights(token, req_query, app_id)
    cols = [c['name'] for c in tbl['columns']]
    rows = tbl['rows']

    print(f'\nUltimos {len(rows)} requests a /document-batches/batch-download — DD API {env.upper()} (últimos {days}d)\n')

    for i, row in enumerate(rows, 1):
        d = dict(zip(cols, row))
        ts = str(d['timestamp'])[:19]
        code = d['resultCode']
        dur = f"{float(d['duration']):.0f}ms" if d['duration'] else ''
        city = d.get('client_City') or '?'
        country = d.get('client_CountryOrRegion') or '?'
        uid = d.get('user_AuthenticatedId') or d.get('user_Id') or '(no user captured)'
        op_id = d['operation_Id']

        # Get key traces for this operation
        trace_query = f"""traces
| where operation_Id == '{op_id}'
| where message contains 'documentIds' or message contains 'emails'
       or message contains 'Started' or message contains 'Completed'
       or message contains 'Error' or message contains 'Exception'
| project timestamp, message
| order by timestamp asc"""
        try:
            t_tbl = query_app_insights(token, trace_query, app_id)
            traces = [r[1] for r in t_tbl['rows']]
        except Exception:
            traces = []

        ok_icon = '✅' if str(code) == '200' else '❌'
        print(f"{'─'*60}")
        print(f"  #{i:<3}  {ts}  |  {ok_icon} {code}  |  {dur}")
        print(f"  Origin  : {city}, {country}")
        print(f"  User    : {uid}")
        print(f"  Traces  :")
        for t in traces:
            print(f"    › {t.strip()}")
        if not traces:
            print("    (no traces found)")
        print()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'detail':
        # detail [days] [limit] [env]
        days  = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        env   = sys.argv[4] if len(sys.argv) > 4 else 'qa'
        detail_batch_download(days=days, limit=limit, env=env)
    else:
        main()
