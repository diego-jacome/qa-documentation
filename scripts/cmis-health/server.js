'use strict';

require('dotenv').config({ path: require('path').join(__dirname, '.env') });

const express = require('express');
const https   = require('https');
const http    = require('http');
const path    = require('path');
const fs      = require('fs');

const app  = express();
const PORT = 3003;

// ── Tenants ───────────────────────────────────────────────────────────────

const TENANTS_FILE = path.join(__dirname, '../dd-api/tenants/dd-tenants.json');

function loadTenants() {
  try {
    const raw = fs.readFileSync(TENANTS_FILE, 'utf8');
    return JSON.parse(raw);
  } catch {
    return { QA: [], Staging: [], Prod: [] };
  }
}

// ── Environment configs ────────────────────────────────────────────────────

const ENVS = {
  dev: {
    label  : 'Dev',
    baseUrl: 'https://api-dev.archeiotech.com',
  },
  qa: {
    label  : 'QA',
    baseUrl: 'https://api-qa.archeiotech.com',
  },
  stg: {
    label  : 'Staging',
    baseUrl: 'https://api-staging.archeiotech.com',
  },
  prod: {
    label  : 'Production',
    baseUrl: '', // Update when endpoint is confirmed
  },
};

// ── Endpoint check definitions ─────────────────────────────────────────────
// probe: false → safe GET, expect 2xx = OK
// probe: true  → expect 4xx = Reachable (API up), 5xx/timeout = Down

