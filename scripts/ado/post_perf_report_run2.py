"""
post_perf_report_run2.py
1. Sube cmis-requests-2026-04-14-12-25.ndjson como adjunto al work item 1796375
2. Publica comentario HTML con los resultados de la Run 2
"""
import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(r'C:\Users\diego.jacome\Repos\qa-documentation\scripts\ado\.env')
ADO_URL     = os.getenv('ADO_URL').rstrip('/')
ADO_PROJECT = os.getenv('ADO_PROJECT')
ADO_PAT     = os.getenv('ADO_PAT')
auth        = HTTPBasicAuth('', ADO_PAT)

WORK_ITEM_ID = 1796375
NDJSON_PATH  = r'C:\Users\diego.jacome\Repos\qa-documentation\scripts\k6\results\cmis-requests-2026-04-14-12-25.ndjson'
FILE_NAME    = 'cmis-requests-run2-2026-04-14.ndjson'

# ── 1. Upload attachment ──────────────────────────────────────────────────────
print('Uploading NDJSON attachment...')
upload_url = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/attachments?fileName={FILE_NAME}&api-version=7.1'
with open(NDJSON_PATH, 'rb') as f:
    r = requests.post(upload_url, auth=auth,
                      headers={'Content-Type': 'application/octet-stream'},
                      data=f, timeout=120)

if r.status_code not in (200, 201):
    print(f'ERROR uploading attachment: {r.status_code} {r.text[:300]}')
    exit(1)

attachment_url = r.json()['url']
attachment_id  = r.json()['id']
print(f'Attachment uploaded: id={attachment_id}')
print(f'  URL: {attachment_url}')

# ── 2. Link attachment to work item ──────────────────────────────────────────
print('Linking attachment to work item...')
patch_url = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/workItems/{WORK_ITEM_ID}?api-version=7.1'
patch_body = [{
    'op': 'add',
    'path': '/relations/-',
    'value': {
        'rel': 'AttachedFile',
        'url': attachment_url,
        'attributes': {'comment': 'k6 raw requests NDJSON - Performance Test Run 2 (April 14 2026)'}
    }
}]
r = requests.patch(patch_url, auth=auth,
                   headers={'Content-Type': 'application/json-patch+json'},
                   json=patch_body, timeout=30)
if r.status_code in (200, 201):
    print('Attachment linked to work item OK')
else:
    print(f'WARNING: link failed {r.status_code} — continuing anyway')

# ── 3. Build HTML comment with download link ──────────────────────────────────
# ADO attachment direct link format for VSTS:
wi_attachment_link = (
    f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/attachments/{attachment_id}?fileName={FILE_NAME}&download=true&api-version=7.1'
)

comment = f"""<h2 style="color:#0078D4; border-bottom:2px solid #0078D4; padding-bottom:6px">Performance Test Report &#8212; CMIS API &nbsp;|&nbsp; Run 2</h2>

<p><strong>Date:</strong> April 14, 2026 &nbsp;|&nbsp; <strong>Environment:</strong> QA &#8212; Tenant: OnDemandQA1 &nbsp;|&nbsp; <strong>Tool:</strong> k6 v1.7.1</p>

<h3 style="margin-top:20px">&#128736; Test Configuration</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Parameter</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Concurrent Users (VUs)</td><td style="border:1px solid #d2d0ce; padding:8px">5</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Iterations per User</td><td style="border:1px solid #d2d0ce; padding:8px">100</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Iterations</td><td style="border:1px solid #d2d0ce; padding:8px">500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Document Size</td><td style="border:1px solid #d2d0ce; padding:8px">3 MB</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Duration</td><td style="border:1px solid #d2d0ce; padding:8px">7 min 23 sec</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Data Sent</td><td style="border:1px solid #d2d0ce; padding:8px">2.1 GB</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Data Received</td><td style="border:1px solid #d2d0ce; padding:8px">1.6 GB</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Raw Requests File</td><td style="border:1px solid #d2d0ce; padding:8px"><a href="{wi_attachment_link}">{FILE_NAME}</a> (7 MB, 1500 requests)</td></tr>
</table>

<h3 style="margin-top:20px">&#128202; Results by Endpoint</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px">Endpoint</th>
    <th style="border:1px solid #d2d0ce; padding:8px">Action</th>
    <th style="border:1px solid #d2d0ce; padding:8px">avg</th>
    <th style="border:1px solid #d2d0ce; padding:8px">median</th>
    <th style="border:1px solid #d2d0ce; padding:8px">p(90)</th>
    <th style="border:1px solid #d2d0ce; padding:8px">p(95)</th>
    <th style="border:1px solid #d2d0ce; padding:8px">max</th>
    <th style="border:1px solid #d2d0ce; padding:8px">vs Run 1 avg</th>
    <th style="border:1px solid #d2d0ce; padding:8px">Result</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>createDocument</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Uploaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.85s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.66s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">3.34s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">3.75s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">10.9s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:#666">+0.19s (+7%)</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Downloaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.02s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">932ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.38s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.54s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">6.77s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green">-0.15s (-13%)</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Viewed</td>
    <td style="border:1px solid #d2d0ce; padding:8px">475ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">434ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">696ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">819ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.56s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:#666">+21ms (+5%)</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
</table>

<h3 style="margin-top:20px">&#9989; Reliability Summary</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Metric</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Run 2</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Run 1</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Requests</td><td style="border:1px solid #d2d0ce; padding:8px">1,500</td><td style="border:1px solid #d2d0ce; padding:8px">1,500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Successful Requests</td><td style="border:1px solid #d2d0ce; padding:8px">1,500 (100%)</td><td style="border:1px solid #d2d0ce; padding:8px">1,500 (100%)</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Error Rate</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">0.00%</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">0.00%</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Throughput</td><td style="border:1px solid #d2d0ce; padding:8px">3.39 req/s</td><td style="border:1px solid #d2d0ce; padding:8px">&#8776;3.25 req/s</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Duration</td><td style="border:1px solid #d2d0ce; padding:8px">7 min 23 sec</td><td style="border:1px solid #d2d0ce; padding:8px">7 min 26 sec</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">All Thresholds</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASSED</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASSED</td></tr>
</table>

<h3 style="margin-top:20px; color:#0078D4">&#128313; Verdict</h3>
<p style="background:#ddf3ff; padding:12px; border-left:4px solid #0078D4">
  Results are <strong>consistent with Run 1</strong>. Variance across all endpoints stays within normal range (&#177;13%). Zero errors in both runs confirm the API handles 5 concurrent users uploading 100 files of 3MB with no degradation. <strong>Performance is stable and reproducible.</strong>
</p>"""

# ── 4. Post comment ───────────────────────────────────────────────────────────
print('Posting comment...')
base     = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/workItems/{WORK_ITEM_ID}/comments'
comments = requests.get(base + '?api-version=7.1-preview.3', auth=auth, timeout=15).json().get('comments', [])
target   = next((c for c in comments if 'Run 2' in c.get('text', '') and 'Performance Test Report' in c.get('text', '')), None)

if target:
    url = f"{base}/{target['id']}?api-version=7.1-preview.3"
    r = requests.patch(url, auth=auth, json={'text': comment},
                       headers={'Content-Type': 'application/json'}, timeout=30)
else:
    url = base + '?api-version=7.1-preview.3'
    r = requests.post(url, auth=auth, json={'text': comment},
                      headers={'Content-Type': 'application/json'}, timeout=30)

print(f'Status: {r.status_code}')
if r.status_code in (200, 201):
    print(f'Comment OK — ID: {r.json().get("id")}')
else:
    print(f'Error: {r.text[:500]}')
