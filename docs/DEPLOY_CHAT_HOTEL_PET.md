# Deploy da página do chat (hotel/creche) para o cliente

Este guia explica como subir **apenas a página de teste do chat** (estilo WhatsApp, Tia Bia) para o cliente acessar. O link que você entrega é só **`/chat-whatsapp`** — o resto do painel (treino, configurações, etc.) fica no mesmo servidor, mas o cliente pode usar só o chat.

### Quick start (Docker)

```bash
# Na raiz do projeto, com .env configurado (OPENAI_API_KEY, API_KEY_N8N):
docker compose -f docker-compose.chat.yml up -d --build
```

Acesse **http://localhost:8000/chat-whatsapp** e envie esse link ao cliente.

---

## O que sobe

- **Backend** (FastAPI): API `/api/v1/qa/ask`, prompt da Tia Bia, etc.
- **Frontend** (React): apenas a SPA, servida junto pelo backend.
- **URL do cliente:** `https://seu-dominio.com/chat-whatsapp`

Tudo em **um único container** (ou um único servidor).

---

## Opção 1: Docker (recomendada)

### Pré-requisitos

- Docker e Docker Compose instalados.
- Arquivo `.env` na raiz do projeto com pelo menos:
  - `OPENAI_API_KEY`
  - `API_KEY_N8N` (a mesma que o frontend usa para chamar a API)

### Passos

1. Na raiz do projeto:

```bash
docker compose -f docker-compose.chat.yml build
docker compose -f docker-compose.chat.yml up -d
```

2. O frontend é buildado com `VITE_API_URL` vazio (mesma origem) e `VITE_API_KEY` = `API_KEY_N8N` do `.env`.

3. Acesse:
   - **Chat (cliente):** `http://localhost:8000/chat-whatsapp`
   - **API:** `http://localhost:8000/docs` (se quiser)

### Customizar API key no build

No `docker-compose.chat.yml` o build usa `VITE_API_KEY: ${API_KEY_N8N}`. Se quiser outra variável, altere ali e garanta que ela exista no `.env`.

---

## Opção 2: VPS (Docker na VPS)

1. Envie o projeto para a VPS (git clone ou upload).
2. Crie o `.env` na raiz com `OPENAI_API_KEY`, `API_KEY_N8N`, etc.
3. Rode:

```bash
docker compose -f docker-compose.chat.yml up -d --build
```

4. Exponha a porta 8000 (firewall, proxy reverso). Exemplo com **nginx**:

```nginx
server {
    listen 80;
    server_name meudominio.com.br;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

5. Opcional: HTTPS com Let’s Encrypt (certbot).

6. **Link para o cliente:** `https://meudominio.com.br/chat-whatsapp`

---

## Opção 3: Build manual (sem Docker)

Se preferir rodar backend e frontend sem Docker:

### 1. Backend

```bash
cd "caminho/do/projeto"
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Configure o `.env` e rode:

```bash
set SERVE_CHAT_SPA=1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

(O `static` ainda não existe; o frontend precisa ser buildado primeiro.)

### 2. Frontend

```bash
cd frontend
npm ci
set VITE_API_URL=
set VITE_API_KEY=valor_igual_ao_API_KEY_N8N
npm run build
```

### 3. Juntar com o backend

Copie o conteúdo de `frontend/dist` para `static/` na raiz do projeto (ao lado de `app/`). Estrutura:

```
projeto/
  app/
  static/
    index.html
    assets/
    vite.svg
  ...
```

Com `SERVE_CHAT_SPA=1` e `static/` preenchido, ao subir o uvicorn o FastAPI serve a SPA. O chat estará em `http://localhost:8000/chat-whatsapp`.

---

## Resumo de variáveis

| Variável | Onde | Uso |
|----------|------|-----|
| `SERVE_CHAT_SPA` | Backend (env) | `1` / `true` para servir a SPA do chat |
| `VITE_API_URL` | Build do frontend | Vazio = mesma origem; ou URL da API se frontend em outro domínio |
| `VITE_API_KEY` | Build do frontend | Mesmo valor do `API_KEY_N8N` (ou da chave que o backend aceita) |
| `API_KEY_N8N` | Backend (.env) | Chave para `X-API-Key` |
| `OPENAI_API_KEY` | Backend (.env) | Para o LLM |

---

## Link para o cliente

Sempre que for “só a página de teste”:

**`https://seu-dominio.com/chat-whatsapp`**

O cliente abre esse link e usa o chat. Não precisa ver `/`, `/training` nem `/settings`.

---

## Observações

- A **API key** é usada no frontend (build). Quem inspecionar o bundle pode encontrá-la. Para uso interno/demo com o cliente, isso costuma ser aceitável. Em cenários mais sensíveis, avalie autenticação extra.
- **Treinamento / configurações:** se quiser usar documentos ou ajustes do tenant `hotel_creche_pet`, use o painel completo (por exemplo em `/training`, `/settings`) em outro ambiente ou em outra URL, e mantenha só o `/chat-whatsapp` como “página de teste” do cliente.
