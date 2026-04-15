# run-cmis-load-3mb.ps1
# Corre el test de carga CMIS con documentos de 3MB
#
# Uso:
#   .\scripts\k6\run-cmis-load-3mb.ps1                             # QA, 5 VUs x 100 iter
#   .\scripts\k6\run-cmis-load-3mb.ps1 -environment stg            # Staging
#   .\scripts\k6\run-cmis-load-3mb.ps1 -environment prod           # Production
#   .\scripts\k6\run-cmis-load-3mb.ps1 -skipCleanup                # deja docs, guarda IDs
#   .\scripts\k6\run-cmis-load-3mb.ps1 -vus 1 -iter 1              # dry-run
#   .\scripts\k6\run-cmis-load-3mb.ps1 -vus 5 -iter 10             # prueba corta

param(
    [int]$vus         = 5,
    [int]$iter        = 100,
    [string]$environment = "qa",    # qa | stg | prod
    [switch]$skipCleanup
)

# Recargar PATH para que k6 este disponible
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Leer credenciales del .env segun el environment
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: No se encontro $envFile" -ForegroundColor Red
    exit 1
}
$prefix = $environment.ToUpper()
$envVars = @{}
Get-Content $envFile | Where-Object { $_ -match "^${prefix}_" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $envVars[$parts[0].Substring($prefix.Length + 1)] = $parts[1]
}
$baseUrl   = $envVars["BASE_URL"]
$repoId    = $envVars["REPO_ID"]
$docId     = $envVars["DOC_ID"]
$folderId  = $envVars["FOLDER_ID"]
$username  = $envVars["USERNAME"]
$password  = $envVars["PASSWORD"]

if (-not $repoId) {
    Write-Host "ERROR: Environment '$environment' no encontrado o no configurado en .env" -ForegroundColor Red
    exit 1
}

# Carpeta de resultados centralizada por environment
$resultsDir = "performance\cmis-api\$(Get-Date -Format 'yyyy-MM-dd')\raw-data"
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

$estMin  = [math]::Round($iter * 20 / 60)
$estMax  = [math]::Round($iter * 40 / 60)
$storage = [math]::Round($vus * $iter * 3 / 1024, 1)

Write-Host ""
Write-Host "=== CMIS 3MB Load Test ($($environment.ToUpper())) ===" -ForegroundColor Cyan
Write-Host "  VUs       : $vus"
Write-Host "  Iterations: $iter per VU"
Write-Host "  Total uploads: $($vus * $iter) documentos de 3MB"
Write-Host "  Storage estimado: ~$storage GB en $($environment.ToUpper()) (se limpia al terminar)"
Write-Host "  Duracion estimada: $estMin - $estMax minutos"
Write-Host "  Resultados en: $resultsDir\"
if ($skipCleanup) { Write-Host "  SKIP_CLEANUP activo -- los docs se dejan en $($environment.ToUpper()), IDs guardados" -ForegroundColor Yellow }
Write-Host ""

$ts = Get-Date -Format "yyyy-MM-dd-HH-mm"
$requestsFile = "$resultsDir\$($environment)-run-$ts-requests.ndjson"

k6 run `
    --env VUS=$vus `
    --env ITERATIONS=$iter `
    --env CMIS_BASE_URL=$baseUrl `
    --env CMIS_REPO_ID=$repoId `
    --env CMIS_DOC_ID=$docId `
    --env CMIS_FOLDER_ID=$folderId `
    --env CMIS_USERNAME=$username `
    --env CMIS_PASSWORD=$password `
    --env CMIS_ENV=$environment `
    --env CMIS_OBJECT_TYPE=$($envVars['OBJECT_TYPE']) `
    --env SKIP_TEARDOWN=$(if ($skipCleanup) { "true" } else { "false" }) `
    --out "json=$requestsFile" `
    scripts/k6/cmis-load-3mb.js

if ($skipCleanup) {
    Write-Host "`nCapturando IDs de documentos k6perf creados..." -ForegroundColor Cyan
    $env:PYTHONIOENCODING = "utf-8"
    python scripts/k6/collect_k6perf_ids.py --env $environment
}

