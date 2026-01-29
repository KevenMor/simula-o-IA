# 🔄 Como Reiniciar o Frontend

## ⚠️ IMPORTANTE: O Vite precisa ser reiniciado para carregar variáveis do .env

### Passos:

1. **Pare o servidor do frontend** (se estiver rodando):
   - Pressione `Ctrl+C` no terminal do frontend

2. **Reinicie o frontend:**
```powershell
cd "C:\Users\keven\Downloads\IA python\frontend"
npm run dev
```

3. **Verifique no console do navegador (F12):**
   - Deve aparecer: `API_URL: http://localhost:8000`
   - Deve aparecer: `API_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

4. **Se ainda der erro, limpe o cache:**
```powershell
cd "C:\Users\keven\Downloads\IA python\frontend"
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
npm run dev
```

## ✅ Verificação Rápida

Abra o console do navegador (F12) e verifique se aparece:
- `API_URL: http://localhost:8000`
- `API_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

Se aparecer "NÃO CONFIGURADA", o .env não foi carregado. Reinicie o Vite!
