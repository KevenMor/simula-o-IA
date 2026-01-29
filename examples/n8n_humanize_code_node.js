/**
 * Código para o node CODE do n8n (JavaScript).
 * Humaniza resposta e evita erros — não precisa de Python.
 *
 * No n8n: adicione um node "Code", escolha "JavaScript", cole este código.
 *
 * ========== O QUE FAZ ==========
 * 1. Lê o texto do item (response ou ai_response).
 * 2. Limpa o texto (espaços, tamanho máximo 10.000 caracteres).
 * 3. Adiciona saudação conforme o horário de BRASÍLIA (Bom dia / Boa tarde / Boa noite) — não usa horário do servidor.
 * 4. Se o cliente está negativo: insere frase de empatia (ex.: "Entendo perfeitamente").
 * 5. Ajusta o tom: "friendly" (Precisa, Você pode...) ou "formal" (É necessário, É possível...).
 * 6. Se tom amigável e não negativo: adiciona emoji (😊 👍 ✨).
 * 7. Se texto longo e amigável: adiciona despedida (ex.: "Qualquer dúvida, é só chamar!").
 * 8. Em erro: devolve o texto original e success: false (não quebra o workflow).
 *
 * ========== ENTRADA (do node anterior) ==========
 * - response ou ai_response (obrigatório): texto a humanizar
 * - tone (opcional): "friendly" | "formal" — padrão "friendly"
 * - customer_sentiment (opcional): "negative" | "neutral" | "positive"
 * - time_context (opcional): "morning" | "afternoon" | "evening" — se omitido, usa horário de Brasília (UTC-3)
 *
 * ========== SAÍDA (para o próximo node) ==========
 * - response: texto humanizado (use no Send WhatsApp: {{ $json.response }})
 * - humanized_response: mesmo texto
 * - tone_applied: tom usado
 * - success: true | false
 * - error: mensagem de erro (se success === false); senão null
 * - Todos os campos do item de entrada são mantidos (spread ...json)
 *
 * ========== EXEMPLOS ==========
 *
 * Entrada (ex.: saída do Process Message):
 *   { "response": "É necessário agendar o exame. Deve-se levar documento.", "sentiment_analysis": { "sentiment": "neutral" } }
 *
 * Saída (tom friendly, manhã):
 *   { "response": "Bom dia! Precisa agendar o exame. Você pode levar documento. 😊", "humanized_response": "...", "tone_applied": "friendly", "success": true, "error": null, ... }
 *
 * Entrada com tom formal e sentimento negativo:
 *   { "ai_response": "O prazo é 5 dias.", "tone": "formal", "customer_sentiment": "negative" }
 *
 * Saída:
 *   { "response": "Boa tarde! Entendo perfeitamente. O prazo é 5 dias.", "tone_applied": "formal", "success": true, ... }
 *   (sem emoji no formal; com empatia por ser negativo)
 */

const GREETINGS_MORNING = ['Bom dia', 'Bom dia!', 'Olá, bom dia'];
const GREETINGS_AFTERNOON = ['Boa tarde', 'Boa tarde!', 'Olá, boa tarde'];
const GREETINGS_EVENING = ['Boa noite', 'Boa noite!', 'Olá, boa noite'];
const EMPATHY_PHRASES = ['Fico feliz em ajudar', 'Entendo perfeitamente', 'Claro, vou te ajudar', 'Sem problemas'];
const CLOSING_PHRASES = ['Estou à disposição', 'Qualquer dúvida, é só chamar', 'Espero ter ajudado'];
const FRIENDLY_REPLACEMENTS = { 'É necessário': 'Precisa', 'É preciso': 'Precisa', 'Deve-se': 'Você pode', 'Recomenda-se': 'Recomendo' };
const FORMAL_REPLACEMENTS = { 'Precisa': 'É necessário', 'Você pode': 'É possível', 'Recomendo': 'Recomenda-se' };
const MAX_LENGTH = 10000;
/** Brasília: UTC-3 (sem horário de verão). Servidor pode estar em outro fuso. */
const BRASILIA_UTC_OFFSET = -3;

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