const CHECKS = [
  // ── Version ─────────────────────────────────────────────────
  { id: 'api-version',        label: 'Get API Version',           method: 'GET',    pathTpl: '/api/version',                                                  tag: 'Version',         probe: false },
  { id: 'cmis-service-doc',   label: 'CMIS Service Document',     method: 'GET',    pathTpl: '/cmis/version/1.1/atom',                                        tag: 'Version',         probe: false },

  // ── Repository / Types ───────────────────────────────────────
  { id: 'types-list',         label: 'List Types',                method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/types',                         tag: 'Types',           probe: false },
  { id: 'type-desc',          label: 'Get Type Descendants',      method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/typedesc',                      tag: 'Types',           probe: false },
  { id: 'type-by-id',         label: 'Get Type by ID',            method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/type?id=cmis:document',         tag: 'Types',           probe: false },

  // ── Navigation ───────────────────────────────────────────────
  { id: 'children-root',      label: 'Get Root Folder Children',  method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/children',                      tag: 'Navigation',      probe: false },
  { id: 'path-root',          label: 'Get Object by Path (root)', method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/path?path=/',                   tag: 'Navigation',      probe: false },
  { id: 'id-probe',           label: 'Get Object by ID (probe)',  method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/id?id=00000000-probe-test',     tag: 'Navigation',      probe: true  },
  { id: 'parent-probe',       label: 'Get Parent (probe)',        method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/parent?id=00000000-probe-test', tag: 'Navigation',      probe: true  },
  { id: 'parents-probe',      label: 'Get Parents (probe)',       method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/parents?objectId=00000000-probe-test', tag: 'Navigation', probe: true },

  // ── Content ──────────────────────────────────────────────────
  { id: 'content-probe',      label: 'Get Content Stream (probe)',method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/content?id=00000000-probe-test',tag: 'Content',         probe: true  },
  { id: 'create-doc-probe',   label: 'Create Document (probe)',   method: 'POST',   pathTpl: '/cmis/version/1.1/atom/{repoId}/children',                      tag: 'Content',         probe: true  },
  { id: 'update-content-probe',label: 'Update Content (probe)',   method: 'PUT',    pathTpl: '/cmis/version/1.1/atom/{repoId}/content?id=00000000-probe-test',tag: 'Content',         probe: true  },
  { id: 'delete-content-probe',label: 'Delete Content (probe)',   method: 'DELETE', pathTpl: '/cmis/version/1.1/atom/{repoId}/content?id=00000000-probe-test',tag: 'Content',         probe: true  },

  // ── Object Operations ────────────────────────────────────────
  { id: 'allowable-probe',    label: 'Allowable Actions (probe)', method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/allowableactions?id=00000000-probe-test', tag: 'Operations', probe: true },
  { id: 'acl-probe',          label: 'Get ACL (probe)',           method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/acl?id=00000000-probe-test',   tag: 'Operations',      probe: true  },
  { id: 'relationships-probe',label: 'Get Relationships (probe)', method: 'GET',    pathTpl: '/cmis/version/1.1/atom/{repoId}/relationships?id=00000000-probe-test', tag: 'Operations', probe: true },
  { id: 'update-probe',       label: 'Bulk Update (probe)',       method: 'POST',   pathTpl: '/cmis/version/1.1/atom/{repoId}/update',                        tag: 'Operations',      probe: true  },
  { id: 'unfiled-probe',      label: 'Unfiled Objects (probe)',   method: 'POST',   pathTpl: '/cmis/version/1.1/atom/{repoId}/unfiled',                       tag: 'Operations',      probe: true  },
];

// ── HTTP helper ────────────────────────────────────────────────────────────

function cmisRequest({ baseUrl, username, password, repoId, method, endpointPath }) {
  return new Promise((resolve) => {
    const start   = Date.now();
    const fullUrl = `${baseUrl}${endpointPath}`;
    let parsed;
    try { parsed = new URL(fullUrl); }
    catch (e) { return resolve({ ok: false, status: 0, ms: 0, error: `URL inválida: ${e.message}` }); }

    const isHttps = parsed.protocol === 'https:';
    const lib     = isHttps ? https : http;

    const credentials = Buffer.from(`${username}:${password}`).toString('base64');

    const headers = {
      'Authorization': `Basic ${credentials}`,
      'Accept'       : 'application/atom+xml, application/xml, */*',
    };

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
        resolve({
          ok    : res.statusCode >= 200 && res.statusCode < 300,
          status: res.statusCode,
          ms,
          body  : raw.slice(0, 500),
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

    req.end();
  });
}

// ── Middleware ─────────────────────────────────────────────────────────────

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── Routes ─────────────────────────────────────────────────────────────────

app.get('/api/config', (_req, res) => {
  const allTenants = loadTenants();
  res.json({
    environments: Object.entries(ENVS).map(([key, cfg]) => ({
      key,
      label  : cfg.label,
      baseUrl: cfg.baseUrl,
      enabled: !!cfg.baseUrl,
    })),
    tenants: {
      dev : (allTenants.QA      || []).map(t => ({ client: t.Client, systemId: t.SystemID })).filter(t => t.systemId),
      qa  : (allTenants.QA      || []).map(t => ({ client: t.Client, systemId: t.SystemID })).filter(t => t.systemId),
      stg : (allTenants.Staging || []).map(t => ({ client: t.Client, systemId: t.SystemID })).filter(t => t.systemId),
      prod: (allTenants.Prod    || []).map(t => ({ client: t.Client, systemId: t.SystemID })).filter(t => t.systemId),
    },
    checks: CHECKS.map(c => ({
      id     : c.id,
      label  : c.label,
      method : c.method,
      pathTpl: c.pathTpl,
      tag    : c.tag,
      probe  : c.probe,
    })),
    defaults: {
      repositoryId: process.env.CMIS_REPOSITORY_ID || '',
    },
  });
});

app.post('/api/health', async (req, res) => {
  const { env, repositoryId } = req.body;

  if (!env || !repositoryId) {
    return res.status(400).json({ error: 'env y repositoryId son requeridos.' });
  }
  if (!ENVS[env]) {
    return res.status(400).json({ error: 'env inválido. Usa: dev, qa, stg o prod.' });
  }
  if (!ENVS[env].baseUrl) {
    return res.status(400).json({ error: `El ambiente "${env}" no tiene URL configurada aún.` });
  }
  if (!/^[a-z0-9_\-\.]{1,64}$/i.test(repositoryId)) {
    return res.status(400).json({ error: 'repositoryId inválido.' });
  }

  const username = process.env.CMIS_USERNAME || '';
  const password = process.env.CMIS_PASSWORD || '';

  if (!username || !password) {
    return res.status(500).json({ error: 'Credenciales no configuradas en .env (CMIS_USERNAME / CMIS_PASSWORD).' });
  }

  const cfg     = ENVS[env];
  const results = [];

  for (const check of CHECKS) {
    const endpointPath = check.pathTpl.replace('{repoId}', encodeURIComponent(repositoryId));

    const result = await cmisRequest({
      baseUrl     : cfg.baseUrl,
      username,
      password,
      repoId      : repositoryId,
      method      : check.method,
      endpointPath,
    });

    // For probe checks: 4xx means reachable (API up), 2xx also ok, 5xx/0 = down
    let status_label;
    if (check.probe) {
      if (result.status >= 400 && result.status < 500) status_label = 'reachable';
      else if (result.ok) status_label = 'ok';
      else status_label = 'error';
    } else {
      status_label = result.ok ? 'ok' : 'error';
    }

    results.push({
      id          : check.id,
      label       : check.label,
      method      : check.method,
      path        : endpointPath,
      tag         : check.tag,
      probe       : check.probe,
      status_label,
      status      : result.status,
      ms          : result.ms,
      error       : result.error || null,
      body_snippet: result.body ? result.body.slice(0, 200) : null,
    });
  }

  res.json({
    env,
    repositoryId,
    baseUrl   : cfg.baseUrl,
    checkedAt : new Date().toISOString(),
    results,
  });
});

// Single endpoint run
app.post('/api/run', async (req, res) => {
  const { env, repositoryId, checkId, customParams } = req.body;

  if (!env || !repositoryId || !checkId) {
    return res.status(400).json({ error: 'Faltan parámetros requeridos.' });
  }
  if (!ENVS[env] || !ENVS[env].baseUrl) {
    return res.status(400).json({ error: 'env inválido o sin URL.' });
  }
  if (!/^[a-z0-9_\-\.]{1,64}$/i.test(repositoryId)) {
    return res.status(400).json({ error: 'repositoryId inválido.' });
  }

  const username = process.env.CMIS_USERNAME || '';
  const password = process.env.CMIS_PASSWORD || '';

  if (!username || !password) {
    return res.status(500).json({ error: 'Credenciales no configuradas en .env.' });
  }

  const check = CHECKS.find(c => c.id === checkId);
  if (!check) return res.status(404).json({ error: 'checkId no encontrado.' });

  const cfg = ENVS[env];
  let endpointPath = check.pathTpl.replace('{repoId}', encodeURIComponent(repositoryId));

  // Append custom query params if provided
  if (customParams && typeof customParams === 'object') {
    const url = new URL(`https://placeholder${endpointPath}`);
    for (const [k, v] of Object.entries(customParams)) {
      if (v !== '' && v !== null && v !== undefined) {
        // Validate param key/value — alphanumeric + common chars only
        if (/^[a-z0-9_\-\.]{1,64}$/i.test(k) && /^[a-z0-9@._\-\/: ]{0,256}$/i.test(String(v))) {
          url.searchParams.set(k, String(v));
        }
      }
    }
    endpointPath = url.pathname + url.search;
  }

  const result = await cmisRequest({
    baseUrl     : cfg.baseUrl,
    username,
    password,
    repoId      : repositoryId,
    method      : check.method,
    endpointPath,
  });

  res.json({
    env,
    repositoryId,
    checkId,
    method      : check.method,
    url         : `${cfg.baseUrl}${endpointPath}`,
    checkedAt   : new Date().toISOString(),
    status      : result.status,
    ms          : result.ms,
    ok          : result.ok,
    error       : result.error || null,
    body        : result.body || null,
  });
});

// ── Start ──────────────────────────────────────────────────────────────────

app.listen(PORT, '127.0.0.1', () => {
  console.log('');
  console.log('  CMIS Health Dashboard listo');
  console.log(`  Abre http://localhost:${PORT} en tu navegador`);
  console.log('');
});
