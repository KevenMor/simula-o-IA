# 🚀 Comandos para Iniciar os Servidores

## Backend (FastAPI)

### Terminal 1 - Backend
```powershell
cd "C:\Users\keven\Downloads\IA python"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Ou em uma linha:**
```powershell
cd "C:\Users\keven\Downloads\IA python"; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Acesse:** http://localhost:8000
**Docs:** http://localhost:8000/docs

---

## Frontend (React + Vite)

### Terminal 2 - Frontend
```powershell
cd "C:\Users\keven\Downloads\IA python\frontend"
npm run dev
```

**Ou em uma linha:**
```powershell
cd "C:\Users\keven\Downloads\IA python\frontend"; npm run dev
```

**Acesse:** http://localhost:3000

---

## ⚡ Iniciar Ambos de Uma Vez (PowerShell)

Crie um arquivo `start.ps1` na raiz do projeto:

```powershell
# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\keven\Downloads\IA python'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# Aguardar 2 segundos
Start-Sleep -Seconds 2

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\keven\Downloads\IA python\frontend'; npm run dev"

Write-Host "✅ Servidores iniciados!"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
```

Execute com:
```powershell
.\start.ps1
```

---

## 📋 Verificar se Estão Rodando

### Backend
```powershell
curl http://localhost:8000/health
```

### Frontend
```powershell
curl http://localhost:3000
```

---

## 🛑 Parar os Servidores

### Backend
Pressione `Ctrl+C` no terminal do backend

### Frontend
Pressione `Ctrl+C` no terminal do frontend

### Parar Todos (PowerShell)
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Python*"} | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```
