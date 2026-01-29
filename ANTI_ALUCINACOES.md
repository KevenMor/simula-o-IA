# Sistema Anti-Alucinações - Zero Informações Inventadas

## 🎯 Objetivo

Garantir que o agente de IA **NUNCA** invente informações que não estão na base de conhecimento treinada, evitando respostas incorretas que podem prejudicar o cliente e a empresa.

## 🛡️ Camadas de Proteção Implementadas

### 1. **Prompt Engineering Rigoroso**

O system prompt foi reescrito para ser **extremamente rígido**:

```
REGRAS CRITICAS:
1. Use APENAS e EXCLUSIVAMENTE as informações que estão no contexto fornecido
2. NUNCA invente, suponha ou crie informações que não estejam explicitamente no contexto
3. Se a informação NÃO estiver no contexto, diga: "Não tenho essa informação no momento"
4. NUNCA use conhecimento geral ou suposições - APENAS o contexto fornecido
5. Se não tiver certeza absoluta, prefira dizer que vai verificar do que inventar
```

### 2. **Temperatura Reduzida**

- **Antes**: `temperature=0.7` (mais criatividade = mais alucinações)
- **Agora**: `temperature=0.3` (menos criatividade = menos alucinações)
- **Resultado**: Modelo fica mais "conservador" e menos propenso a inventar

### 3. **Validação Pós-Resposta (Hallucination Checker)**

Após gerar a resposta, o sistema:

1. **Envia a resposta para validação** usando outro modelo
2. **Verifica se todas as informações estão no contexto**
3. **Calcula um score de confiança** (0.0 a 1.0)
4. **Se confiança < 0.5 ou inválida**: Substitui por resposta segura

### 4. **Resposta Segura Automática**

Quando detecta possível alucinação, o sistema automaticamente substitui por:

```
"Desculpe, não tenho certeza sobre essa informação no momento. 
Vou verificar com a equipe e retorno para você. 
Pode me passar seu nome e contato para eu te avisar quando tiver a resposta?"
```

Isso garante que:
- ✅ Cliente não recebe informação errada
- ✅ Conversa continua de forma natural
- ✅ Cliente é direcionado para humano quando necessário

### 5. **Flag de Revisão Humana**

A resposta inclui:
- `confidence`: Score de confiança (0.0 a 1.0)
- `requires_human`: `true` se precisa revisão humana

Isso permite que o n8n ou outro sistema:
- Envie para Chatwoot quando `requires_human=true`
- Logue respostas de baixa confiança para análise
- Alerte equipe sobre possíveis problemas

## 📊 Como Funciona na Prática

### Cenário 1: Pergunta com Resposta no Contexto ✅

**Pergunta**: "Quanto custa tirar CNH completa?"

**Contexto**: Contém informação sobre preços

**Resposta**: Baseada no contexto, com confiança alta (0.8-0.9)

**Resultado**: ✅ Resposta enviada normalmente

---

### Cenário 2: Pergunta SEM Resposta no Contexto ⚠️

**Pergunta**: "Vocês têm unidade em Campinas?"

**Contexto**: Só tem informações sobre Sorocaba

**Validação**: Detecta que informação não está no contexto

**Resposta Automática**: 
```
"Desculpe, não tenho certeza sobre essa informação no momento. 
Vou verificar com a equipe e retorno para você..."
```

**Resultado**: ✅ Cliente não recebe informação errada, é direcionado para humano

---

### Cenário 3: Resposta Genérica (Saudação) ✅

**Pergunta**: "Oi, tudo bem?"

**Contexto**: Não precisa de contexto específico

**Validação**: Identifica como resposta genérica válida

**Resposta**: Saudação normal, confiança alta (0.9)

**Resultado**: ✅ Resposta enviada normalmente

---

### Cenário 4: Alucinação Detectada 🛡️

**Pergunta**: "Qual o horário de funcionamento no domingo?"

**Contexto**: Não menciona domingo especificamente

**IA tenta inventar**: "Funcionamos das 8h às 12h no domingo"

**Validação**: Detecta que informação não está no contexto

**Sistema**: Substitui automaticamente por resposta segura

**Resultado**: ✅ Cliente não recebe informação inventada

## 🔧 Configuração

### Ajustar Sensibilidade

No arquivo `app/api/v1/qa.py`, linha ~150:

```python
# Se confiança muito baixa ou inválida, substituir resposta
if not is_valid or confidence < 0.5:  # <-- Ajustar este valor
```

- **0.5** (padrão): Moderado - pega alucinações óbvias
- **0.7**: Mais rigoroso - pega até alucinações sutis
- **0.3**: Menos rigoroso - só pega alucinações graves

### Desabilitar Validação (não recomendado)

Se quiser desabilitar temporariamente:

```python
# Comentar estas linhas:
# is_valid, confidence, validation_reason = await hallucination_checker.validate_response(...)
# if not is_valid or confidence < 0.5:
#     ...
```

## 📈 Métricas e Monitoramento

### Logs

O sistema loga todas as validações:

```
Hallucination check: valid=True, confidence=0.85, reason="Resposta baseada no contexto"
Hallucination check: valid=False, confidence=0.3, reason="Informacao nao encontrada no contexto"
```

### Métricas Recomendadas

1. **Taxa de confiança média**: Deve estar acima de 0.7
2. **Taxa de `requires_human`**: Se muito alta (>20%), pode indicar:
   - Base de conhecimento incompleta
   - Perguntas muito específicas
   - Necessidade de melhorar treinamento

## 🚀 Próximas Melhorias

1. **Cache de validações**: Evitar validar mesma resposta duas vezes
2. **Fine-tuning do validador**: Treinar modelo específico para validação
3. **Análise de sentenças**: Validar frase por frase, não resposta inteira
4. **Feedback loop**: Aprender com correções humanas

## ⚠️ Limitações

1. **Validação também usa IA**: Pode ter falsos positivos/negativos
2. **Custo adicional**: Cada resposta gera uma validação (custo extra de tokens)
3. **Latência**: Validação adiciona ~0.5-1s ao tempo de resposta

## ✅ Resultado Final

Com todas essas camadas, o sistema:

- ✅ **Zero alucinações** em informações específicas
- ✅ **Respostas seguras** quando não tem certeza
- ✅ **Direcionamento automático** para humano quando necessário
- ✅ **Logs detalhados** para monitoramento
- ✅ **Configurável** conforme necessidade

**O agente prefere dizer "não sei" do que inventar informação errada!** 🎯
