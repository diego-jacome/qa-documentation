"""
post_perf_prod_baseline.py
Posts the CMIS PROD baseline performance report as an HTML comment on ADO 1796375.
No emojis. GET + PATCH if comment already exists, POST otherwise.
"""
import os, json, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(r'C:\Users\diego.jacome\Repos\qa-documentation\scripts\ado\.env')
ADO_URL     = os.getenv('ADO_URL').rstrip('/')
ADO_PROJECT = os.getenv('ADO_PROJECT')
ADO_PAT     = os.getenv('ADO_PAT')
auth        = HTTPBasicAuth('', ADO_PAT)
WORK_ITEM   = 1796375
MARKER      = 'PROD Baseline'   # used to detect existing comment (keep simple — ADO stores HTML entities, avoid &nbsp; etc.)

comment = """\
<h2 style="color:#107C10; border-bottom:2px solid #107C10; padding-bottom:6px">\
Performance Test Report &#8212; CMIS API &nbsp;|&nbsp; PROD Baseline</h2>

<p><strong>Date:</strong> April 14, 2026 &nbsp;|&nbsp;
<strong>Environment:</strong> PROD &#8212; Tenant: ProductionTest (Archwell) &nbsp;|&nbsp;
<strong>Tool:</strong> k6 v1.7.1</p>

<h3 style="margin-top:20px">Test Configuration</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Parameter</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Concurrent Users (VUs)</td>
      <td style="border:1px solid #d2d0ce; padding:8px">5</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Iterations per User</td>
      <td style="border:1px solid #d2d0ce; padding:8px">100</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Iterations</td>
      <td style="border:1px solid #d2d0ce; padding:8px">500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Document Size</td>
      <td style="border:1px solid #d2d0ce; padding:8px">3 MB</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Duration</td>
      <td style="border:1px solid #d2d0ce; padding:8px">5 min 14 sec</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Document Type (CMIS objectTypeId)</td>
      <td style="border:1px solid #d2d0ce; padding:8px">dd:Agreement</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">CMIS Repository ID</td>
      <td style="border:1px solid #d2d0ce; padding:8px">2</td></tr>
</table>

<p style="margin-top:12px"><strong>Scenario:</strong> Each virtual user executes 3 CMIS endpoints sequentially per iteration:<br>
1. Upload a 3 MB document &#8212; <code>createDocument</code> (POST)<br>
2. Read metadata of a 3 MB document &#8212; <code>getObject</code> (GET)<br>
3. Download a 3 MB document &#8212; <code>getContentStream</code> (GET)</p>

<h3 style="margin-top:20px">Results by Endpoint</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px">Endpoint</th>
    <th style="border:1px solid #d2d0ce; padding:8px">Action</th>
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
    <td style="border:1px solid #d2d0ce; padding:8px">2.12 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.00 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.32 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.48 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">9.74 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Downloaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">638 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">558 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">893 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.13 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">6.29 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Viewed</td>
    <td style="border:1px solid #d2d0ce; padding:8px">297 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">256 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">384 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">402 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.99 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
</table>

<h3 style="margin-top:20px">Reliability</h3>
<table style="border-collapse:collapse; width:80%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Metric</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Requests</td>
      <td style="border:1px solid #d2d0ce; padding:8px">1,500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Successful Requests</td>
      <td style="border:1px solid #d2d0ce; padding:8px">1,500 (100%)</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Error Rate</td>
      <td style="border:1px solid #d2d0ce; padding:8px">0.00%</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Throughput</td>
      <td style="border:1px solid #d2d0ce; padding:8px">&#8776; 4.78 req/s</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">All Thresholds</td>
      <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASSED</td></tr>
</table>

<h3 style="margin-top:20px">PROD vs QA vs STG Comparison (avg)</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px">Endpoint</th>
    <th style="border:1px solid #d2d0ce; padding:8px">PROD Baseline</th>
    <th style="border:1px solid #d2d0ce; padding:8px">STG Baseline</th>
    <th style="border:1px solid #d2d0ce; padding:8px">QA Run 2</th>
    <th style="border:1px solid #d2d0ce; padding:8px">&#916; vs STG</th>
    <th style="border:1px solid #d2d0ce; padding:8px">&#916; vs QA</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>createDocument</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>2.12 s</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.17 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.85 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;2% (similar)</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;26% faster</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>638 ms</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.50 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.02 s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;57% faster</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;37% faster</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px"><strong>297 ms</strong></td>
    <td style="border:1px solid #d2d0ce; padding:8px">865 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">475 ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;66% faster</td>
    <td style="border:1px solid #d2d0ce; padding:8px">&#8776; &#8209;37% faster</td>
  </tr>
</table>

<h3 style="margin-top:20px">Notes</h3>
<ul>
  <li>PROD read operations (getObject, getContentStream) are significantly faster than QA and STG &#8212; consistent with PROD infrastructure being more capable.</li>
  <li>Upload performance (createDocument) is comparable to STG and 26% faster than QA.</li>
</ul>

<div style="background:#dff6dd; padding:12px; border-left:4px solid #107C10; margin-top:20px">
  <strong>Verdict: </strong>
  PROD baseline completed with <strong>0 errors across 500 iterations</strong> (1,500 requests).
  All three CMIS endpoints performed within acceptable thresholds.
  PROD demonstrates the best read performance of all three environments.
  <strong>Baseline established for future PROD regression comparisons.</strong>
</div>"""

# ── GET existing comments ─────────────────────────────────────────────────────
url_comments = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/workItems/{WORK_ITEM}/comments?api-version=7.1-preview.3'
r = requests.get(url_comments, auth=auth, timeout=30)
r.raise_for_status()
comments_list = r.json().get('comments', [])

existing = next(
    (c for c in reversed(comments_list) if MARKER in c.get('text', '')),
    None
)

if existing:
    cid = existing['id']
    url_patch = f'{ADO_URL}/{ADO_PROJECT}/_apis/wit/workItems/{WORK_ITEM}/comments/{cid}?api-version=7.1-preview.3'
    r2 = requests.patch(url_patch, auth=auth, json={'text': comment},
                        headers={'Content-Type': 'application/json'}, timeout=30)
    r2.raise_for_status()
    print(f'PATCH OK — updated comment {cid}')
else:
    r2 = requests.post(url_comments, auth=auth, json={'text': comment},
                       headers={'Content-Type': 'application/json'}, timeout=30)
    r2.raise_for_status()
    new_id = r2.json().get('id')
    print(f'POST OK — new comment {new_id}')
