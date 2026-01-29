# 🐘 Configurando PostgreSQL na VPS

## ✅ Sim, é totalmente possível!

O Supabase usa PostgreSQL com a extensão `pgvector`. Você pode usar seu próprio PostgreSQL na VPS.

## 📋 Pré-requisitos

- VPS com Ubuntu/Debian
- Acesso root ou sudo
- PostgreSQL 12+ instalado

## 🔧 Instalação do PostgreSQL na VPS

### 1. Instalar PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib -y

# Verificar versão
psql --version
```

### 2. Instalar pgvector (extensão para vetores)

```bash
# Instalar dependências
sudo apt install build-essential postgresql-server-dev-14 git -y

# Clonar e compilar pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Ou instalar via apt (se disponível)
sudo apt install postgresql-14-pgvector -y
```

### 3. Criar Banco de Dados

```bash
# Acessar PostgreSQL como usuário postgres
sudo -u postgres psql

# Criar banco de dados
CREATE DATABASE ai_agent_db;

# Criar usuário
CREATE USER ai_agent_user WITH PASSWORD 'sua_senha_segura_aqui';

# Dar permissões
GRANT ALL PRIVILEGES ON DATABASE ai_agent_db TO ai_agent_user;

# Sair
\q
```

### 4. Configurar pgvector

```bash
# Acessar o banco criado
sudo -u postgres psql -d ai_agent_db

# Criar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar se foi criada
\dx

# Sair
\q
```

### 5. Criar Tabelas

```bash
# Acessar o banco
sudo -u postgres psql -d ai_agent_db

# Executar SQL
```

```sql
-- Criar extensão pgvector (se ainda não criou)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de documentos da base de conhecimento
CREATE TABLE knowledge_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_base_id VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca vetorial
CREATE INDEX ON knowledge_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice para knowledge_base_id (para filtros)
CREATE INDEX idx_knowledge_base_id ON knowledge_documents(knowledge_base_id);

-- Tabela de logs de conversação (opcional)
CREATE TABLE conversation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(100) NOT NULL,
  customer_id VARCHAR(100),
  message TEXT NOT NULL,
  response TEXT,
  sentiment VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Dar permissões ao usuário
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_agent_user;
```

## 🔐 Configurar Acesso Remoto (Opcional)

Se quiser acessar o PostgreSQL de fora da VPS:

### 1. Editar `postgresql.conf`

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Encontrar e descomentar:
```
listen_addresses = '*'
```

### 2. Editar `pg_hba.conf`

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Adicionar no final:
```
host    all             all             0.0.0.0/0               md5
```

### 3. Reiniciar PostgreSQL

```bash
sudo systemctl restart postgresql
```

### 4. Configurar Firewall

```bash
sudo ufw allow 5432/tcp
```

## ⚙️ Atualizar Configuração do Backend

### 1. Atualizar `.env`

```env
# Substituir Supabase por PostgreSQL direto
# SUPABASE_URL=https://seu-projeto.supabase.co
# SUPABASE_KEY=sua-chave

# Usar PostgreSQL direto
POSTGRES_HOST=seu-ip-vps-ou-localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_agent_db
POSTGRES_USER=ai_agent_user
POSTGRES_PASSWORD=sua_senha_segura_aqui
```

### 2. Instalar biblioteca Python

```bash
pip install psycopg2-binary pgvector
```

## 🔄 Alternativa: Usar psycopg2 direto

Se preferir não usar a biblioteca do Supabase, podemos criar um cliente PostgreSQL direto.

## 📝 Vantagens de usar PostgreSQL próprio

✅ **Controle total** sobre o banco
✅ **Sem limites** do plano do Supabase
✅ **Mais barato** (só paga a VPS)
✅ **Mesma funcionalidade** (pgvector)
✅ **Backup próprio**

## ⚠️ Desvantagens

❌ Precisa gerenciar backups manualmente
❌ Precisa manter PostgreSQL atualizado
❌ Precisa configurar segurança

## 🚀 Próximos Passos

Quer que eu:
1. Crie um script de migração do Supabase para PostgreSQL?
2. Atualize o código para usar PostgreSQL direto?
3. Crie scripts de backup automático?
