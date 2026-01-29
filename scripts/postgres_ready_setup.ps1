# Executa apos o PostgreSQL estar RODANDO (extensao vector + tabelas)
# Uso: .\scripts\postgres_ready_setup.ps1
# Requer: PostgreSQL 18 rodando na porta 5432, .env com POSTGRES_* preenchidos

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Carregar senha do .env
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERRO] Arquivo .env nao encontrado em $projectRoot" -ForegroundColor Red
    exit 1
}
$password = (Get-Content $envFile | Where-Object { $_ -match "^POSTGRES_PASSWORD=" }) -replace "POSTGRES_PASSWORD=", ""
if (-not $password) {
    Write-Host "[ERRO] POSTGRES_PASSWORD nao encontrado no .env" -ForegroundColor Red
    exit 1
}

$pgBin = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$env:PGPASSWORD = $password
$connArgs = @("-U", "ai_agent_user", "-h", "localhost", "-d", "ai_agent_db", "-p", "5432")

# Testar conexao
Write-Host "[*] Testando conexao com PostgreSQL..." -ForegroundColor Cyan
$test = & $pgBin @connArgs -c "SELECT 1;" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Nao foi possivel conectar. PostgreSQL esta rodando na porta 5432?" -ForegroundColor Red
    Write-Host $test
    exit 1
}
Write-Host "[OK] Conexao OK" -ForegroundColor Green

# Criar extensao vector
Write-Host "[*] Criando extensao vector..." -ForegroundColor Cyan
& $pgBin @connArgs -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Extensao vector criada/ja existe" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Falha ao criar extensao vector (pode ja existir)" -ForegroundColor Yellow
}

# Criar tabelas
$sqlFile = Join-Path $scriptDir "create_postgres_tables.sql"
if (Test-Path $sqlFile) {
    Write-Host "[*] Criando tabelas..." -ForegroundColor Cyan
    & $pgBin @connArgs -f $sqlFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Tabelas criadas" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Erro ao criar tabelas (verifique manualmente)" -ForegroundColor Yellow
    }
}

$env:PGPASSWORD = $null
Write-Host "`n[OK] Setup concluido. Banco ai_agent_db pronto para uso." -ForegroundColor Green
