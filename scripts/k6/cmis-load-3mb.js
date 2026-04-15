/**
 * k6 Load Test — CMIS API — 3MB Documents
 *
 * Scenario:
 *   - N concurrent users (default: 5), each runs M iterations (default: 100)
 *   - Per iteration:
 *       1. createDocument   (Document Uploaded)   — uploads a 3MB file
 *       2. getObject        (Document Viewed)      — metadata of 3MB document
 *       3. getContentStream (Document Downloaded)  — downloads 3MB document
 *
 * CMIS objectTypeId = DD Document Type (stored as "Template" in SQL Server)
 *   dd:Agreement is available in QA (repo 63), STG (repo 28), and PROD (repo 2).
 *   Each tenant/repo has its own set of allowed types.
 *
 * Cleanup: all uploaded k6perf-* documents are removed in teardown
 * Results: saved to scripts/k6/results/ as .json and .txt
 *
 * Usage:
 *   .\scripts\k6\run-cmis-load-3mb.ps1
 *
 * Or directly with overrides:
 *   k6 run --env VUS=10 --env ITERATIONS=50 scripts/k6/cmis-load-3mb.js
 */

import http from 'k6/http';
import { check } from 'k6';
import { Trend, Rate } from 'k6/metrics';
import encoding from 'k6/encoding';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// ─── Config ───────────────────────────────────────────────────────────────────

const BASE_URL      = __ENV.CMIS_BASE_URL     || 'https://api-qa.archeiotech.com';
const REPOSITORY_ID = __ENV.CMIS_REPO_ID      || '63';
const READ_DOC_ID   = __ENV.CMIS_DOC_ID       || 'document-659653'; // 3MB document
const FOLDER_ID     = __ENV.CMIS_FOLDER_ID    || 'folder-2307';
const OBJECT_TYPE   = __ENV.CMIS_OBJECT_TYPE  || 'dd:Agreement';
const USERNAME      = __ENV.CMIS_USERNAME     || 'dynamicdocs_user';
const PASSWORD      = __ENV.CMIS_PASSWORD     || 'j!h1b5DOfH';

const VUS        = parseInt(__ENV.VUS        || '5');
const ITERATIONS = parseInt(__ENV.ITERATIONS || '100');

// ─── k6 Options ───────────────────────────────────────────────────────────────

export const options = {
  teardownTimeout: '30m', // allow enough time to delete 500+ documents
  scenarios: {
    cmis_load: {
      executor:    'per-vu-iterations',
      vus:         VUS,
      iterations:  ITERATIONS,
      maxDuration: '90m',
    },
  },
  thresholds: {
    errors:                       ['rate<0.05'],
    create_document_duration:     ['p(95)<60000'],  // 60s — 3MB upload under load
    get_object_duration:          ['p(95)<15000'],  // 15s — metadata (includes cold start)
    get_content_stream_duration:  ['p(95)<30000'],  // 30s — 3MB download under load
  },
};

// ─── Custom Metrics ───────────────────────────────────────────────────────────

const createDocTrend  = new Trend('create_document_duration',    true);
const getObjectTrend  = new Trend('get_object_duration',         true);
const getContentTrend = new Trend('get_content_stream_duration', true);
const errorRate       = new Rate('errors');

// ─── Auth Headers ─────────────────────────────────────────────────────────────

const authHeader  = `Basic ${encoding.b64encode(`${USERNAME}:${PASSWORD}`)}`;
const baseHeaders = { Authorization: authHeader };
const xmlHeaders  = { Authorization: authHeader, 'Content-Type': 'application/atom+xml' };

// ─── Setup: generate 3MB content once, shared across all VUs ─────────────────

export function setup() {
  const targetBytes = 3 * 1024 * 1024;
  const chunk       = 'k6perfdata0123456789abcdefghij\n'; // 32 bytes
  const reps        = Math.ceil(targetBytes / chunk.length);
  const content     = chunk.repeat(reps).slice(0, targetBytes);
  const b64Content  = encoding.b64encode(content);

  console.log(`Setup: 3MB content ready (raw=${targetBytes} bytes, b64=${(b64Content.length / 1024 / 1024).toFixed(2)} MB)`);
  console.log(`Setup: ${VUS} VUs × ${ITERATIONS} iterations = ${VUS * ITERATIONS} total uploads`);
  console.log(`Setup: estimated storage impact ~${((VUS * ITERATIONS * 3) / 1024).toFixed(1)} GB`);

  return { b64Content };
}

// ─── Main Test ────────────────────────────────────────────────────────────────

