-- Script SQL para criar tabelas no PostgreSQL com pgvector
-- Execute este script no seu banco PostgreSQL

-- Criar extensão pgvector (se ainda não criou)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de documentos da base de conhecimento
CREATE TABLE IF NOT EXISTS knowledge_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_base_id VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca vetorial (usando ivfflat para performance)
CREATE INDEX IF NOT EXISTS knowledge_documents_embedding_idx 
ON knowledge_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Índice para knowledge_base_id (para filtros rápidos)
CREATE INDEX IF NOT EXISTS idx_knowledge_base_id 
ON knowledge_documents(knowledge_base_id);

-- Tabela de logs de conversação (opcional)
CREATE TABLE IF NOT EXISTS conversation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id VARCHAR(100) NOT NULL,
  customer_id VARCHAR(100),
  message TEXT NOT NULL,
  response TEXT,
  sentiment VARCHAR(50),
  confidence_score FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para logs
CREATE INDEX IF NOT EXISTS idx_conversation_logs_tenant 
ON conversation_logs(tenant_id, created_at DESC);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_knowledge_documents_updated_at ON knowledge_documents;
CREATE TRIGGER update_knowledge_documents_updated_at
    BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Dar permissões (ajuste o usuário conforme necessário)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_agent_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_agent_user;
