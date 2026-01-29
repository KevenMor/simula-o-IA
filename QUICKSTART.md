# Guia Rápido de Início

## Configuração Rápida (5 minutos)

### 1. Instalação

```bash
# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-supabase
API_KEY_N8N=sua-chave-secreta
ENVIRONMENT=development
```

### 3. Configurar Supabase

Execute o SQL fornecido no README.md no SQL Editor do Supabase para criar as tabelas e função de busca vetorial.

### 4. Popular Base de Conhecimento (Opcional)

```bash
python scripts/populate_knowledge_base.py
```

### 5. Iniciar API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

## Testando os Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Processar Mensagem (Endpoint Principal)
```bash
curl -X POST http://localhost:8000/api/v1/process/message \
  -H "X-API-Key: sua-chave-secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quanto custa tirar CNH completa?",
    "knowledge_base_id": "autoescola_ideal",
    "customer_id": "cust_123",
    "metadata": {
      "phone": "5515999999999",
      "name": "João Silva"
    }
  }'
```

### Análise de Sentimento
```bash
curl -X POST http://localhost:8000/api/v1/sentiment/analyze \
  -H "X-API-Key: sua-chave-secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Já faz 3 dias que espero resposta!",
    "context": "customer_support"
  }'
```

### RAG Query
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "X-API-Key: sua-chave-secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Como renovar CNH vencida?",
    "knowledge_base_id": "autoescola_ideal",
    "max_results": 5,
    "min_score": 0.7
  }'
```

## Documentação Interativa

Acesse http://localhost:8000/docs para ver a documentação interativa do Swagger UI.

## Próximos Passos

1. Configure seu workflow n8n usando o exemplo em `examples/n8n_workflow.json`
2. Adicione mais documentos à sua base de conhecimento
3. Ajuste os parâmetros de temperatura e max_tokens conforme necessário
4. Configure CORS adequadamente para produção
5. Implemente cache Redis para melhor performance (opcional)
