"""
Crea borrador Outlook para Dynamic Docs Release 26.06 con imagen embebida.
Destinatario: lista DD Team (diegoj123@gmail.com — 1 miembro)
CC: diego.jacome@quorumsoftware.com
"""
import sys
import os
import win32com.client

sys.stdout.reconfigure(encoding="utf-8")

IMAGE_PATH = r"C:\Users\diego.jacome\OneDrive - Quorum Business Solutions\Pictures\Pie Chart Automation.png"
RELEASE_LINK = "https://archeiojira.atlassian.net/projects/DD/versions/11429/tab/release-report-all-issues"
ADO_LINK     = "https://quorumsoftware.visualstudio.com/Quorum/_workitems/edit/1793785"

try:
    ol = win32com.client.GetActiveObject("Outlook.Application")
except Exception:
    print("ERROR: Outlook no esta abierto.")
    sys.exit(1)

ns = ol.GetNamespace("MAPI")

# ── Resolver listas de distribucion ──────────────────────────────────────
contacts = ns.GetDefaultFolder(10)
dl_mgmt = None
dl_team = None
for item in contacts.Items:
    if item.Class == 69:
        if item.DLName == "Regression Reports [Management]":
            dl_mgmt = item
        elif item.DLName == "Regression Reports [DD Team]":
            dl_team = item

if not dl_mgmt:
    print("ERROR: No se encontro la lista 'Regression Reports [Management]'.")
    sys.exit(1)
if not dl_team:
    print("ERROR: No se encontro la lista 'Regression Reports [DD Team]'.")
    sys.exit(1)

# ── Crear el mail ─────────────────────────────────────────────────────────
mail = ol.CreateItem(0)  # MailItem
mail.Subject = "Dynamic Docs Release 26.06"

# To: Management
recip = mail.Recipients.Add(dl_mgmt.DLName)
recip.Type = 1  # olTo
recip.Resolve()

# CC: DD Team
cc_team = mail.Recipients.Add(dl_team.DLName)
cc_team.Type = 2  # olCC
cc_team.Resolve()

# CC: diego
cc_recip = mail.Recipients.Add("diego.jacome@quorumsoftware.com")
cc_recip.Type = 2  # olCC
cc_recip.Resolve()

# ── Adjuntar imagen y obtener CID ─────────────────────────────────────────
attachment = mail.Attachments.Add(IMAGE_PATH)
attachment.PropertyAccessor.SetProperty(
    "http://schemas.microsoft.com/mapi/proptag/0x3712001F",
    "regression_chart"
)

# ── HTML Body ─────────────────────────────────────────────────────────────
html = f"""
<html>
<head>
<style type="text/css" style="display:none;"> P {{margin-top:0;margin-bottom:0;}} </style>
</head>
<body dir="ltr">

<p style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin-top: 1em; margin-bottom: 1em;">
Hi Team. &nbsp;Version <b>26.06</b> of&nbsp;Dynamic&nbsp;Docs has been released in the <b>Staging</b> environment.
Some test cases related to Integrated Search failed during the automated regression run (adding documents to another
user&#8217;s cart, performing keyword search with invalid operators, unlink document at department level).
These are being addressed in <a href="{ADO_LINK}">#1793785</a> for the next sprint.
</p>

<div style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin: 1em 0px;">
<b>New Features:</b>
</div>
<ul style="margin-top: 0; margin-bottom: 0;">
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Import status update issues</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Audit logging for new Export Service</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Add option to export whitelist from Settings page</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Move Setting page to Client Admin level and rename page</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Rewrite Permission page (Projects and Assign Bulk) for Vue.js rewrite</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Rewrite the Permission page (Location Permissions) using Vue.js</li>
</ul>

<p style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin-top: 1em; margin-bottom: 1em;">
<b>Bug fixes:</b>
</p>
<ul style="margin-top: 0; margin-bottom: 0;">
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Email Ingestion errors for large number of attachments &#8212; part 2 Email Service</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Upload file popup freezes when uploading files via Drag &amp; Drop</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Integrated Search bug fixes: date range and listing file toast</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Email Ingestion endpoint incorrectly treats non-applicable email recipients as processable</li>
</ul>

<p style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin-top: 1em; margin-bottom: 1em;">
<b>Notes:</b>
</p>
<ul style="margin-top: 0; margin-bottom: 0;">
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">The detailed list <a href="{RELEASE_LINK}">is here.</a></li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Next release on Production: <b>April 22<sup>nd</sup>.</b></li>
</ul>

<p style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin-top: 1em; margin-bottom: 1em;">
<b>Testing Notes:</b>
</p>
<ul style="margin-top: 0; margin-bottom: 0;">
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Manual testing was performed on <u>OnDemand QA1</u> and <u>Encino</u> tenants.</li>
  <li style="font-family: Calibri, sans-serif; font-size: 11pt;">
    Automated test run in QA was executed with <b>84% pass rate</b> (208 passed / 41 failed / 249 total &#8212; run R39942).<br>
    <ul style="margin-top: 4px;">
      <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Known issues with Integrated Search are being fixed in <a href="{ADO_LINK}">#1793785</a> for the next sprint.</li>
      <li style="font-family: Calibri, sans-serif; font-size: 11pt;">Some work is still pending to adjust automated tests that involve interaction with the Permissions page.</li>
    </ul>
    <br>
    <img src="cid:regression_chart" style="max-width: 835px; width: 100%;">
  </li>
</ul>

<p style="font-family: Calibri, sans-serif; font-size: 11pt; color: black; margin-top: 1.5em; margin-bottom: 1em;">
If you have any questions, please reach out to the <b>QA team</b>.
</p>

</body>
</html>
"""

mail.HTMLBody = html
mail.Save()  # Guardar como borrador

print("Borrador guardado en Drafts.")
print(f"  Asunto : {mail.Subject}")
print(f"  Para   : Regression Reports [Management]")
print(f"  CC     : Regression Reports [DD Team] + diego.jacome@quorumsoftware.com")
print(f"  Imagen : {os.path.basename(IMAGE_PATH)}")
