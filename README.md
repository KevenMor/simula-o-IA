# AI Agent API - RAG, Sentiment Analysis & Humanization Platform

API FastAPI para processamento inteligente de mensagens para chatbots WhatsApp, com integração RAG, análise de sentimento e humanização de respostas.

## 🚀 Funcionalidades

- **RAG (Retrieval Augmented Generation)**: Busca semântica em base de conhecimento usando embeddings
- **Análise de Sentimento**: Detecção de emoções em português brasileiro usando BERTimbau
- **Humanização de Respostas**: Transformação de respostas de IA em linguagem natural brasileira
- **Processamento Completo**: Endpoint único que executa todo o pipeline

## 📋 Pré-requisitos

- Python 3.11+
- Conta OpenAI (para embeddings e LLM)
- Supabase (para vector store)
- (Opcional) Conta Anthropic para Claude

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd ai-agent-api
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## 🗄️ Configuração do Banco de Dados (Supabase)

Execute o seguinte SQL no Supabase SQL Editor:

```sql
-- Criar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela de documentos da base de conhecimento
CREATE TABLE knowledge_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- Tabela de logs de conversação
CREATE TABLE conversation_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id VARCHAR(100),
  message TEXT,
  response TEXT,
  sentiment_score FLOAT,
  confidence_score FLOAT,
  knowledge_base_used VARCHAR(100),
  processing_time_ms INT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Função RPC para busca vetorial
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding vector(1536),
  knowledge_base_id text,
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_documents.id,
    knowledge_documents.content,
    knowledge_documents.metadata,
    1 - (knowledge_documents.embedding <=> query_embedding) AS similarity
  FROM knowledge_documents
  WHERE knowledge_documents.knowledge_base_id = match_documents.knowledge_base_id
    AND 1 - (knowledge_documents.embedding <=> query_embedding) > match_threshold
  ORDER BY knowledge_documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

## 🏃 Executando a API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Endpoints da API

### 1. Health Check
```
GET /health
```

### 2. RAG Query
```
POST /api/v1/rag/query
Headers: X-API-Key: your-api-key
Body:
{
  "query": "Como renovar CNH vencida?",
  "knowledge_base_id": "autoescola_ideal",
  "max_results": 5,
  "min_score": 0.7
}
```

### 3. Análise de Sentimento
```
POST /api/v1/sentiment/analyze
Headers: X-API-Key: your-api-key
Body:
{
  "text": "Já faz 3 dias que espero resposta!",
  "context": "customer_support"
}
```

### 4. Humanização de Resposta
```
POST /api/v1/humanize/response
Headers: X-API-Key: your-api-key
Body:
{
  "ai_response": "A documentação necessária inclui...",
  "tone": "friendly",
  "customer_sentiment": "neutral",
  "time_context": "morning"
}
```

### 5. Processamento Completo (Principal)
```
POST /api/v1/process/message
Headers: X-API-Key: your-api-key
Body:
{
  "message": "Quanto custa tirar CNH completa?",
  "conversation_history": [],
  "customer_id": "cust_123",
  "knowledge_base_id": "autoescola_ideal",
  "metadata": {
    "phone": "5515999999999",
    "name": "João Silva"
  }
}
```

## 🔐 Autenticação

Todos os endpoints (exceto `/health`) requerem o header:
```
X-API-Key: your-secret-api-key
```

Configure a chave no arquivo `.env` como `API_KEY_N8N`.

## 🔗 Integração com n8n

### Exemplo de Workflow n8n

```json
{
  "nodes": [
    {
      "name": "Webhook WhatsApp",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "whatsapp-webhook",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Process Message",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/api/v1/process/message",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "={{ $env.API_KEY_N8N }}"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "message",
              "value": "={{ $json.body.message }}"
            },
            {
              "name": "customer_id",
              "value": "={{ $json.body.from }}"
            },
            {
              "name": "knowledge_base_id",
              "value": "autoescola_ideal"
            },
            {
              "name": "metadata",
              "value": "={{ { \"phone\": $json.body.from, \"name\": $json.body.name } }}"
            }
          ]
        }
      }
    },
    {
      "name": "Send WhatsApp",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.whatsapp.com/send",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "to",
              "value": "={{ $json.body.from }}"
            },
            {
              "name": "message",
              "value": "={{ $('Process Message').item.json.response }}"
            }
          ]
        }
      }
    }
  ]
}
```

## 📊 Estrutura do Projeto

```
ai-agent-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configurações
│   ├── api/
│   │   ├── v1/
│   │   │   ├── rag.py         # Endpoint RAG
│   │   │   ├── sentiment.py   # Endpoint sentimento
│   │   │   ├── humanize.py    # Endpoint humanização
│   │   │   └── process.py     # Endpoint principal
│   ├── core/
│   │   ├── rag_engine.py      # Lógica RAG
│   │   ├── sentiment_analyzer.py
│   │   ├── humanizer.py
│   │   └── llm_client.py      # Cliente LLM
│   ├── models/
│   │   ├── requests.py        # Modelos Pydantic (requests)
│   │   └── responses.py       # Modelos Pydantic (responses)
│   ├── db/
│   │   ├── supabase_client.py
│   │   └── vector_store.py
│   └── utils/
│       ├── logger.py
│       └── validators.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/
```

## 🐳 Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ai-agent-api .
docker run -p 8000:8000 --env-file .env ai-agent-api
```

## 📝 Notas

- O modelo de sentimento BERTimbau será baixado na primeira execução (~500MB)
- Configure adequadamente o CORS para produção
- Implemente rate limiting adicional se necessário
- Monitore o uso de tokens da OpenAI para controle de custos

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
