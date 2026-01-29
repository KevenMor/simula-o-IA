# 💾 Uso de Espaço na VPS - Análise Detalhada

## 📊 Resumo Rápido

**Uso estimado de espaço:**
- PostgreSQL + pgvector: ~200-500 MB (base)
- Embeddings: ~6 KB por documento
- Dados de treinamento: ~1-10 MB por 1000 documentos
- **Total estimado: < 1 GB para começar**

## 🔍 Análise Detalhada

### 1. PostgreSQL + pgvector

**Espaço base:**
- PostgreSQL instalado: ~150-200 MB
- Extensão pgvector: ~5-10 MB
- Estrutura de tabelas: ~1-5 MB
- **Total base: ~200-500 MB**

### 2. Embeddings (Vetores)

**Cálculo:**
- Cada embedding: 1536 dimensões (OpenAI text-embedding-3-small)
- Cada dimensão: 4 bytes (float32)
- **Por embedding: 1536 × 4 = 6.144 KB ≈ 6 KB**

**Exemplos:**
- 100 documentos: ~600 KB
- 1.000 documentos: ~6 MB
- 10.000 documentos: ~60 MB
- 100.000 documentos: ~600 MB

### 3. Dados de Treinamento (Texto)

**Cálculo:**
- Texto médio por documento: ~1-5 KB
- Com Markdown/HTML: pode chegar a 10-20 KB

**Exemplos:**
- 100 documentos: ~100-500 KB
- 1.000 documentos: ~1-5 MB
- 10.000 documentos: ~10-50 MB

### 4. Índices do PostgreSQL

**Espaço adicional:**
- Índice ivfflat: ~20-30% do tamanho dos embeddings
- Índices de texto: ~10-20% do tamanho dos dados

**Exemplo:**
- 1.000 documentos (6 MB embeddings):
  - Índice vetorial: ~1.5-2 MB
  - Índices de texto: ~0.5-1 MB
  - **Total índices: ~2-3 MB**

## 📈 Estimativas por Cenário

### Cenário 1: Pequeno (Início)
- 100 documentos de treinamento
- **Espaço necessário:**
  - PostgreSQL: 200 MB
  - Embeddings: 0.6 MB
  - Textos: 0.5 MB
  - Índices: 0.2 MB
  - **Total: ~201 MB**

### Cenário 2: Médio (Crescimento)
- 1.000 documentos de treinamento
- **Espaço necessário:**
  - PostgreSQL: 200 MB
  - Embeddings: 6 MB
  - Textos: 5 MB
  - Índices: 2 MB
  - **Total: ~213 MB**

### Cenário 3: Grande (Produção)
- 10.000 documentos de treinamento
- **Espaço necessário:**
  - PostgreSQL: 200 MB
  - Embeddings: 60 MB
  - Textos: 50 MB
  - Índices: 20 MB
  - **Total: ~330 MB**

### Cenário 4: Muito Grande
- 100.000 documentos de treinamento
- **Espaço necessário:**
  - PostgreSQL: 200 MB
  - Embeddings: 600 MB
  - Textos: 500 MB
  - Índices: 200 MB
  - **Total: ~1.5 GB**

## 💡 Otimizações para Reduzir Espaço

### 1. Limpar Embeddings Antigos

```sql
-- Remover documentos antigos (exemplo: mais de 1 ano)
DELETE FROM knowledge_documents 
WHERE updated_at < NOW() - INTERVAL '1 year';
```

### 2. Comprimir Textos Longos

- Armazenar apenas resumos
- Usar compressão no PostgreSQL (TOAST)

### 3. Particionar Tabelas

```sql
-- Dividir por knowledge_base_id
CREATE TABLE knowledge_documents_2024 PARTITION OF knowledge_documents
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 4. Limitar Tamanho dos Documentos

- Máximo de 10.000 caracteres por documento
- Dividir documentos grandes em chunks menores

## 🎯 Recomendações de VPS

### Para Começar (100-1.000 docs)
- **Espaço mínimo: 1 GB**
- VPS básico: 2 GB RAM, 20 GB disco
- **Custo: ~$5-10/mês**

### Para Crescimento (1.000-10.000 docs)
- **Espaço mínimo: 5 GB**
- VPS médio: 4 GB RAM, 50 GB disco
- **Custo: ~$15-25/mês**

### Para Produção (10.000+ docs)
- **Espaço mínimo: 20 GB**
- VPS grande: 8 GB RAM, 100 GB disco
- **Custo: ~$40-60/mês**

## 📊 Comparação com Supabase

### Supabase Free Tier
- Limite: 500 MB de banco
- **Suficiente para: ~5.000-8.000 documentos**

### Supabase Pro ($25/mês)
- Limite: 8 GB de banco
- **Suficiente para: ~80.000-100.000 documentos**

### VPS Próprio
- Sem limites (só o disco da VPS)
- **Custo similar ao Supabase Pro**
- **Mas com controle total**

## 🔧 Monitoramento de Espaço

### Verificar uso no PostgreSQL

```sql
-- Tamanho do banco
SELECT pg_size_pretty(pg_database_size('ai_agent_db'));

-- Tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Tamanho dos índices
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexname::regclass) DESC;
```

### Script de Monitoramento

```bash
# Ver espaço usado no disco
df -h

# Ver espaço usado pelo PostgreSQL
sudo -u postgres psql -d ai_agent_db -c "
SELECT 
    pg_size_pretty(pg_database_size('ai_agent_db')) as database_size,
    (SELECT COUNT(*) FROM knowledge_documents) as total_documents;
"
```

## ✅ Conclusão

**Para a maioria dos casos:**
- **Espaço necessário: < 1 GB** (início)
- **Crescimento: ~1 MB por 100 documentos**
- **VPS de 20 GB é suficiente para anos de uso**

**Recomendação:**
- Comece com VPS de 20-50 GB
- Monitore o crescimento
- Faça backups regulares
- Limpe dados antigos periodicamente
