'use strict';

const express = require('express');
const https   = require('https');
const http    = require('http');
const path    = require('path');
const fs      = require('fs');

const app  = express();
const PORT = 3002;

// ── Load environment configs ───────────────────────────────────────────────

const ENVS = {
  qa: {
    label  : 'QA',
    baseUrl: 'https://test-api.ondemandquorum.com/documents/v1',
    apiKey : '2569b8fe8ca743d9a2f0733a53a9b7c6',
  },
  stg: {
    label  : 'Staging',
    baseUrl: 'https://apim-api-management-stg.azure-api.net/documents/v1',
    apiKey : '906362991def40fb94193eaf725dac33',
  },
  prod: {
    label  : 'Production',
    baseUrl: 'https://api.ondemandquorum.com/documents/v1',
    apiKey : '5d5edb41a057494783d7d2a9bf8177ab',
  },
};

const TENANTS_FILE = path.join(__dirname, '../dd-api/tenants/dd-tenants.json');

function loadTenants() {
  try {
    const raw = fs.readFileSync(TENANTS_FILE, 'utf8');
    return JSON.parse(raw);
  } catch {
    return { QA: [], Staging: [], Prod: [] };
  }
}

// ── Health check endpoint definitions ─────────────────────────────────────
// probe: false → normal check, expect 2xx = OK
// probe: true  → dummy ID/body, expect 4xx = Reachable (API up), 5xx/timeout = Down

