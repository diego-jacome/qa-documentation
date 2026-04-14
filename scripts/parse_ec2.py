import json, os

with open(os.path.join(os.environ['TEMP'], 'ec2.json'), encoding='utf-8-sig') as f:
    data = json.load(f)

instances = sorted([i for sub in data for i in sub], key=lambda x: (x.get('Name') or '').lower())
print(f'Total: {len(instances)} instancias corriendo\n')

keywords = ['cmis','cms','document','content','archei','alfresco','nuxeo','dd-','dyndoc','dynamic']
matches = [i for i in instances if any(k in (i.get('Name') or '').lower() for k in keywords)]

print('=== POSIBLES MATCHES ===')
for i in matches:
    print(f"  {i.get('Name','?'):<50} | {i.get('ID','?'):<20} | {i.get('PrivateIP') or '':<16} | {i.get('PublicIP') or ''}")

print('\n=== TODAS ===')
for i in instances:
    print(f"  {i.get('Name','(sin nombre)'):<50} | {i.get('ID','?'):<20} | {i.get('PrivateIP') or '':<16} | {i.get('PublicIP') or ''}")
