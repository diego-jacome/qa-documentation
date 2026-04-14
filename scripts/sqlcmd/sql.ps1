# Helper para conectarse a SQL Server via sqlcmd
# Uso: .\scripts\sqlcmd\sql.ps1 qa
#      .\scripts\sqlcmd\sql.ps1 stg DynamicDocsTest
#      .\scripts\sqlcmd\sql.ps1 stg DynamicDocsTest "SELECT TOP 5 * FROM Content"

param(
    [Parameter(Mandatory, Position=0)][ValidateSet("qa","stg","prd")][string]$Target,
    [Parameter(Position=1)][string]$Database = "",
    [Parameter(Position=2)][string]$Sql = ""
)

# Refrescar PATH para encontrar sqlcmd
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Cargar .env
$envFile = Join-Path $PSScriptRoot ".env"
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+)=(.+)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}

switch ($Target) {
    "qa"  { $server = $env:SQL_QA_SERVER;  $user = $env:SQL_QA_USER;  $pass = $env:SQL_QA_PASSWORD }
    "stg" { $server = $env:SQL_STG_SERVER; $user = $env:SQL_STG_USER; $pass = $env:SQL_STG_PASSWORD }
    "prd" { $server = $env:SQL_PRD_SERVER; $user = $env:SQL_PRD_USER; $pass = $env:SQL_PRD_PASSWORD }
}

$cmdArgs = @("-S", $server, "-U", $user, "-P", $pass, "-l", "30")
if ($Database) { $cmdArgs += @("-d", $Database) }
if ($Sql)      { $cmdArgs += @("-Q", $Sql, "-y", "40", "-Y", "40") }

sqlcmd @cmdArgs
