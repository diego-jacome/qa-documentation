'use strict';

const express = require('express');
const https   = require('https');
const path    = require('path');
require('dotenv').config({ path: path.join(__dirname, '../ado/.env') });

process.on('uncaughtException',  err => console.error('[uncaughtException]', err.message));
process.on('unhandledRejection', err => console.error('[unhandledRejection]', err?.message || err));

const app  = express();
const PORT = 3001;

const ADO_URL     = (process.env.ADO_URL     || '').replace(/\/$/, '');
const ADO_PROJECT = (process.env.ADO_PROJECT || '');
const ADO_PAT     = (process.env.ADO_PAT     || '');

if (!ADO_URL || !ADO_PROJECT || !ADO_PAT) {
  console.error('\n  ❌  Faltan variables ADO_URL / ADO_PROJECT / ADO_PAT en scripts/ado/.env\n');
  process.exit(1);
}

const TEAM_ID  = 'afb630ad-4f72-4eae-b6aa-1bfa3436052b';
const AREA_PATH = 'Quorum\\North America\\Upstream\\Dynamic Docs RnD';
const AUTH_B64  = Buffer.from(`:${ADO_PAT}`).toString('base64');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── helpers ────────────────────────────────────────────────────────────────

function adoGet(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: { Authorization: `Basic ${AUTH_B64}`, Accept: 'application/json' },
      timeout: 20000,
    }, (res) => {
      let raw = '';
      res.on('data', c => { raw += c; });
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { reject(new Error('Respuesta no-JSON de ADO')); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout conectando a ADO')); });
  });
}

function adoPost(url, body) {
  return new Promise((resolve, reject) => {
    const payload  = JSON.stringify(body);
    const parsed   = new URL(url);
    const options  = {
      hostname : parsed.hostname,
      path     : parsed.pathname + parsed.search,
      method   : 'POST',
      headers  : {
        Authorization  : `Basic ${AUTH_B64}`,
        'Content-Type' : 'application/json',
        Accept         : 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
      timeout: 20000,
    };
    const req = https.request(options, (res) => {
      let raw = '';
      res.on('data', c => { raw += c; });
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { reject(new Error('Respuesta no-JSON de ADO')); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout en POST a ADO')); });
    req.write(payload);
    req.end();
  });
}

// ── routes ─────────────────────────────────────────────────────────────────

// GET /api/sprints — lista los sprints del equipo
app.get('/api/sprints', async (_req, res) => {
  try {
    const url    = `${ADO_URL}/${ADO_PROJECT}/${TEAM_ID}/_apis/work/teamsettings/iterations?api-version=7.1`;
    const result = await adoGet(url);
    if (result.status !== 200) {
      return res.status(result.status).json({ error: `ADO devolvió ${result.status}`, detail: result.body });
    }
    res.json(result.body);
  } catch (e) {
    res.status(502).json({ error: e.message });
  }
});

// GET /api/workitems?iterationPath=Quorum\PI 26.1\26.1.1
app.get('/api/workitems', async (req, res) => {
  const iterationPath = req.query.iterationPath;
  if (!iterationPath) return res.status(400).json({ error: 'iterationPath es requerido' });

  // Solo permitir rutas que comiencen con "Quorum"
  if (!/^Quorum(\\[^"<>|*?]+)*$/.test(iterationPath)) {
    return res.status(400).json({ error: 'iterationPath inválido' });
  }

  try {
    // 1. WIQL → IDs
    const wiqlUrl = `${ADO_URL}/${ADO_PROJECT}/_apis/wit/wiql?api-version=7.1`;
    const wiql = {
      query: `SELECT [System.Id] FROM WorkItems WHERE [System.IterationPath] = '${iterationPath}' AND [System.AreaPath] UNDER '${AREA_PATH}' AND [System.WorkItemType] IN ('User Story','Bug') ORDER BY [System.State] ASC, [Microsoft.VSTS.Common.Priority] ASC`,
    };
    const wiqlResult = await adoPost(wiqlUrl, wiql);
    const ids = (wiqlResult.body.workItems || []).map(w => w.id);
    if (ids.length === 0) return res.json({ value: [] });

    // 2. Batch fetch detalles (chunks de 200)
    const fields = [
      'System.Id',
      'System.Title',
      'System.WorkItemType',
      'System.State',
      'System.AssignedTo',
      'Microsoft.VSTS.Common.Priority',
      'System.Tags',
      'System.ChangedDate',
      'Microsoft.VSTS.Scheduling.StoryPoints',
      'System.CreatedDate',
    ].join(',');

    const items = [];
    for (let i = 0; i < ids.length; i += 200) {
      const chunk  = ids.slice(i, i + 200);
      const url    = `${ADO_URL}/${ADO_PROJECT}/_apis/wit/workitems?ids=${chunk.join(',')}&fields=${encodeURIComponent(fields)}&api-version=7.1`;
      const result = await adoGet(url);
      items.push(...(result.body.value || []));
    }

    res.json({ value: items });
  } catch (e) {
    res.status(502).json({ error: e.message });
  }
});

// POST /api/state-dates — recibe { ids: [...], state: "Test" }
// Devuelve { [id]: "2026-04-09" } con la fecha en que cada item entró al estado
app.post('/api/state-dates', async (req, res) => {
  const { ids, state } = req.body;
  if (!Array.isArray(ids) || !ids.length || !state) {
    return res.status(400).json({ error: 'ids (array) y state son requeridos' });
  }
  if (ids.length > 50) return res.status(400).json({ error: 'Máximo 50 IDs por llamada' });
  if (!/^[A-Za-z ]+$/.test(state)) return res.status(400).json({ error: 'state inválido' });
  if (!ids.every(id => Number.isInteger(Number(id)) && Number(id) > 0)) {
    return res.status(400).json({ error: 'IDs inválidos' });
  }

  try {
    const results = {};
    await Promise.all(ids.map(async (id) => {
      const url  = `${ADO_URL}/${ADO_PROJECT}/_apis/wit/workitems/${id}/updates?api-version=7.1`;
      const r    = await adoGet(url);
      const updates = r.body.value || [];
      // Buscar la última revisión donde State cambió al estado pedido
      const match = [...updates].reverse().find(u =>
        u.fields?.['System.State']?.newValue === state
      );
      results[id] = match ? match.fields['System.ChangedDate']?.newValue || null : null;
    }));
    res.json(results);
  } catch (e) {
    res.status(502).json({ error: e.message });
  }
});

// ── start ──────────────────────────────────────────────────────────────────
app.listen(PORT, '127.0.0.1', () => {
  console.log('');
  console.log('  ✅  ADO Dashboard listo');
  console.log(`  👉  Abre http://localhost:${PORT} en tu navegador`);
  console.log('');
});
