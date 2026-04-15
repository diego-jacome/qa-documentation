/**
 * k6 Performance Test — CMIS API (QA)
 *
 * Endpoints tested:
 *   1. createDocument   (Document Uploaded)   POST /cmis/.../children
 *   2. getObject        (Document Viewed)      GET  /cmis/.../id
 *   3. getContentStream (Document Downloaded)  GET  /cmis/.../content
 *
 * Usage:
 *   k6 run scripts/k6/cmis-performance.js
 *
 * Override params via CLI:
 *   k6 run --vus 20 --duration 2m scripts/k6/cmis-performance.js
 *
 * Override credentials/env via CLI (optional):
 *   k6 run --env CMIS_USERNAME=user --env CMIS_PASSWORD=pass scripts/k6/cmis-performance.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';
import encoding from 'k6/encoding';

// ─── Config ──────────────────────────────────────────────────────────────────

const BASE_URL       = 'https://api-qa.archeiotech.com';
const REPOSITORY_ID  = __ENV.CMIS_REPO_ID  || '63';
const DOCUMENT_ID    = __ENV.CMIS_DOC_ID   || 'document-652392';
const FOLDER_ID      = __ENV.CMIS_FOLDER_ID || '2307';
const USERNAME       = __ENV.CMIS_USERNAME  || 'dynamicdocs_user';
const PASSWORD       = __ENV.CMIS_PASSWORD  || 'j!h1b5DOfH';

// ─── k6 Options ──────────────────────────────────────────────────────────────

export const options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    // 95% de las requests deben responder en menos de 3 segundos
    http_req_duration:            ['p(95)<3000'],
    // Menos del 5% de errores
    errors:                       ['rate<0.05'],
    // Por endpoint
    create_document_duration:     ['p(95)<5000'],
    get_object_duration:          ['p(95)<2000'],
    get_content_stream_duration:  ['p(95)<3000'],
  },
};

// ─── Custom Metrics ───────────────────────────────────────────────────────────

const createDocTrend  = new Trend('create_document_duration',    true);
const getObjectTrend  = new Trend('get_object_duration',         true);
const getContentTrend = new Trend('get_content_stream_duration', true);
const errorRate       = new Rate('errors');

// ─── Helpers ─────────────────────────────────────────────────────────────────

const authHeader = `Basic ${encoding.b64encode(`${USERNAME}:${PASSWORD}`)}`;

const baseHeaders = {
  Authorization: authHeader,
};

const xmlHeaders = {
  Authorization:  authHeader,
  'Content-Type': 'application/atom+xml',
};

function buildCreateDocBody(docName) {
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
    <cmisra:base64>${encoding.b64encode('k6 performance test')}</cmisra:base64>
  </cmisra:content>
  <cmisra:object xmlns:ns3="http://docs.oasis-open.org/ns/cmis/messaging/200908/">
    <cmis:properties>
      <cmis:propertyString propertyDefinitionId="cmis:name">
        <cmis:value>${docName}</cmis:value>
      </cmis:propertyString>
      <cmis:propertyId propertyDefinitionId="cmis:objectTypeId">
        <cmis:value>dd:Agreement</cmis:value>
      </cmis:propertyId>
    </cmis:properties>
  </cmisra:object>
</atom:entry>`;
}

// ─── Main Test Function ───────────────────────────────────────────────────────

export default function () {
  const docName = `perf-test-vu${__VU}-iter${__ITER}.txt`;

  // 1. Document Uploaded — createDocument
  const createRes = http.post(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/children?id=folder-${FOLDER_ID}`,
    buildCreateDocBody(docName),
    { headers: xmlHeaders, tags: { endpoint: 'createDocument' } }
  );
  createDocTrend.add(createRes.timings.duration);
  const createOk = check(createRes, {
    'createDocument: status 2xx': (r) => r.status >= 200 && r.status < 300,
  });
  errorRate.add(!createOk);

  // 2. Document Viewed — getObject
  const getObjRes = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/id?id=${DOCUMENT_ID}`,
    { headers: baseHeaders, tags: { endpoint: 'getObject' } }
  );
  getObjectTrend.add(getObjRes.timings.duration);
  const getObjOk = check(getObjRes, {
    'getObject: status 2xx': (r) => r.status >= 200 && r.status < 300,
  });
  errorRate.add(!getObjOk);

  // 3. Document Downloaded — getContentStream
  const getContentRes = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/content?id=${DOCUMENT_ID}`,
    { headers: baseHeaders, tags: { endpoint: 'getContentStream' } }
  );
  getContentTrend.add(getContentRes.timings.duration);
  const getContentOk = check(getContentRes, {
    'getContentStream: status 2xx': (r) => r.status >= 200 && r.status < 300,
  });
  errorRate.add(!getContentOk);

  sleep(1);
}
