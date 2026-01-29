# Chat estilo WhatsApp – (nome da empresa) | Tia Bia

Página que simula atendimento via WhatsApp para um **hotel e creche para cachorros**. O cliente conversa com a **Tia Bia**, agente de atendimento. O nome do estabelecimento aparece como **(nome da empresa)** — o dono do negócio substitui pelo nome real (ex.: "PetFriend", "Hotel do Totó"). Pode ser usada no **desktop** ou em demonstrações.

## Como acessar

- **URL:** `http://seu-dominio/chat-whatsapp`
- No painel admin: sidebar → **Chat WhatsApp (demo)**

A página abre em **tela cheia**, sem sidebar, como um app de mensagens.

## Agente: Tia Bia

O backend usa o **prompt da Tia Bia** quando o tenant é `hotel_creche_pet`:

- **Prompt:** `app/prompts/tia_dani_petfriend.txt`
- **Loader:** `app/prompts/loader.py` (injeta data atual e saudação por período)
- Regras: triagem obrigatória (mais perguntas, respostas curtas e humanizadas), nunca recusar (exceto raças bloqueadas), uso de "(nome da empresa)" ao citar o estabelecimento. Pedido de preço antes da triagem: manter fluxo; na segunda insistência, perguntar frequência (creche) ou datas (hotel) e depois passar valores.

Modo **desktop**: sem ferramentas externas.

## Configuração

1. **Treinamento (opcional):** Em **Treinamento**, adicione documentos com tenant `hotel_creche_pet` (endereço, preços, regras, FAQs). O prompt já traz a estrutura; os docs complementam.
2. **Configurações (opcional):** Em **Configurações**, configure o tenant `hotel_creche_pet` (temperatura, tokens, etc.).
3. **Nome da empresa:** Para exibir o nome real no chat, edite `frontend/src/pages/WhatsAppChatPage.tsx` (header e boas-vindas) e substitua "(nome da empresa)" pelo nome do negócio. No prompt, a Tia Bia continua usando "(nome da empresa)" até você ajustar o arquivo de prompt, se quiser.

## Personalização

- **Frontend:** `WhatsAppChatPage.tsx` — `TENANT_ID`, "(nome da empresa)", "Tia Bia", textos de boas-vindas.
- **Prompt:** `app/prompts/tia_dani_petfriend.txt` — regras, triagem, valores de referência, raças bloqueadas, etc.
- **Backend:** `app/api/v1/qa.py` — `TENANT_PETFRIEND = "hotel_creche_pet"`.

## Tecnologia

- Frontend: React + Tailwind, estilo WhatsApp.
- Backend: `POST /api/v1/qa/ask` com `tenant_id: hotel_creche_pet` e `conversation_history`.
- Sem cache nem checagem de alucinação para esse tenant.

## Deploy para o cliente

Para subir **só essa página** e dar o link ao cliente, use o guia **`docs/DEPLOY_CHAT_HOTEL_PET.md`** (Docker, VPS ou build manual).
