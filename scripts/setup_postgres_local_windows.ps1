# Script para configurar PostgreSQL local no Windows

Write-Host "[*] Configurando PostgreSQL Local no Windows..." -ForegroundColor Green

# Verificar se PostgreSQL esta instalado
$pgPath = "C:\Program Files\PostgreSQL"
$pgVersions = Get-ChildItem $pgPath -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "^\d+$" }

if (-not $pgVersions) {
    Write-Host "[ERRO] PostgreSQL nao encontrado!" -ForegroundColor Red
    Write-Host "`nInstale PostgreSQL primeiro:" -ForegroundColor Yellow
    Write-Host "   1. Baixe: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "   2. Execute o instalador" -ForegroundColor White
    Write-Host "   3. Anote a senha do usuario 'postgres'" -ForegroundColor White
    Write-Host "   4. Execute este script novamente" -ForegroundColor White
    exit 1
}

$latestVersion = ($pgVersions | Sort-Object Name -Descending | Select-Object -First 1).Name
$pgBin = "$pgPath\$latestVersion\bin"
$psql = "$pgBin\psql.exe"

Write-Host "[OK] PostgreSQL $latestVersion encontrado" -ForegroundColor Green

# Solicitar senha do postgres
$postgresPassword = Read-Host "Digite a senha do usuario 'postgres'"

# Configurar variavel de ambiente temporaria
$env:PGPASSWORD = $postgresPassword

# Criar banco de dados
Write-Host "`n[*] Criando banco de dados..." -ForegroundColor Cyan
& $psql -U postgres -c "CREATE DATABASE ai_agent_db;" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Banco 'ai_agent_db' criado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Banco pode ja existir (continuando...)" -ForegroundColor Yellow
}

# Criar usuario
Write-Host "[*] Criando usuario..." -ForegroundColor Cyan
$userPassword = Read-Host "Digite a senha para o usuario 'ai_agent_user'"
& $psql -U postgres -c "CREATE USER ai_agent_user WITH PASSWORD '$userPassword';" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Usuario 'ai_agent_user' criado" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Usuario pode ja existir (continuando...)" -ForegroundColor Yellow
}

# Dar permissoes
Write-Host "[*] Configurando permissoes..." -ForegroundColor Cyan
& $psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_agent_db TO ai_agent_user;" 2>&1 | Out-Null
Write-Host "[OK] Permissoes configuradas" -ForegroundColor Green

# Criar extensao pgvector
Write-Host "`n[*] Configurando pgvector..." -ForegroundColor Cyan
Write-Host "[AVISO] pgvector precisa ser instalado manualmente no Windows" -ForegroundColor Yellow
Write-Host "   Veja: docs/POSTGRES_LOCAL_WINDOWS.md" -ForegroundColor Yellow

# Tentar criar extensao (pode falhar se pgvector nao estiver instalado)
& $psql -U postgres -d ai_agent_db -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Extensao pgvector criada" -ForegroundColor Green
} else {
    Write-Host "[AVISO] pgvector nao encontrado - instale manualmente" -ForegroundColor Yellow
}

# Criar tabelas
Write-Host "`n[*] Criando tabelas..." -ForegroundColor Cyan
$sqlFile = Join-Path $PSScriptRoot "create_postgres_tables.sql"
if (Test-Path $sqlFile) {
    & $psql -U postgres -d ai_agent_db -f $sqlFile 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Tabelas criadas" -ForegroundColor Green
    } else {
        Write-Host "[AVISO] Erro ao criar tabelas (verifique manualmente)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[AVISO] Arquivo SQL nao encontrado: $sqlFile" -ForegroundColor Yellow
}

# Dar permissoes nas tabelas
Write-Host "[*] Configurando permissoes nas tabelas..." -ForegroundColor Cyan
& $psql -U postgres -d ai_agent_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_agent_user;" 2>&1 | Out-Null
& $psql -U postgres -d ai_agent_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_agent_user;" 2>&1 | Out-Null
Write-Host "[OK] Permissoes nas tabelas configuradas" -ForegroundColor Green

# Limpar senha da memoria
$env:PGPASSWORD = $null

Write-Host "`n[OK] Configuracao concluida!" -ForegroundColor Green
Write-Host "`nAdicione ao seu .env:" -ForegroundColor Cyan
Write-Host "POSTGRES_HOST=localhost" -ForegroundColor White
Write-Host "POSTGRES_PORT=5432" -ForegroundColor White
Write-Host "POSTGRES_DB=ai_agent_db" -ForegroundColor White
Write-Host "POSTGRES_USER=ai_agent_user" -ForegroundColor White
Write-Host ("POSTGRES_PASSWORD=" + $userPassword) -ForegroundColor White
