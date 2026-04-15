import boto3, json, datetime, re
from urllib.parse import urlparse

HOURS_BACK = 168  # 7 dias

client = boto3.client('logs', region_name='us-west-2')
start_ms = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)).timestamp() * 1000)

LOG_GROUPS = [
    'qa-cmis-api-log-group',
    'QA-CMIS-Log-Group',
    'qa-cmis-api-iis-log-group',
    'cmis-qa-iis',
    'cmis-iis-log-group',
]

all_requests = []

for lg in LOG_GROUPS:
    try:
        response = client.filter_log_events(
            logGroupName=lg,
            startTime=start_ms,
            filterPattern='LoggingMiddleware "completed with status code"',
            limit=200,
        )
        events = response.get('events', [])
        for e in events:
            try:
                msg = json.loads(e['message'])
                url = msg.get('GetDisplayUrlContextRequest', '')
                path = urlparse(url).path if url else ''
                if path in ('/swagger/index.html', '/swagger/v1/swagger.json'):
                    continue
                all_requests.append({
                    'ts': e['timestamp'],
                    'lg': lg,
                    'status': msg.get('ResponseStatusCode', '?'),
                    'path': path,
                    'message': msg.get('message', ''),
                })
            except Exception:
                pass
        print(f'{lg}: {len(events)} eventos encontrados (antes de filtrar swagger)')
    except Exception as ex:
        print(f'{lg}: ERROR - {ex}')

all_requests.sort(key=lambda x: x['ts'])
last_100 = all_requests[-100:]

print(f'\nUltimas {len(last_100)} requests CMIS (sin health checks) en los ultimos 7 dias\n')
print(f"{'Timestamp (UTC)':<21} | {'Status':<6} | {'Log Group':<30} | Endpoint")
print('-' * 110)

for r in last_100:
    ts = datetime.datetime.fromtimestamp(r['ts']/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    m = re.search(r'Request took: (\d+ms)', r['message'])
    ms = m.group(1) if m else ''
    print(f"{ts} | {str(r['status']):<6} | {r['lg']:<30} | {ms:<8} {r['path']}")

if not last_100:
    print('No se encontraron requests CMIS reales en los ultimos 7 dias.')
    print('\nVerificando si hay ANY actividad en los log groups...')
    for lg in LOG_GROUPS:
        try:
            r = client.filter_log_events(logGroupName=lg, startTime=start_ms, limit=1)
            count = len(r.get('events', []))
            print(f'  {lg}: {count} eventos totales')
        except Exception as ex:
            print(f'  {lg}: ERROR - {ex}')


client = boto3.client('logs', region_name='us-west-2')

start_ms = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=HOURS_BACK)).timestamp() * 1000)

all_events = []
kwargs = {
    'logGroupName': LOG_GROUP,
    'startTime': start_ms,
    'filterPattern': 'LoggingMiddleware "completed with status code"',
    'limit': 100,
}

response = client.filter_log_events(**kwargs)
all_events.extend(response.get('events', []))

# Handle pagination to get up to 500 events (last ones)
while response.get('nextToken') and len(all_events) < 500:
    kwargs['nextToken'] = response['nextToken']
    response = client.filter_log_events(**kwargs)
    all_events.extend(response.get('events', []))

# Take last 100 sorted by time
all_events.sort(key=lambda e: e['timestamp'])
last_100 = all_events[-100:]

print(f'Ultimas {len(last_100)} requests en qa-cmis-api-log-group (ultimas {HOURS_BACK}h)\n')
print(f"{'Timestamp (UTC)':<21} | {'Status':<6} | {'Tiempo':<12} | Endpoint")
print('-' * 90)

for e in last_100:
    ts = datetime.datetime.fromtimestamp(e['timestamp']/1000, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    try:
        msg = json.loads(e['message'])
        url = msg.get('GetDisplayUrlContextRequest', '')
        status = msg.get('ResponseStatusCode', '?')
        path = urlparse(url).path if url else ''
        message_text = msg.get('message', '')
        m = re.search(r'Request took: (\d+ms)', message_text)
        ms = m.group(1) if m else ''
        # Excluir health checks del ELB en swagger
        if path == '/swagger/index.html':
            continue
        print(f'{ts} | {str(status):<6} | {ms:<12} | {path}')
    except Exception:
        print(ts, e['message'][:150])
