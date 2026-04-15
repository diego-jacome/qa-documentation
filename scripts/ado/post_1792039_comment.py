"""
Post comment on ADO work item 1792039 with image attachment.
Steps:
  1. Upload image as ADO attachment
  2. Link attachment to work item
  3. POST or PATCH comment with inline <img>
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv('scripts/ado/.env')

ADO_URL   = os.getenv('ADO_URL', '').rstrip('/')
PROJECT   = os.getenv('ADO_PROJECT', '')
PAT       = os.getenv('ADO_PAT', '')
auth      = HTTPBasicAuth('', PAT)

WORK_ITEM_ID = 1792039
IMAGE_PATH   = r'C:\Users\diego.jacome\AppData\Roaming\Code\User\workspaceStorage\vscode-chat-images\image-1776208175557.png'
FILE_NAME    = 'ExportWorker_BatchAccount_Apr14_2026.png'

# ── 1. Upload attachment ──────────────────────────────────────────────────────
print(f'[1/3] Uploading attachment: {FILE_NAME}')
upload_url = f'{ADO_URL}/{PROJECT}/_apis/wit/attachments?fileName={FILE_NAME}&api-version=7.1'

with open(IMAGE_PATH, 'rb') as f:
    image_bytes = f.read()

resp = requests.post(
    upload_url,
    auth=auth,
    headers={'Content-Type': 'application/octet-stream'},
    data=image_bytes,
    timeout=60
)
resp.raise_for_status()
attachment = resp.json()
attachment_url = attachment['url']
print(f'    Attachment URL: {attachment_url}')

# ── 2. Link attachment to work item ──────────────────────────────────────────
print(f'[2/3] Linking attachment to work item #{WORK_ITEM_ID}')
patch_url = f'{ADO_URL}/{PROJECT}/_apis/wit/workItems/{WORK_ITEM_ID}?api-version=7.1'
patch_body = [
    {
        "op": "add",
        "path": "/relations/-",
        "value": {
            "rel": "AttachedFile",
            "url": attachment_url,
            "attributes": {"comment": "ExportWorker Batch Account — active packages (Apr 14, 2026)"}
        }
    }
]
resp2 = requests.patch(
    patch_url,
    auth=auth,
    headers={'Content-Type': 'application/json-patch+json'},
    json=patch_body,
    timeout=30
)
resp2.raise_for_status()
print('    Attachment linked.')

# ── 3. Build HTML comment ─────────────────────────────────────────────────────
html = f"""<h2 style="color:#107C10; border-bottom:2px solid #107C10; padding-bottom:6px">QA Testing Note &#8212; Implementation Clarification</h2>

<p><strong>Date:</strong> April 14, 2026 &nbsp;|&nbsp; <strong>Tester:</strong> Diego Jacome &nbsp;|&nbsp; <strong>State:</strong> In Test</p>

<h3 style="margin-top:20px">Dev Clarification</h3>

<p>During testing intake, the development team (Luis Urrea) clarified that <strong>the application was not containerized</strong> as originally described in the user story. Instead, it was <strong>implemented into an Azure Batch Account</strong> (<code>batchddexportservicetest</code>), which serves as an alternative deployment approach to achieve the same management and execution goals.</p>

<h3 style="margin-top:20px">Observed Batch Account State</h3>

<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Field</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Value</th>
  </tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Batch Account</td><td style="border:1px solid #d2d0ce; padding:8px"><code>batchddexportservicetest</code></td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Resource Group</td><td style="border:1px solid #d2d0ce; padding:8px"><code>rg-batch-operations-test</code></td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Application</td><td style="border:1px solid #d2d0ce; padding:8px"><code>ExportWorker</code></td></tr>
  <tr><td style="border:1px solid #d2d0ce; padding:8px">Allow Updates</td><td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">true</td></tr>
</table>

<h3 style="margin-top:20px">Active Application Packages at Time of Testing</h3>

<table style="border-collapse:collapse; width:100%">
  <tr style="background:#f3f2f1">
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Package ID</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">State</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Format</th>
    <th style="border:1px solid #d2d0ce; padding:8px; text-align:left">Last Activation</th>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>25f2a7e</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">Active</td>
    <td style="border:1px solid #d2d0ce; padding:8px">zip</td>
    <td style="border:1px solid #d2d0ce; padding:8px">Apr 14, 2026 06:56:00</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>26ce68d</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">Active</td>
    <td style="border:1px solid #d2d0ce; padding:8px">zip</td>
    <td style="border:1px solid #d2d0ce; padding:8px">Apr 14, 2026 08:12:08</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>b428dac</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">Active</td>
    <td style="border:1px solid #d2d0ce; padding:8px">zip</td>
    <td style="border:1px solid #d2d0ce; padding:8px">Apr 13, 2026 15:37:41</td>
  </tr>
  <tr>
    <td style="border:1px solid #d2d0ce; padding:8px"><code>d25d0a6</code></td>
    <td style="border:1px solid #d2d0ce; padding:8px; color:green; font-weight:bold">Active</td>
    <td style="border:1px solid #d2d0ce; padding:8px">zip</td>
    <td style="border:1px solid #d2d0ce; padding:8px">Apr 14, 2026 14:27:51</td>
  </tr>
</table>

<h3 style="margin-top:20px">Screenshot &#8212; Azure Portal (Batch Account)</h3>
<p><img src="{attachment_url}" alt="ExportWorker Batch Account — active packages" style="max-width:100%; border:1px solid #d2d0ce;" /></p>

<h3 style="margin-top:20px; color:#107C10">Acceptance Criteria Deviation</h3>
<p style="background:#fff4ce; padding:12px; border-left:4px solid #f2c94c;">
  The original AC states: <em>"The application must be fully containerized."</em><br/>
  The team chose <strong>Azure Batch Account</strong> as the deployment mechanism instead of a container.<br/>
  This approach deviation should be <strong>acknowledged and accepted by the PO/BA</strong> before the story is moved to Acceptance.
</p>"""

# ── 4. POST or PATCH comment ──────────────────────────────────────────────────
print(f'[3/3] Posting comment on work item #{WORK_ITEM_ID}')
comments_base = f'{ADO_URL}/{PROJECT}/_apis/wit/workItems/{WORK_ITEM_ID}/comments'
existing = requests.get(
    comments_base + '?api-version=7.1-preview.3',
    auth=auth, timeout=30
).json().get('comments', [])

target = next((c for c in existing if 'QA Testing Note' in c.get('text', '') and 'Implementation Clarification' in c.get('text', '')), None)

if target:
    r = requests.patch(
        f"{comments_base}/{target['id']}?api-version=7.1-preview.3",
        auth=auth,
        headers={'Content-Type': 'application/json'},
        json={'text': html},
        timeout=30
    )
    r.raise_for_status()
    print(f'    Comment UPDATED (id={target["id"]}). Done.')
else:
    r = requests.post(
        comments_base + '?api-version=7.1-preview.3',
        auth=auth,
        headers={'Content-Type': 'application/json'},
        json={'text': html},
        timeout=30
    )
    r.raise_for_status()
    comment_id = r.json().get('id')
    print(f'    Comment POSTED (id={comment_id}). Done.')
