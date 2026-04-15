import http from 'k6/http';
import encoding from 'k6/encoding';

const BASE_URL      = 'https://api-qa.archeiotech.com';
const REPOSITORY_ID = '63';
const DOCUMENT_ID   = 'document-652392';
const FOLDER_ID     = '2307';
const USERNAME      = 'dynamicdocs_user';
const PASSWORD      = 'j!h1b5DOfH';

const authHeader = `Basic ${encoding.b64encode(`${USERNAME}:${PASSWORD}`)}`;
const baseHeaders = { Authorization: authHeader };
const xmlHeaders  = { Authorization: authHeader, 'Content-Type': 'application/atom+xml' };

export default function () {
  // getObject
  const r1 = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/id?id=${DOCUMENT_ID}`,
    { headers: baseHeaders }
  );
  console.log(`getObject => status=${r1.status} body=${r1.body.substring(0, 300)}`);

  // getContentStream
  const r2 = http.get(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/content?id=${DOCUMENT_ID}`,
    { headers: baseHeaders }
  );
  console.log(`getContentStream => status=${r2.status} body=${r2.body.substring(0, 300)}`);

  // createDocument (small doc)
  const docName = `perf-debug-${Date.now()}.txt`;
  const body = `<?xml version="1.0" encoding="UTF-8"?>
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

  const r3 = http.post(
    `${BASE_URL}/cmis/version/1.1/atom/${REPOSITORY_ID}/children?id=folder-${FOLDER_ID}`,
    body,
    { headers: xmlHeaders }
  );
  console.log(`createDocument => status=${r3.status} body=${r3.body.substring(0, 800)}`);
}
