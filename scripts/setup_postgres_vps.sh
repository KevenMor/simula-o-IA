#!/bin/bash
# Script para configurar PostgreSQL com pgvector na VPS

set -e

echo "🐘 Configurando PostgreSQL na VPS..."

# 1. Instalar PostgreSQL
echo "📦 Instalando PostgreSQL..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# 2. Instalar dependências para pgvector
echo "📦 Instalando dependências para pgvector..."
sudo apt install -y build-essential postgresql-server-dev-14 git

# 3. Instalar pgvector
echo "📦 Instalando pgvector..."
cd /tmp
if [ -d "pgvector" ]; then
    rm -rf pgvector
fi
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# 4. Criar banco de dados
echo "🗄️ Criando banco de dados..."
sudo -u postgres psql <<EOF
-- Criar banco
CREATE DATABASE ai_agent_db;

-- Criar usuário (altere a senha!)
CREATE USER ai_agent_user WITH PASSWORD 'ALTERE_ESTA_SENHA';

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE ai_agent_db TO ai_agent_user;
EOF

# 5. Configurar pgvector e criar tabelas
echo "🔧 Configurando pgvector e criando tabelas..."
sudo -u postgres psql -d ai_agent_db <<EOF
-- Criar extensão
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar tabelas
CREATE TABLE IF NOT EXISTS knowledge_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_base_id VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS knowledge_documents_embedding_idx 
ON knowledge_documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_id 
ON knowledge_documents(knowledge_base_id);

-- Dar permissões
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_agent_user;
EOF

echo "✅ PostgreSQL configurado com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "1. Atualize o .env com as credenciais:"
echo "   POSTGRES_HOST=localhost"
echo "   POSTGRES_PORT=5432"
echo "   POSTGRES_DB=ai_agent_db"
echo "   POSTGRES_USER=ai_agent_user"
echo "   POSTGRES_PASSWORD=ALTERE_ESTA_SENHA"
echo ""
echo "2. Instale as dependências Python:"
echo "   pip install psycopg2-binary"
