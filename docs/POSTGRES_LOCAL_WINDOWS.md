# 🐘 PostgreSQL Local no Windows - Setup para Testes

## 🎯 Objetivo

Configurar PostgreSQL localmente no Windows para testar como se fosse produção, antes de subir na VPS.

## 📦 Instalação

### Opção 1: Instalador Windows (Recomendado)

1. **Baixar PostgreSQL:**
   - Acesse: https://www.postgresql.org/download/windows/
   - Baixe o instalador (ex: postgresql-15.x-windows-x64.exe)

2. **Instalar:**
   - Execute o instalador
   - Escolha porta padrão: `5432`
   - Defina senha para usuário `postgres` (anote essa senha!)
   - Complete a instalação

3. **Verificar instalação:**
```powershell
# Verificar se está rodando
Get-Service -Name postgresql*
```

### Se o serviço não aparecer (postgresql-x64-18)

Às vezes o instalador não registra o serviço. Opções:

1. **Iniciar pelo pgAdmin (se instalou junto):**
   - Abra **pgAdmin 4** no Menu Iniciar
   - Conecte ao servidor (senha do usuário `postgres`)
   - O pgAdmin pode iniciar o servidor ao conectar

2. **Reexecutar o instalador:**
   - Execute de novo o instalador do PostgreSQL 18
   - Escolha **Modify** e marque a opção de instalar/registrar o serviço

3. **Iniciar manualmente (desenvolvimento):**
   - Abra um **Prompt de Comando ou PowerShell como Administrador**
   - Execute:
   ```cmd
   "C:\Program Files\PostgreSQL\18\bin\postgres.exe" -D "C:\Program Files\PostgreSQL\18\data"
   ```
   - Deixe a janela aberta (o servidor roda em primeiro plano)
   - Em outro terminal, use `psql` ou a API do projeto

### Opção 2: Via Chocolatey

```powershell
# Instalar Chocolatey (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar PostgreSQL
choco install postgresql15 -y
```

## 🔧 Configurar pgvector

### 1. Baixar pgvector

```powershell
# Criar diretório temporário
cd $env:TEMP
mkdir pgvector -ErrorAction SilentlyContinue
cd pgvector

# Baixar pgvector (versão Windows)
# Opção 1: Via Git (se tiver)
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git

# Opção 2: Baixar ZIP
# Acesse: https://github.com/pgvector/pgvector/releases
# Baixe: pgvector-0.5.1-windows-x64.zip
# Extraia no diretório atual
```

### 2. Compilar pgvector (Windows)

**Requisitos:**
- Visual Studio Build Tools
- Ou usar versão pré-compilada

**Opção mais fácil: Usar versão pré-compilada**

1. Baixar DLL pré-compilada:
   - Acesse: https://github.com/pgvector/pgvector/releases
   - Baixe: `pgvector-0.5.1-windows-x64.zip`

2. Extrair e copiar:
```powershell
# Encontrar diretório do PostgreSQL
$pgDir = "C:\Program Files\PostgreSQL\15"  # Ajuste a versão

# Copiar DLL para lib
Copy-Item "vector.dll" "$pgDir\lib\"

# Copiar arquivos SQL para share/extension
Copy-Item "vector.control" "$pgDir\share\extension\"
Copy-Item "vector--*.sql" "$pgDir\share\extension\"
```

### 3. Criar Extensão

```powershell
# Acessar PostgreSQL
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres

# No prompt do PostgreSQL:
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

## 🗄️ Criar Banco de Dados

### Via PowerShell

```powershell
# Conectar ao PostgreSQL
$env:PGPASSWORD = "sua_senha_postgres"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE ai_agent_db;"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER ai_agent_user WITH PASSWORD 'sua_senha_aqui';"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_agent_db TO ai_agent_user;"
```

### Via pgAdmin (Interface Gráfica)

1. Abrir pgAdmin (instalado com PostgreSQL)
2. Conectar ao servidor (senha do postgres)
3. Botão direito em "Databases" → Create → Database
   - Name: `ai_agent_db`
4. Botão direito em "Login/Group Roles" → Create → Login/Group Role
   - Name: `ai_agent_user`
   - Password: `sua_senha_aqui`
   - Privileges: Can login? ✅

## 📝 Criar Tabelas

```powershell
# Executar script SQL
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d ai_agent_db -f "scripts\create_postgres_tables.sql"
```

Ou via pgAdmin:
1. Botão direito em `ai_agent_db` → Query Tool
2. Colar conteúdo de `scripts/create_postgres_tables.sql`
3. Executar (F5)

## ⚙️ Configurar .env

Atualize seu `.env`:

```env
# Comentar Supabase (ou manter para fallback)
# SUPABASE_URL=...
# SUPABASE_KEY=...

# Adicionar PostgreSQL local
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agent_db
POSTGRES_USER=ai_agent_user
POSTGRES_PASSWORD=sua_senha_aqui
```

## 🧪 Testar Conexão

```powershell
# Testar conexão
python -c "
import asyncpg
import asyncio

async def test():
    conn = await asyncpg.connect(
        'postgresql://ai_agent_user:sua_senha_aqui@localhost:5432/ai_agent_db'
    )
    result = await conn.fetchval('SELECT version()')
    print('✅ Conectado!')
    print(result)
    await conn.close()

asyncio.run(test())
"
```

## 🚀 Próximos Passos

1. ✅ PostgreSQL instalado
2. ✅ pgvector configurado
3. ✅ Banco criado
4. ✅ Tabelas criadas
5. ✅ .env configurado
6. ✅ Testar conexão

Agora você pode testar localmente como se fosse produção!

## 📋 Comandos Úteis

```powershell
# Iniciar PostgreSQL
Start-Service postgresql-x64-15

# Parar PostgreSQL
Stop-Service postgresql-x64-15

# Ver status
Get-Service postgresql-x64-15

# Acessar psql
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d ai_agent_db

# Backup
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -d ai_agent_db -F c -f backup.dump

# Restore
& "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" -U postgres -d ai_agent_db backup.dump
```
