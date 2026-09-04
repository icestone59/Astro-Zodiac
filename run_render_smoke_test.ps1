param(
    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl
)

$env:DATABASE_URL = $DatabaseUrl

Write-Host "Running Astro-Zodiac T23 Render PostgreSQL smoke test..."
python .\t22_smoke_test.py
exit $LASTEXITCODE
