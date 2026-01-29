# Instala pgvector no PostgreSQL 18 (Windows)
# Usa build pre-compilado de: https://github.com/andreiramani/pgvector_pgsql_windows
#
# IMPORTANTE: Execute o PowerShell como Administrador (botao direito -> Executar como administrador)

$ErrorActionPreference = "Stop"
$pgPath = "C:\Program Files\PostgreSQL"
$pgVersions = Get-ChildItem $pgPath -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "^\d+$" }
if (-not $pgVersions) {
    Write-Host "[ERRO] PostgreSQL nao encontrado em $pgPath" -ForegroundColor Red
    exit 1
}
$pgVer = ($pgVersions | Sort-Object Name -Descending | Select-Object -First 1).Name
$pgRoot = "$pgPath\$pgVer"
$pgLib = "$pgRoot\lib"
$pgExt = "$pgRoot\share\extension"

Write-Host "[*] PostgreSQL $pgVer encontrado em $pgRoot" -ForegroundColor Green

# URL do build pre-compilado para PG 18
$zipUrl = "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/0.8.1_18.0.2/vector.v0.8.1-pg18.zip"
$zipPath = "$env:USERPROFILE\Downloads\vector.v0.8.1-pg18.zip"
$extractPath = "$env:USERPROFILE\Downloads\pgvector_install"

# Baixar se nao existir em Downloads
if (-not (Test-Path $zipPath)) {
    Write-Host "[*] Baixando pgvector para PostgreSQL 18..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        Write-Host "[OK] Download concluido: $zipPath" -ForegroundColor Green
    } catch {
        Write-Host "[ERRO] Falha no download. Baixe manualmente:" -ForegroundColor Red
        Write-Host "  $zipUrl" -ForegroundColor White
        Write-Host "  Salve em: $zipPath" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "[OK] Zip ja existe: $zipPath" -ForegroundColor Green
}

# Extrair
if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

# Procurar vector.dll e arquivos da extensao (podem estar na raiz ou em subpasta)
$dll = Get-ChildItem $extractPath -Recurse -Filter "vector.dll" -ErrorAction SilentlyContinue | Select-Object -First 1
$control = Get-ChildItem $extractPath -Recurse -Filter "vector.control" -ErrorAction SilentlyContinue | Select-Object -First 1
$sqlFiles = Get-ChildItem $extractPath -Recurse -Filter "vector--*.sql" -ErrorAction SilentlyContinue

if (-not $dll) {
    Write-Host "[ERRO] vector.dll nao encontrado dentro do zip." -ForegroundColor Red
    Write-Host "Conteudo extraido:" -ForegroundColor Yellow
    Get-ChildItem $extractPath -Recurse | ForEach-Object { Write-Host "  $($_.FullName)" }
    exit 1
}

# Copiar (precisa de permissao de administrador para Program Files)
Write-Host "[*] Copiando arquivos para PostgreSQL (pode pedir permissao de admin)..." -ForegroundColor Cyan
try {
    Copy-Item $dll.FullName -Destination $pgLib -Force
    Write-Host "[OK] vector.dll -> $pgLib" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Nao foi possivel copiar vector.dll. Execute o PowerShell como Administrador." -ForegroundColor Red
    Write-Host "Ou copie manualmente: $($dll.FullName) -> $pgLib" -ForegroundColor Yellow
    exit 1
}

if ($control) {
    Copy-Item $control.FullName -Destination $pgExt -Force
    Write-Host "[OK] vector.control -> $pgExt" -ForegroundColor Green
}
foreach ($f in $sqlFiles) {
    Copy-Item $f.FullName -Destination $pgExt -Force
    Write-Host "[OK] $($f.Name) -> $pgExt" -ForegroundColor Green
}

# Limpar
Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n[OK] pgvector instalado." -ForegroundColor Green
Write-Host "Agora no banco ai_agent_db execute: CREATE EXTENSION IF NOT EXISTS vector;" -ForegroundColor Cyan
Write-Host "Depois rode o script de tabelas: scripts\create_postgres_tables.sql" -ForegroundColor Cyan