export default function (data) {
  const docName = `k6perf-vu${__VU}-iter${__ITER}-${Date.now()}.txt`;

  // 1. createDocument — Document Uploaded (3MB)
  const createRes = http.post(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/children?id=${FOLDER_ID}`,
    buildBody(docName, data.b64Content),
    { headers: xmlHeaders, tags: { endpoint: 'createDocument' }, timeout: '120s' }
  );
  createDocTrend.add(createRes.timings.duration);
  errorRate.add(!check(createRes, {
    'createDocument: status 2xx': (r) => r.status >= 200 && r.status < 300,
  }));

  // 2. getObject — Document Viewed (metadata of 3MB document)
  const getObjRes = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/id?id=${READ_DOC_ID}`,
    { headers: baseHeaders, tags: { endpoint: 'getObject' }, timeout: '30s' }
  );
  getObjectTrend.add(getObjRes.timings.duration);
  errorRate.add(!check(getObjRes, {
    'getObject: status 2xx': (r) => r.status >= 200 && r.status < 300,
  }));

  // 3. getContentStream — Document Downloaded (3MB)
  const getContentRes = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/content?id=${READ_DOC_ID}`,
    { headers: baseHeaders, tags: { endpoint: 'getContentStream' }, timeout: '120s' }
  );
  getContentTrend.add(getContentRes.timings.duration);
  errorRate.add(!check(getContentRes, {
    'getContentStream: status 2xx': (r) => r.status >= 200 && r.status < 300,
  }));
}

// ─── Teardown: delete all uploaded k6perf-* documents ────────────────────────

export function teardown() {
  if (__ENV.SKIP_TEARDOWN === 'true') {
    console.log('Teardown: SKIP_TEARDOWN=true — documents left in QA (IDs will be captured by post-test script)');
    return;
  }

  console.log('Teardown: scanning folder for k6perf documents...');

  const toDelete  = [];
  let   skipCount = 0;
  const maxItems  = 200;

  // Phase 1 — collect all k6perf IDs (no deletes yet to avoid pagination drift)
  while (true) {
    const res = http.get(
      `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/children?id=${FOLDER_ID}&maxItems=${maxItems}&skipCount=${skipCount}`,
      { headers: baseHeaders, timeout: '60s' }
    );

    if (res.status !== 200) {
      console.error(`Teardown: getChildren failed status=${res.status}`);
      break;
    }

    const entries     = res.body.split('<atom:entry');
    const totalInPage = (res.body.match(/<atom:entry/g) || []).length;
    let   foundInPage = 0;

    for (const entry of entries) {
      if (!entry.includes('k6perf')) continue;
      const m = entry.match(/content\?id=(document-\d+)/);
      if (m) { toDelete.push(m[1]); foundInPage++; }
    }

    console.log(`  page skipCount=${skipCount}: ${totalInPage} entries, ${foundInPage} k6perf found`);

    if (totalInPage < maxItems) break;
    skipCount += maxItems;
  }

  console.log(`Teardown: ${toDelete.length} documents to delete`);

  // Phase 2 — delete all collected IDs
  let deleted = 0;
  let failed  = 0;

  for (const docId of toDelete) {
    const res = http.del(
      `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/id?id=${docId}`,
      null,
      { headers: baseHeaders, timeout: '30s' }
    );
    if (res.status === 200 || res.status === 204) {
      deleted++;
    } else {
      failed++;
      console.warn(`  failed to delete ${docId}: status=${res.status}`);
    }
  }

  console.log(`Teardown complete — deleted: ${deleted}, failed: ${failed}`);
}

// ─── Summary: save results to files ──────────────────────────────────────────

export function handleSummary(data) {
  const ts   = new Date().toISOString().slice(0, 16).replace('T', '-').replace(':', '-');
  const date = ts.slice(0, 10);
  const env  = (__ENV.CMIS_ENV || 'qa').toLowerCase();
  const base = `performance/cmis-api/${date}/raw-data/${env}-run-${ts}`;

  return {
    [`${base}.json`]: JSON.stringify(data, null, 2),
    [`${base}.txt`]:  textSummary(data, { indent: ' ', enableColors: false }),
    stdout:           textSummary(data, { enableColors: true }),
  };
}

// ─── XML Body Builder ─────────────────────────────────────────────────────────

function buildBody(docName, b64Content) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<atom:entry xmlns:atom="http://www.w3.org/2005/Atom"
            xmlns:cmis="http://docs.oasis-open.org/ns/cmis/core/200908/"
            xmlns:cmisra="http://docs.oasis-open.org/ns/cmis/restatom/200908/">
  <atom:author><cmis:name>k6-perf</cmis:name></atom:author>
  <atom:id>urn:uuid:00000000-0000-0000-0000-000000000000</atom:id>
  <atom:title/>
  <atom:updated>2026-04-14T00:00:00Z</atom:updated>
  <cmisra:content>
    <cmisra:mediatype>text/plain</cmisra:mediatype>
    <cmisra:base64>${b64Content}</cmisra:base64>
  </cmisra:content>
  <cmisra:object xmlns:ns3="http://docs.oasis-open.org/ns/cmis/messaging/200908/">
    <cmis:properties>
      <cmis:propertyString propertyDefinitionId="cmis:name">
        <cmis:value>${docName}</cmis:value>
      </cmis:propertyString>
      <cmis:propertyId propertyDefinitionId="cmis:objectTypeId">
        <cmis:value>${OBJECT_TYPE}</cmis:value>
      </cmis:propertyId>
    </cmis:properties>
  </cmisra:object>
</atom:entry>`;
}
