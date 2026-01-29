# Script para iniciar Backend e Frontend

Write-Host "🚀 Iniciando servidores..." -ForegroundColor Green

# Backend
Write-Host "`n📦 Iniciando Backend (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Aguardar 2 segundos
Start-Sleep -Seconds 2

# Frontend
Write-Host "📦 Iniciando Frontend (React)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`n✅ Servidores iniciados!" -ForegroundColor Green
Write-Host "`n📍 Acesse:" -ForegroundColor Yellow
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Docs API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n⚠️  Para parar, feche as janelas do PowerShell ou pressione Ctrl+C" -ForegroundColor Gray
