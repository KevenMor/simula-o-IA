# Node de humanização no n8n: resposta humanizada e sem erros

Este guia explica como humanizar respostas no n8n **sem depender de Python** (Code em JavaScript) ou usando o script Python / a API.

---

## Erro "Python runner unavailable" no Code node

Se aparecer:

- **"Python 3 is missing from this system"** ou  
- **"Internal mode is intended only for debugging. For production, deploy in external mode"**

significa que o n8n está sem Python 3 no servidor ou em modo interno. **Solução mais simples:** use o **Code node em JavaScript** (abaixo) — não precisa de Python e funciona em qualquer instalação do n8n.

## O que a humanização faz

- **Humaniza** o texto (saudação, tom amigável/formal, empatia, emojis, despedida).
- **Trata erros**: em caso de exceção, devolve o texto original e `success: false`, sem falhar o workflow.
- **Input**: `response` ou `ai_response`, e opcionalmente `tone`, `customer_sentiment`, `time_context`.
- **Output**: `humanized_response`, `response` (para o Send WhatsApp), `tone_applied`, `success`, `error`.

---

## Opção 1 (recomendada): Code node em JavaScript — sem Python

Funciona em qualquer n8n; não precisa de Python instalado.

1. Adicione um node **Code**.
2. Deixe o modo em **JavaScript** (não use Python).
3. Copie todo o conteúdo do arquivo **`n8n_humanize_code_node.js`** e cole no editor do node.
4. Conecte a entrada ao node que traz a resposta (ex.: **Process Message**).
5. No **Send WhatsApp**, use no corpo da mensagem: `{{ $json.response }}`.

O código lê `response` ou `ai_response` do item, humaniza e devolve `response` + `humanized_response`; em erro devolve o texto original e `success: false`.

---

## Opção 2: Execute Command (Python) no n8n

Use quando quiser humanizar **dentro do n8n** sem chamar a API (sem depender do servidor FastAPI).

### 1. Coloque o script em um local acessível

Exemplo: `C:\Users\keven\Downloads\IA python\examples\n8n_humanize_node.py`  
Ou copie o conteúdo para um caminho onde o n8n (ou o usuário que roda o n8n) tenha permissão de leitura.

### 2. Crie o node no workflow

1. Adicione um node **Execute Command**.
2. **Command**: `python` (ou `python3` no Linux/Mac).
3. **Arguments**:  
   `"C:\Users\keven\Downloads\IA python\examples\n8n_humanize_node.py"`  
   (ajuste o caminho conforme seu ambiente.)
4. **Stdin**: para passar o item atual como JSON:
   ``` 
   {{ JSON.stringify($json) }}
   ```
   Assim o script recebe no stdin o mesmo objeto que o node anterior (ex.: saída do Process Message).

### 3. Posição no fluxo

- **Depois de “Process Message”**  
  Se quiser humanizar de novo (ou garantir humanização mesmo quando a API falhar):  
  Webhook → Process Message → **Humanize (Python)** → Check Human Needed → Send WhatsApp / Chatwoot.

- **Depois de “Check Human Needed” (só no ramo do bot)**  
  Para humanizar apenas a resposta que vai para o WhatsApp:  
  … → Check Human Needed (false) → **Humanize (Python)** → Send WhatsApp.

### 4. Usar a saída no “Send WhatsApp”

No node **Send WhatsApp**, no corpo da mensagem use:

- `{{ $json.response }}`  
  (o script sempre devolve `response` com o texto final, humanizado ou original em fallback.)

### 5. Tratar falha de humanização (opcional)

Se quiser diferenciar quando houve erro na humanização:

- Depois do **Humanize (Python)**, use um **IF**:
  - Condição: `{{ $json.success }}` igual a `true`.
  - Ramo true: segue para Send WhatsApp (ou próximo passo).
  - Ramo false: pode enviar mensagem genérica, logar ou encaminhar para humano, usando `{{ $json.response }}` (texto original).

---

## Opção 3: HTTP Request para a API (sem Python no n8n)

Se preferir usar a API FastAPI de humanização:

1. Adicione um node **HTTP Request**.
2. **Method**: POST.
3. **URL**: `http://localhost:8000/api/v1/humanize/response` (ou a URL do seu servidor).
4. **Headers**:
   - `X-API-Key`: `{{ $env.API_KEY_N8N }}`
   - `Content-Type`: `application/json`
5. **Body (JSON)**:
   ```json
   {
     "ai_response": "{{ $json.response }}",
     "tone": "{{ $json.sentiment_analysis ? 'friendly' : 'friendly' }}",
     "customer_sentiment": "{{ $json.sentiment_analysis?.sentiment || 'neutral' }}"
   }
   ```
6. **Tratamento de erro**: ative “Continue On Fail” no node e, no próximo node, use um **IF**:
   - Se `{{ $json.humanized_response }}` existir → use esse texto.
   - Senão → use `{{ $('Process Message').item.json.response }}` (resposta original).

Assim você humaniza pela API e evita quebrar o fluxo em caso de erro.

---

## Campos do input (para o script Python)

| Campo                | Obrigatório | Descrição |
|----------------------|------------|-----------|
| `response` ou `ai_response` | Sim       | Texto a humanizar (ex.: saída do Process Message). |
| `tone`               | Não        | `"friendly"` (padrão) ou `"formal"`. |
| `customer_sentiment` | Não        | `"negative"`, `"neutral"`, `"positive"`. |
| `time_context`       | Não        | `"morning"`, `"afternoon"`, `"evening"`. |

## Campos do output (do script)

| Campo                | Descrição |
|----------------------|-----------|
| `humanized_response` | Texto humanizado (ou original em fallback). |
| `response`           | Mesmo que `humanized_response` (para usar direto no Send WhatsApp). |
| `tone_applied`       | Tom aplicado. |
| `success`            | `true` se humanizou com sucesso; `false` se houve erro e foi usado fallback. |
| `error`              | Mensagem de erro (se `success` for `false`). |

---

## Resumo: evitar erros

1. **Script Python**: não levanta exceção; em erro devolve texto original e `success: false`.
2. **n8n**: use **Continue On Fail** no HTTP Request (opção 2) para não parar o workflow.
3. **Fluxo**: sempre ter um fallback (ex.: usar `$json.response` quando `success` for `false` ou quando a API falhar).

Se disser em qual opção você está (Execute Command com Python ou HTTP Request para a API), dá para desenhar o fluxo exato dos nodes no seu n8n (nomes e conexões).