const CHECKS = [
  // ── Document Types ──────────────────────────────────────────
  { id: 'doc-types-list',       label: 'Get Document Types',        method: 'GET',    path: '/document-types',                       tag: 'Document Types',    probe: false },
  { id: 'doc-types-create',     label: 'Create Document Type',      method: 'POST',   path: '/document-types',        body: {},      tag: 'Document Types',    probe: true  },

  // ── Documents ───────────────────────────────────────────────
  { id: 'docs-list',            label: 'Get Documents',             method: 'GET',    path: '/documents?page=1&pageSize=1',           tag: 'Documents',         probe: false },
  { id: 'docs-get-id',          label: 'Get Document by ID',        method: 'GET',    path: '/documents/0',                          tag: 'Documents',         probe: true  },
  { id: 'docs-upload',          label: 'Upload Document',           method: 'POST',   path: '/documents',             body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-search',          label: 'Search Documents',          method: 'POST',   path: '/documents/search',      body: { page: 1, pageSize: 1 }, tag: 'Documents', probe: false },
  { id: 'docs-update',          label: 'Update Document by ID',     method: 'PATCH',  path: '/documents/0',           body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-soft-delete-id',  label: 'Soft-Delete Document',      method: 'DELETE', path: '/documents/0',                          tag: 'Documents',         probe: true  },
  { id: 'docs-soft-delete-bulk',label: 'Soft-Delete (Bulk)',        method: 'DELETE', path: '/documents',             body: { ids: [] }, tag: 'Documents',      probe: true  },
  { id: 'docs-hard-delete',     label: 'Hard-Delete (Bulk)',        method: 'DELETE', path: '/documents/hard-delete', body: { ids: [] }, tag: 'Documents',      probe: true  },
  { id: 'docs-download',        label: 'Download Document',         method: 'GET',    path: '/documents/0/download',                 tag: 'Documents',         probe: true  },
  { id: 'docs-download-url',    label: 'Get Download URL',          method: 'GET',    path: '/documents/0/download-url',             tag: 'Documents',         probe: true  },
  { id: 'docs-restore',         label: 'Restore Document',          method: 'POST',   path: '/documents/0/restore',   body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-replace',         label: 'Replace Document',          method: 'PUT',    path: '/documents/0/replace',   body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-linked-loc-get',  label: 'Get Linked Locations',      method: 'GET',    path: '/documents/0/linked-locations',         tag: 'Documents',         probe: true  },
  { id: 'docs-linked-loc-patch',label: 'Update Linked Locations',   method: 'PATCH',  path: '/documents/0/linked-locations', body: {}, tag: 'Documents',       probe: true  },
  { id: 'docs-entities',        label: 'Add/Remove Entities',       method: 'PATCH',  path: '/documents/0/entities',  body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-move-staging',    label: 'Move from Staging',         method: 'PUT',    path: '/documents/0/move-from-staging', body: {}, tag: 'Documents',      probe: true  },
  { id: 'docs-bulk-link',       label: 'Bulk Link/Unlink Locations',method: 'POST',   path: '/documents/bulk-link-unlink', body: {}, tag: 'Documents',         probe: true  },
  { id: 'docs-bulk-update',     label: 'Bulk Update Documents',     method: 'PATCH',  path: '/documents/bulk-update', body: {},      tag: 'Documents',         probe: true  },
  { id: 'docs-move',            label: 'Move Documents',            method: 'POST',   path: '/documents/move-documents', body: {},   tag: 'Documents',         probe: true  },

  // ── OCR ─────────────────────────────────────────────────────
  { id: 'ocr-single-post',      label: 'OCR Single Document',       method: 'POST',   path: '/documents/0/ocr',       body: {},      tag: 'OCR',               probe: true  },
  { id: 'ocr-single-get',       label: 'Get OCR Text (Single)',     method: 'GET',    path: '/documents/0/ocr',                      tag: 'OCR',               probe: true  },
  { id: 'ocr-bulk-post',        label: 'OCR Multiple Documents',    method: 'POST',   path: '/documents/ocr',         body: {},      tag: 'OCR',               probe: true  },
  { id: 'ocr-bulk-retrieval',   label: 'Bulk OCR Retrieval',        method: 'POST',   path: '/documents/bulk-ocr-retrieval', body: {}, tag: 'OCR',             probe: true  },

  // ── Versions ────────────────────────────────────────────────
  { id: 'versions-upload',      label: 'Upload Version',            method: 'POST',   path: '/documents/0/versions',  body: {},      tag: 'Versions',          probe: true  },
  { id: 'versions-download',    label: 'Download by Version ID',    method: 'GET',    path: '/documents/0/versions/0/download',      tag: 'Versions',          probe: true  },

  // ── Document Batches ────────────────────────────────────────
  { id: 'batches-create',       label: 'Create Document Batch',     method: 'POST',   path: '/document-batches',      body: {},      tag: 'Document Batches',  probe: true  },
  { id: 'batches-export-jobs',  label: 'Get Export Jobs',           method: 'GET',    path: '/document-batches/export-jobs?page=1&pageSize=1', tag: 'Document Batches', probe: false },
  { id: 'batches-download',     label: 'Create Batch Download',     method: 'POST',   path: '/document-batches/batch-download', body: {}, tag: 'Document Batches', probe: true },

  // ── Insights ────────────────────────────────────────────────
  { id: 'insights-analyze',     label: 'Analyze Documents',         method: 'POST',   path: '/insights/documents',    body: {},      tag: 'Insights',          probe: true  },
  { id: 'insights-results',     label: 'Get Analysis Results',      method: 'GET',    path: '/insights/results?page=1&pageSize=1',    tag: 'Insights',          probe: false },

  // ── Locations ───────────────────────────────────────────────
  { id: 'locations-list',       label: 'Get Locations',             method: 'GET',    path: '/locations?page=1&pageSize=1',           tag: 'Locations',         probe: false },
  { id: 'locations-create',     label: 'Create Locations',          method: 'POST',   path: '/locations',             body: {},      tag: 'Locations',         probe: true  },
  { id: 'locations-get-id',     label: 'Get Location by ID',        method: 'GET',    path: '/locations/primary/0',                  tag: 'Locations',         probe: true  },
  { id: 'locations-update',     label: 'Update Location Name',      method: 'PUT',    path: '/locations/primary/0',   body: {},      tag: 'Locations',         probe: true  },
  { id: 'locations-delete',     label: 'Delete Location',           method: 'DELETE', path: '/locations/primary/0',                  tag: 'Locations',         probe: true  },
  { id: 'locations-attrs-create',label:'Create Location Attributes',method: 'POST',   path: '/locations/primary/0/attributes', body: {}, tag: 'Locations',    probe: true  },
  { id: 'locations-attrs-update',label:'Update Location Attributes',method: 'PUT',    path: '/locations/primary/0/attributes', body: {}, tag: 'Locations',    probe: true  },

  // ── Linked Documents ────────────────────────────────────────
  { id: 'linked-docs',          label: 'Link Documents',            method: 'POST',   path: '/linked-documents',      body: {},      tag: 'Linked Documents',  probe: true  },

  // ── Email ───────────────────────────────────────────────────
  { id: 'email',                label: 'Send via Email Ingestion',  method: 'POST',   path: '/email',                 body: {},      tag: 'Email',             probe: true  },

  // ── Projects ────────────────────────────────────────────────
  { id: 'projects-create',      label: 'Create Project',            method: 'POST',   path: '/projects',              body: {},      tag: 'Projects',          probe: true  },
  { id: 'projects-populate',    label: 'Populate Project',          method: 'PATCH',  path: '/projects/0/populate',   body: {},      tag: 'Projects',          probe: true  },
  { id: 'projects-attrs',       label: 'Update Project Attributes', method: 'PATCH',  path: '/projects/0/attributes', body: {},      tag: 'Projects',          probe: true  },

  // ── Users ───────────────────────────────────────────────────
  { id: 'users-create',         label: 'Create User',               method: 'POST',   path: '/users',                 body: {},      tag: 'Users',             probe: true  },

  // ── Credentials ─────────────────────────────────────────────
  { id: 'credentials-create',   label: 'Create Credential',         method: 'POST',   path: '/credentials',           body: {},      tag: 'Credentials',       probe: true  },
  { id: 'credentials-get',      label: 'Get Credentials by User',   method: 'GET',    path: '/credentials/users/0',                  tag: 'Credentials',       probe: true  },
  { id: 'credentials-update',   label: 'Update Credential',         method: 'PATCH',  path: '/credentials/0/users/0', body: {},      tag: 'Credentials',       probe: true  },

  // ── Extension ───────────────────────────────────────────────
  { id: 'extension',            label: 'Get Extension Whitelist',   method: 'GET',    path: '/extension',                            tag: 'Extension',         probe: false },
];

// ── HTTP helper ────────────────────────────────────────────────────────────

function ddRequest({ baseUrl, apiKey, quti, email, method, endpointPath, body }) {
  return new Promise((resolve) => {
    const start  = Date.now();
    const fullUrl = `${baseUrl}${endpointPath}`;
    let parsed;
    try { parsed = new URL(fullUrl); }
    catch (e) { return resolve({ ok: false, status: 0, ms: 0, error: `URL inválida: ${e.message}` }); }

    const isHttps  = parsed.protocol === 'https:';
    const lib      = isHttps ? https : http;
    const payload  = body ? JSON.stringify(body) : null;

    const headers = {
      'Ocp-Apim-Subscription-Key': apiKey,
      'quti'                     : quti,
      'email'                    : email,
      'Accept'                   : 'application/json',
    };
    if (payload) {
      headers['Content-Type']   = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(payload);
    }

    const options = {
      hostname: parsed.hostname,
      port    : parsed.port || (isHttps ? 443 : 80),
      path    : parsed.pathname + parsed.search,
      method  : method,
      headers,
      timeout : 15000,
    };

    const req = lib.request(options, (res) => {
      let raw = '';
      res.on('data', chunk => { raw += chunk; });
      res.on('end', () => {
        const ms = Date.now() - start;
        let responseBody = null;
        try { responseBody = JSON.parse(raw); } catch { responseBody = raw.slice(0, 300); }
        resolve({
          ok    : res.statusCode >= 200 && res.statusCode < 300,
          status: res.statusCode,
          ms,
          body  : responseBody,
        });
      });
    });

    req.on('error', (err) => {
      resolve({ ok: false, status: 0, ms: Date.now() - start, error: err.message });
    });
    req.on('timeout', () => {
      req.destroy();
      resolve({ ok: false, status: 0, ms: 15000, error: 'Request timeout (15s)' });
    });

    if (payload) req.write(payload);
    req.end();
  });
}

// ── Middleware ─────────────────────────────────────────────────────────────

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── Routes ─────────────────────────────────────────────────────────────────

// GET /api/config — return envs + tenants (no individual prod tenant PII)
app.get('/api/config', (_req, res) => {
  const allTenants = loadTenants();
  res.json({
    environments: Object.entries(ENVS).map(([key, cfg]) => ({ key, label: cfg.label })),
    tenants: {
      qa : allTenants.QA.map(t => ({ client: t.Client, quti: t.QUTI })),
      stg: allTenants.Staging.map(t => ({ client: t.Client, quti: t.QUTI })),
      prod: allTenants.Prod.slice(0, 50).map(t => ({ client: t.Client, quti: t.QUTI })),
    },
    checks: CHECKS.map(c => ({ id: c.id, label: c.label, method: c.method, path: c.path, tag: c.tag, probe: c.probe })),
  });
});

// POST /api/health — run all checks for a given env + tenant
app.post('/api/health', async (req, res) => {
  const { env, quti, email } = req.body;

  if (!env || !quti || !email) {
    return res.status(400).json({ error: 'env, quti y email son requeridos.' });
  }

  // Validate env
  if (!ENVS[env]) {
    return res.status(400).json({ error: 'env inválido. Usa: qa, stg o prod.' });
  }

  // Validate email format (basic)
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'email inválido.' });
  }

  // Validate quti (alphanumeric + common separators only)
  if (!/^[a-z0-9_\-\.]{1,64}$/i.test(quti)) {
    return res.status(400).json({ error: 'quti inválido.' });
  }

  const cfg = ENVS[env];
  const results = [];

  // Run checks sequentially to avoid hammering the API
  for (const check of CHECKS) {
    const result = await ddRequest({
      baseUrl     : cfg.baseUrl,
      apiKey      : cfg.apiKey,
      quti,
      email,
      method      : check.method,
      endpointPath: check.path,
      body        : check.body || null,
    });

    results.push({
      id    : check.id,
      label : check.label,
      method: check.method,
      path  : check.path,
      tag   : check.tag,
      probe : check.probe,
      ok    : result.ok,
      status: result.status,
      ms    : result.ms,
      error : result.error || null,
    });
  }

  res.json({
    env,
    quti,
    baseUrl  : cfg.baseUrl,
    checkedAt: new Date().toISOString(),
    results,
  });
});

// ── Start ──────────────────────────────────────────────────────────────────

app.listen(PORT, '127.0.0.1', () => {
  console.log('');
  console.log('  ✅  DD API Health Dashboard listo');
  console.log(`  👉  Abre http://localhost:${PORT} en tu navegador`);
  console.log('');
});
