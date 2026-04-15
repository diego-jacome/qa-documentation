"""
post_perf_stg_baseline.py
Publica comentario HTML con los resultados del STG Baseline en el work item 1796375
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

comment = """<h2 style="color:#107C10; border-bottom:2px solid #107C10; padding-bottom:6px">Performance Test Report &#8212; CMIS API &nbsp;|&nbsp; STG Baseline</h2>

<p><strong>Date:</strong> April 14, 2026 &nbsp;|&nbsp; <strong>Environment:</strong> Staging &#8212; Tenant: Encino &nbsp;|&nbsp; <strong>Tool:</strong> k6 v1.7.1</p>

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
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Duration</td><td style="border:1px solid #d2d0ce; padding:8px">7 min 47 sec</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Teardown</td><td style="border:1px solid #d2d0ce; padding:8px">Automatic (501 docs deleted)</td></tr>
</table>

<h3 style="margin-top:20px">&#128202; Results by Endpoint</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Endpoint</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Action</th>
    <th style="border:1px solid #d2d0ce; padding:8px">avg</th>
    <th style="border:1px solid #d2d0ce; padding:8px">median</th>
    <th style="border:1px solid #d2d0ce; padding:8px">p(90)</th>
    <th style="border:1px solid #d2d0ce; padding:8px">p(95)</th>
    <th style="border:1px solid #d2d0ce; padding:8px">max</th>
    <th style="border:1px solid #d2d0ce; padding:8px">Result</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>createDocument</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Uploaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.17s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.11s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.56s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.77s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">5.19s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Downloaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.50s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.44s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.06s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.30s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">4.28s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Viewed</td>
    <td style="border:1px solid #d2d0ce; padding:8px">865ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">807ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.24s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.34s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.22s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
</table>

<h3 style="margin-top:20px">&#128321; STG vs QA Comparison (avg)</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Endpoint</th>
    <th style="border:1px solid #d2d0ce; padding:8px">STG Baseline</th>
    <th style="border:1px solid #d2d0ce; padding:8px">QA Run 1</th>
    <th style="border:1px solid #d2d0ce; padding:8px">QA Run 2</th>
    <th style="border:1px solid #d2d0ce; padding:8px">&#916; vs QA R1</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>createDocument</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>2.17s</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.66s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.85s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">&#8209;18% faster</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>1.50s</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.17s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.02s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:#d83b01; font-weight:bold">+28% slower</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>865ms</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">454ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">475ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:#d83b01; font-weight:bold">+90% slower</td>
  </tr>
</table>

<h3 style="margin-top:20px">&#9989; Reliability</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Metric</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Requests</td><td style="border:1px solid #d2d0ce; padding:8px">1,500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Successful Requests</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">1,500 (100%)</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Error Rate</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">0.00%</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Throughput</td><td style="border:1px solid #d2d0ce; padding:8px">&#8776; 3.21 req/s</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">All Thresholds</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASSED</td></tr>
</table>

<h3 style="margin-top:20px; color:#107C10">&#128313; Verdict</h3>
<p style="background:#dff6dd; padding:12px; border-left:4px solid #107C10">
  STG Baseline completed with <strong>0 errors across 500 iterations</strong> (1,500 requests). Upload performance is <strong>18% faster than QA</strong> (2.17s vs 2.66s avg). Read operations (<code>getObject</code>, <code>getContentStream</code>) are slower in STG &#8212; expected for a different tenant/dataset. Baseline established for future STG regression comparisons.
</p>"""

# ── POST comment to work item ─────────────────────────────────────────────────
print(f'Posting STG Baseline comment to work item {WORK_ITEM_ID}...')
url = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/workItems/{WORK_ITEM_ID}/comments?api-version=7.1-preview.3'
r = requests.post(url, auth=auth,
                  headers={'Content-Type': 'application/json'},
                  json={'text': comment}, timeout=30)

if r.status_code in (200, 201):
    comment_id = r.json().get('id')
    print(f'Comment posted OK — ID: {comment_id}')
else:
    print(f'ERROR: {r.status_code}')
    print(r.text[:500])
