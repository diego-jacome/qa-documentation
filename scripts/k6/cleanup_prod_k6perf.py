"""
cleanup_prod_k6perf.py
Busca y borra documentos k6perf-* de PROD folder-2315 via DD API
QUTI: 1000000009999996 (ProductionTest / Archwell)
"""
import requests, sys

BASE_URL  = 'https://api.ondemandquorum.com/documents/v1'
API_KEY   = '5d5edb41a057494783d7d2a9bf8177ab'
QUTI      = '1000000009999996'
FOLDER_ID = 2315
EMAIL     = 'dynamicdocs_user@archeiotech.com'

headers = {
    'Ocp-Apim-Subscription-Key': API_KEY,
    'quti':    QUTI,
    'email':   EMAIL,
    'Content-Type': 'application/json',
    'Accept':  'application/json',
}

# ── 1. Search k6perf docs by name (pagination via query params) ───────────────
print('Searching for k6perf documents via DD API /documents/search...')
all_ids = []
page = 1
page_size = 500
while True:
    body = {"match": {"documentName": "k6perf"}}
    params = {'pageNumber': page, 'pageSize': page_size}
    r = requests.post(BASE_URL + '/documents/search',
                      headers=headers, params=params, json=body, timeout=30)
    if r.status_code != 200:
        print(f'Search failed: {r.status_code} {r.text[:300]}')
        sys.exit(1)
    data = r.json()
    docs = data.get('matchingDocuments', [])
    if not docs:
        print(f'  page {page}: 0 docs — done.')
        break
    k6perf = [d for d in docs if str(d.get('name', '')).startswith('k6perf')]
    all_ids.extend([d['contentId'] for d in k6perf])
    print(f'  page {page}: {len(docs)} returned, {len(k6perf)} k6perf matched. '
          f'Sample names: {[d.get("name","?") for d in docs[:3]]}')
    if len(docs) < page_size:
        break
    page += 1

print(f'\nTotal k6perf docs to delete: {len(all_ids)}')
if not all_ids:
    print('Nothing to delete.')
    sys.exit(0)

print('Sample IDs:', all_ids[:5])
confirm = input('Proceed with soft delete? (y/N) ')
if confirm.lower() != 'y':
    print('Aborted.')
    sys.exit(0)

# ── 2. Soft-delete in batches of 100 (DELETE /documents?document_ids=...)  ────
deleted = 0
failed  = 0
batch_size = 100
del_headers = {k: v for k, v in headers.items()}

for i in range(0, len(all_ids), batch_size):
    batch = all_ids[i:i+batch_size]
    r = requests.delete(BASE_URL + '/documents',
                        headers=del_headers,
                        params={'document_ids': batch},
                        timeout=30)
    if r.status_code in (200, 204):
        deleted += len(batch)
        print(f'  Deleted batch {i//batch_size + 1}: {len(batch)} docs OK')
    else:
        failed += len(batch)
        print(f'  Batch {i//batch_size + 1} FAILED: {r.status_code} {r.text[:200]}')

print(f'\nDone — deleted: {deleted}, failed: {failed}')
