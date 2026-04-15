import requests, re, base64
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('dynamicdocs_user', 'eN88_4jpQC')
base = 'https://api-archwell.archeiotech.com'
auth_header = 'Basic ' + base64.b64encode(b'dynamicdocs_user:eN88_4jpQC').decode()
b64 = base64.b64encode(b'probe').decode()
hdrs = {'Authorization': auth_header, 'Content-Type': 'application/atom+xml'}

# List document subtypes in repo 2
r = requests.get(base+'/cmis/version/1.1/atom/2/types?typeId=cmis:document', auth=auth, timeout=10)
type_ids = re.findall(r'<cmis:id>([^<]+)', r.text)
type_names = re.findall(r'<cmis:displayName>([^<]+)', r.text)
print('Types in repo 2:')
for tid, tn in zip(type_ids, type_names):
    print(f'  {tid} | {tn}')

# Try upload with first available types
print('\nTesting upload to folder-2315 via repo 2:')
for obj_type in type_ids[:6]:
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<atom:entry xmlns:atom="http://www.w3.org/2005/Atom"
            xmlns:cmis="http://docs.oasis-open.org/ns/cmis/core/200908/"
            xmlns:cmisra="http://docs.oasis-open.org/ns/cmis/restatom/200908/">
  <atom:author><cmis:name>k6-probe</cmis:name></atom:author>
  <atom:id>urn:uuid:0</atom:id><atom:title/><atom:updated>2026-04-14T00:00:00Z</atom:updated>
  <cmisra:content><cmisra:mediatype>text/plain</cmisra:mediatype><cmisra:base64>{b64}</cmisra:base64></cmisra:content>
  <cmisra:object xmlns:ns3="http://docs.oasis-open.org/ns/cmis/messaging/200908/">
    <cmis:properties>
      <cmis:propertyString propertyDefinitionId="cmis:name"><cmis:value>k6-probe.txt</cmis:value></cmis:propertyString>
      <cmis:propertyId propertyDefinitionId="cmis:objectTypeId"><cmis:value>{obj_type}</cmis:value></cmis:propertyId>
    </cmis:properties>
  </cmisra:object>
</atom:entry>"""
    r2 = requests.post(base+'/cmis/version/1.1/atom/2/children?id=folder-2315', headers=hdrs, data=xml.encode(), timeout=15)
    if r2.status_code in (200, 201):
        new_ids = re.findall(r'cmis:objectId[^>]+>[^<]*<cmis:value>([^<]+)', r2.text)
        created = new_ids[0] if new_ids else '?'
        print(f'  {obj_type}: CREATED! id={created}')
        requests.delete(base+f'/cmis/version/1.1/atom/2/id?id={created}', auth=auth, timeout=10)
        break
    else:
        msg = r2.text[r2.text.find('<!--message-->')+14:r2.text.find('<!--/message-->')]
        print(f'  {obj_type}: {r2.status_code} — {msg[:100]}')
import requests, re
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('dynamicdocs_user', 'eN88_4jpQC')
base = 'https://api-archwell.archeiotech.com'

# List repos
r = requests.get(base+'/cmis/version/1.1/atom', auth=auth, timeout=10)
repos = re.findall(r'<atom:title>(\d+)</atom:title>', r.text)
print('Repos:', repos)

# Check folder-2315 via repo 2
for obj_id in ['department-209', 'cabinet-100722', 'folder-2315']:
    r2 = requests.get(base+f'/cmis/version/1.1/atom/2/id?id={obj_id}', auth=auth, timeout=10)
    names = re.findall(r'cmis:name[^>]+>[^<]*<cmis:value>([^<]+)', r2.text)
    nm = names[0] if names else '-'
    print(f'  repo2 / {obj_id}: {r2.status_code}  {nm}')

# Check document-577484 via repo 1
r3 = requests.get(base+'/cmis/version/1.1/atom/1/id?id=document-577484', auth=auth, timeout=10)
names3 = re.findall(r'cmis:name[^>]+>[^<]*<cmis:value>([^<]+)', r3.text)
nm3 = names3[0] if names3 else '-'
print(f'  repo1 / document-577484: {r3.status_code}  {nm3}')
