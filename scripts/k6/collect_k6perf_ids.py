"""
collect_k6perf_ids.py
Consulta la carpeta CMIS folder-2307 y guarda en un archivo todos los
document IDs que empiecen con k6perf-*, junto con sus nombres de archivo.

Output: scripts/k6/results/k6perf-ids-YYYY-MM-DD-HH-MM.txt
"""
import os, re, sys, argparse, requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import dotenv_values

parser = argparse.ArgumentParser()
parser.add_argument('--env', default='qa', choices=['qa', 'stg', 'prod'])
args = parser.parse_args()

env_file = os.path.join(os.path.dirname(__file__), '.env')
config   = dotenv_values(env_file)
prefix   = args.env.upper()

BASE_URL  = config.get(f'{prefix}_BASE_URL', 'https://api-qa.archeiotech.com')
REPO_ID   = config.get(f'{prefix}_REPO_ID', '63')
FOLDER_ID = config.get(f'{prefix}_FOLDER_ID', '2307')
USERNAME  = config.get(f'{prefix}_USERNAME', 'dynamicdocs_user')
PASSWORD  = config.get(f'{prefix}_PASSWORD', '')

auth     = HTTPBasicAuth(USERNAME, PASSWORD)
headers  = {'Accept': 'application/xml'}

ids      = []
skip     = 0
max_items = 200

print(f'Scanning folder-{FOLDER_ID} for k6perf-* documents...')

while True:
    url = (f'{BASE_URL}/cmis/version/1.1/atom/{REPO_ID}/children'
           f'?id=folder-{FOLDER_ID}&maxItems={max_items}&skipCount={skip}')
    r = requests.get(url, auth=auth, headers=headers, timeout=60)

    if r.status_code != 200:
        print(f'ERROR: status {r.status_code}', file=sys.stderr)
        sys.exit(1)

    body = r.text
    entries = body.split('<atom:entry')
    total_in_page = body.count('<atom:entry')

    found_in_page = 0
    for entry in entries:
        if 'k6perf' not in entry:
            continue
        # Extract document ID
        m_id   = re.search(r'content\?id=(document-\d+)', entry)
        # Extract filename
        m_name = re.search(r'<atom:title[^>]*>([^<]*k6perf[^<]*)</atom:title>', entry)
        if m_id:
            doc_id   = m_id.group(1)
            doc_name = m_name.group(1) if m_name else '(unknown)'
            ids.append((doc_id, doc_name))
            found_in_page += 1

    print(f'  page skip={skip}: {total_in_page} entries, {found_in_page} k6perf found')

    if total_in_page < max_items:
        break
    skip += max_items

print(f'\nTotal k6perf documents found: {len(ids)}')

# Save to file
ts       = datetime.now().strftime('%Y-%m-%d-%H-%M')
date_dir = datetime.now().strftime('%Y-%m-%d')
out_path = os.path.join('performance', 'cmis-api', date_dir, 'raw-data', f'k6perf-ids-{ts}.txt')
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'k6perf documents in QA folder-{FOLDER_ID} — captured {ts}\n')
    f.write(f'Total: {len(ids)}\n')
    f.write('-' * 60 + '\n')
    for doc_id, doc_name in ids:
        f.write(f'{doc_id}\t{doc_name}\n')

print(f'IDs saved to: {out_path}')