/** Retorna a hora atual em Brasília (0–23). */
function getHourBrasilia() {
  const utcHour = new Date().getUTCHours();
  return (utcHour + BRASILIA_UTC_OFFSET + 24) % 24;
}

function sanitize(text) {
  if (text == null || typeof text !== 'string') return '';
  text = text.replace(/\s+/g, ' ').trim();
  return text.length > MAX_LENGTH ? text.slice(0, MAX_LENGTH) : text;
}

function getGreeting(timeContext) {
  if (['morning', 'afternoon', 'evening'].includes(timeContext)) {
    if (timeContext === 'morning') return pick(GREETINGS_MORNING);
    if (timeContext === 'afternoon') return pick(GREETINGS_AFTERNOON);
    return pick(GREETINGS_EVENING);
  }
  const hour = getHourBrasilia();
  if (hour >= 5 && hour < 12) return pick(GREETINGS_MORNING);
  if (hour >= 12 && hour < 18) return pick(GREETINGS_AFTERNOON);
  if (hour >= 18 || hour < 5) return pick(GREETINGS_EVENING);
  return null;
}

function makeFriendly(text) {
  let out = text;
  for (const [formal, friendly] of Object.entries(FRIENDLY_REPLACEMENTS)) {
    if (out.includes(formal)) out = out.replace(formal, friendly);
  }
  return out;
}

function makeFormal(text) {
  let out = text;
  for (const [casual, formal] of Object.entries(FORMAL_REPLACEMENTS)) {
    if (out.includes(casual)) out = out.replace(casual, formal);
  }
  return out;
}

function humanize(aiResponse, tone = 'friendly', customerSentiment, timeContext) {
  let humanized = sanitize(aiResponse);
  if (!humanized) return aiResponse || '';

  const greeting = getGreeting(timeContext);
  if (greeting) humanized = `${greeting}! ${humanized}`;

  if (customerSentiment === 'negative') {
    const empathy = pick(EMPATHY_PHRASES);
    if (greeting) humanized = humanized.replace(`${greeting}! `, `${greeting}! ${empathy}. `);
    else humanized = `${empathy}. ${humanized}`;
  }

  if (tone === 'friendly') humanized = makeFriendly(humanized);
  else if (tone === 'formal') humanized = makeFormal(humanized);

  if (tone === 'friendly' && customerSentiment !== 'negative') {
    const emoji = pick(['😊', '👍', '✨']);
    if (humanized.slice(0, 20).includes('!')) humanized = humanized.replace('!', `! ${emoji}`);
    else humanized = `${humanized} ${emoji}`;
  }

  if (humanized.length > 100 && tone === 'friendly') {
    humanized = `${humanized}\n\n${pick(CLOSING_PHRASES)}!`;
  }

  return humanized;
}

// --- Processar todos os itens do n8n ---
const items = $input.all();
const result = [];

for (const item of items) {
  const json = item.json;
  try {
    const text = json.response ?? json.ai_response ?? '';
    const tone = (json.tone || 'friendly').toString().toLowerCase();
    const toneOk = tone === 'friendly' || tone === 'formal' ? tone : 'friendly';
    const sentiment = json.customer_sentiment;
    const timeContext = json.time_context;

    if (!text) {
      result.push({ json: { ...json, humanized_response: '', response: '', tone_applied: toneOk, success: true, error: null } });
      continue;
    }

    const humanized = humanize(text, toneOk, sentiment, timeContext);

    result.push({
      json: {
        ...json,
        humanized_response: humanized,
        response: humanized,
        tone_applied: toneOk,
        success: true,
        error: null,
      },
    });
  } catch (e) {
    const text = json.response ?? json.ai_response ?? '';
    result.push({
      json: {
        ...json,
        humanized_response: typeof text === 'string' ? text : '',
        response: typeof text === 'string' ? text : '',
        tone_applied: 'friendly',
        success: false,
        error: String(e && e.message ? e.message : e),
      },
    });
  }
}

return result;
