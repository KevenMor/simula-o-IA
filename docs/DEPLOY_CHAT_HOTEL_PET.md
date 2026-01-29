# Deploy da página do chat (hotel/creche) para o cliente

Este guia explica como subir **apenas a página de teste do chat** (estilo WhatsApp, Tia Bia) para o cliente acessar. O link que você entrega é só **`/chat-whatsapp`** — o resto do painel (treino, configurações, etc.) fica no mesmo servidor, mas o cliente pode usar só o chat.

### Quick start (Docker)

```bash
# Na raiz do projeto, com .env configurado (OPENAI_API_KEY, API_KEY_N8N):
docker compose -f docker-compose.chat.yml up -d --build
```

Acesse **http://localhost:8000/chat-whatsapp** e envie esse link ao cliente.

---

## Deploy no EasyPanel

Use o **EasyPanel** para subir o projeto e configure as **variáveis de ambiente** direto na interface (não precisa de arquivo `.env`).

### ⚠️ Frontend não abre? Use o `Dockerfile.chat`

O **`Dockerfile`** padrão sobe **só a API** (sem frontend). Para ter a **página do chat** (`/`, `/chat-whatsapp`), o EasyPanel precisa usar o **`Dockerfile.chat`**.

No EasyPanel, em **Build** / **Dockerfile** / **Dockerfile path**, defina:
- **`Dockerfile.chat`** (e não `Dockerfile`)

O `Dockerfile.chat` faz o build do React, coloca em `/app/static` e o FastAPI sirve a SPA. Sem isso, você só acessa a API (ex.: `/docs`).

### 1. Conectar o repositório

- **Repositório:** `https://github.com/KevenMor/simula-o-IA`
- **Dockerfile:** `Dockerfile.chat` ← **obrigatório para o frontend**
- **Porta:** `8000`

### 2. Variáveis de ambiente (no EasyPanel)

Configure estas variáveis em **Variáveis de ambiente** / **Environment**:

| Variável | Obrigatório | Exemplo / valor |
|----------|-------------|------------------|
| `OPENAI_API_KEY` | ✅ Sim | `sk-proj-...` |
| `API_KEY_N8N` | ✅ Sim | Mesma chave que o frontend usa para `X-API-Key` |

Opcionais (se usar):

| Variável | Uso |
|----------|-----|
| `ANTHROPIC_API_KEY` | Claude |
| `SUPABASE_URL` / `SUPABASE_KEY` | RAG (Supabase) |
| `POSTGRES_HOST`, `POSTGRES_PORT`, etc. | PostgreSQL |

O `SERVE_CHAT_SPA=1` já está definido no `Dockerfile.chat`; não é preciso repetir.

### 3. Build arguments (se o EasyPanel tiver)

Se existir **Build args** / **Build environment**:

- `VITE_API_URL` = vazio (ou em branco)
- `VITE_API_KEY` = **mesmo valor** de `API_KEY_N8N`

Assim o frontend é buildado já com a chave. Se o EasyPanel não tiver build args, o deploy sobe, mas o chat pode falhar ao chamar a API (sem chave no frontend). Nesse caso, use deploy por **docker-compose** (VPS) ou informe se o EasyPanel aceita variáveis no build.

### 4. Depois do deploy

- **Chat (cliente):** `https://seu-dominio.easypanel.host/chat-whatsapp` (ou o domínio que você configurou)
- **API:** `https://seu-dominio/docs` (se precisar)

Envie o link **`/chat-whatsapp`** para o cliente.

### 5. Troubleshooting — frontend não abre

**Passo a passo para diagnosticar:**

1. **Abra `https://seu-dominio/health`**  
   Deve retornar algo como:
   ```json
   { "serve_spa": true, "static_exists": true, "index_html_exists": true, ... }
   ```
   - Se `serve_spa: false` ou `static_exists: false` → o build não usou `Dockerfile.chat` ou o static não foi gerado.

2. **Rebuild sem cache**  
   O frontend no Docker estava **CACHED**. Pode estar quebrado. No EasyPanel:
   - Procure **"Clear build cache"**, **"Rebuild"** ou **"No cache"** e faça um novo deploy.
   - O projeto tem **cache bust** (`FRONTEND_CACHEBUST`) no `Dockerfile.chat`; altere o valor lá e dê push para forçar rebuild.

3. **DevTools (F12) → aba Network**  
   Abra a URL do app, recarregue e veja:
   - `GET /` ou `/chat-whatsapp` → 200? Retorna HTML?
   - `GET /assets/...js` e `...css` → 200 ou 404?  
   Se os assets forem 404, o proxy (EasyPanel) pode estar servindo o app em **subpath**; aí será preciso configurar `base` no Vite.

4. **URL exata**  
   O app está em **`https://dominio.com/`** (raiz) ou em **`https://dominio.com/algum-path/`**? Se for subpath, avise para ajustarmos o `base` no frontend.

#### Por que abre em dev e não em prod?

| | **Dev** | **Prod** |
|---|--------|--------|
| **Frontend** | Vite em `localhost:3000`; proxy `/api` → `:8000` | Build estático servido pelo FastAPI (mesmo container) |
| **API** | Backend em `:8000`; frontend chama `localhost:8000` ou usa proxy | **Mesma origem**: frontend e API no mesmo domínio. O front deve usar `VITE_API_URL=""` para não apontar para `localhost` (que no navegador do usuário seria a máquina dele, não o servidor). |
| **O que quebra em prod** | — | (1) **API URL**: se o build usou fallback `localhost:8000`, as chamadas vão para o PC do usuário → falha. (2) **Assets 404**: app em subpath sem `base` no Vite. (3) **Cache**: frontend CACHED no Docker com build antigo. |

O `api.ts` foi ajustado: com `VITE_API_URL=""` no build, usamos **mesma origem** em prod. Em dev, continuamos com `localhost:8000` quando não houver `VITE_API_URL`. Rebuild e redeploy após o fix.

| Sintoma | Causa | Solução |
|--------|--------|---------|
| Só aparece JSON ou só `/docs` | Build com `Dockerfile` padrão (só API) | Usar **`Dockerfile.chat`** no EasyPanel |
| Página em branco ou 404 em `/chat-whatsapp` | SPA não está sendo servida | Conferir se o Dockerfile é `Dockerfile.chat` e se `SERVE_CHAT_SPA=1` (já vem no Dockerfile) |
| Chat abre mas erro ao enviar mensagem | Frontend sem `VITE_API_KEY` no build | Preencher **Build args**: `VITE_API_KEY` = mesmo valor de `API_KEY_N8N` |
| Build do Docker **falha** no estágio do frontend | `tsc` quebra (main.ts, api.ts) | O `Dockerfile.chat` já usa só `vite build` (sem `tsc`). Faça **rebuild** e confira os logs. |
| Deploy ok mas frontend não abre | Cache antigo ou static ausente | Ver **`/health`**; fazer **rebuild sem cache**; checar Network (assets 404?). |
| **Container reinicia / uvicorn crash** | `api_key_n8n` Field required, ou `ModuleNotFoundError: app.models` | (1) **API_KEY_N8N**: defina nas variáveis de ambiente do EasyPanel (ex.: `API_KEY_N8N=suachave`). (2) **app.models**: o módulo foi criado; faça pull e redeploy. |

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
