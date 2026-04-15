import os, requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(r'C:\Users\diego.jacome\Repos\qa-documentation\scripts\ado\.env')
ADO_URL = os.getenv('ADO_URL').rstrip('/')
ADO_PROJECT = os.getenv('ADO_PROJECT')
ADO_PAT = os.getenv('ADO_PAT')
auth = HTTPBasicAuth('', ADO_PAT)

comment = """<h2 style="color:#107C10; border-bottom:2px solid #107C10; padding-bottom:6px">Performance Test Report &#8212; CMIS API</h2>

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
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Duration</td><td style="border:1px solid #d2d0ce; padding:8px">7 min 26 sec</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Data Sent</td><td style="border:1px solid #d2d0ce; padding:8px">2.1 GB</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Data Received</td><td style="border:1px solid #d2d0ce; padding:8px">1.6 GB</td></tr>
</table>

<p style="margin-top:12px"><strong>Scenario:</strong> Each virtual user concurrently executes the following 3 endpoints sequentially per iteration:<br>
1. Upload a 3MB document &#8212; <code>createDocument</code><br>
2. Read metadata of a 3MB document &#8212; <code>getObject</code><br>
3. Download a 3MB document &#8212; <code>getContentStream</code></p>

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
    <th style="border:1px solid #d2d0ce; padding:8px">Result</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>createDocument</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Uploaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.66s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">2.53s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">3.23s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">3.58s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">9.57s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getContentStream</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Downloaded</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.17s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.04s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.75s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.93s</td>
    <td style="border:1px solid #d2d0ce; padding:8px">8.04s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>getObject</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px">Document Viewed</td>
    <td style="border:1px solid #d2d0ce; padding:8px">454ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">427ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">591ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">730ms</td>
    <td style="border:1px solid #d2d0ce; padding:8px">1.46s</td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASS</td>
  </tr>
</table>

<h3 style="margin-top:20px">&#9989; Reliability Summary</h3>
<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Metric</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Total Requests</td><td style="border:1px solid #d2d0ce; padding:8px">1,500 (500 iterations x 3 endpoints)</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Successful Requests</td><td style="border:1px solid #d2d0ce; padding:8px">1,500 (100%)</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Error Rate</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">0.00%</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Checks Passed</td><td style="border:1px solid #d2d0ce; padding:8px">1,500 / 1,500</td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">All Thresholds</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">PASSED</td></tr>
</table>

<h3 style="margin-top:20px">&#128221; Observations</h3>
<ol>
  <li style="margin-bottom:6px"><strong>Zero errors under load</strong> &#8212; The API handled 5 concurrent users uploading and downloading 3MB files continuously without a single failure.</li>
  <li style="margin-bottom:6px"><strong>Stable upload performance</strong> &#8212; <code>createDocument</code> averaged 2.66s with p(95) at 3.58s. The 9.57s peak was an isolated outlier.</li>
  <li style="margin-bottom:6px"><strong>Efficient downloads</strong> &#8212; <code>getContentStream</code> downloaded 3MB files in 1.17s on average, with p(95) well under 2s.</li>
  <li style="margin-bottom:6px"><strong>Fast metadata reads</strong> &#8212; <code>getObject</code> responded in 454ms on average regardless of concurrent load.</li>
  <li style="margin-bottom:6px"><strong>Sustained throughput</strong> &#8212; &#8776;3.25 requests/second maintained throughout the entire test (&#8776;1 upload per second across the 5 VUs).</li>
</ol>

<h3 style="margin-top:20px; color:#107C10">&#128313; Verdict</h3>
<p style="background:#dff6dd; padding:12px; border-left:4px solid #107C10">
  The CMIS API in QA <strong>successfully handles 5 concurrent users each uploading 100 files of 3MB</strong>, totaling 500 concurrent uploads with no performance degradation or errors. The scenario previously reported as problematic in production <strong>does not reproduce in QA under these conditions</strong>.
</p>"""

base = ADO_URL + '/' + ADO_PROJECT + '/_apis/wit/workItems/1796375/comments'
headers = {'Content-Type': 'application/json'}

# Get existing comments to find the perf report one
r = requests.get(base + '?api-version=7.1-preview.3', auth=auth, timeout=15)
comments = r.json().get('comments', [])
target_id = None
for c in comments:
    if 'Performance Test Report' in c.get('text', '') or 'CMIS API' in c.get('text', ''):
        target_id = c['id']
        print(f'Found existing comment ID: {target_id}')
        break

if target_id:
    url = f'{base}/{target_id}?api-version=7.1-preview.3'
    r = requests.patch(url, auth=auth, json={'text': comment}, headers=headers, timeout=30)
else:
    print('No existing perf comment found — posting new one')
    url = base + '?api-version=7.1-preview.3'
    r = requests.post(url, auth=auth, json={'text': comment}, headers=headers, timeout=30)

print('Status:', r.status_code)
if r.status_code in (200, 201):
    print('OK — Comment ID:', r.json().get('id'))
else:
    print('Error:', r.text[:500])
