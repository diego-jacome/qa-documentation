import requests, re
from requests.auth import HTTPBasicAuth

BASE = 'https://api-staging.archeiotech.com'
REPO = '28'
auth = HTTPBasicAuth('quorum_user', 'Z?sqL3=HD0')

r = requests.get(f'{BASE}/cmis/version/1.1/atom/{REPO}/children?maxItems=20', auth=auth, timeout=15)
print('root children status:', r.status_code)
entries = r.text.split('<atom:entry')
for entry in entries[1:]:
    name_m = re.search(r'<atom:title[^>]*>([^<]+)</atom:title>', entry)
    id_m   = re.search(r'children\?id=(folder-\d+)', entry)
    if id_m:
        name = name_m.group(1) if name_m else '(unknown)'
        print(f'  {id_m.group(1)}  {name}')
