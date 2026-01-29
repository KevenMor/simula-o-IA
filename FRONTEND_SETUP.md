# 🚀 Frontend React - Guia de Instalação

## ✅ O que foi criado

Frontend moderno em **React + TypeScript + Tailwind CSS** com design corporativo tipo SaaS.

### 📦 Estrutura

```
frontend/
├── src/
│   ├── pages/
│   │   ├── ChatPage.tsx          # Chat com IA (estilo WhatsApp)
│   │   ├── TrainingPage.tsx      # Gerenciar base de conhecimento
│   │   ├── SettingsPage.tsx      # ⭐ Configurações do agente
│   │   └── DashboardPage.tsx     # Dashboard com métricas
│   ├── components/
│   │   └── Layout.tsx            # Layout com sidebar
│   └── services/
│       └── api.ts                # Integração com FastAPI
```

## 🎯 Página de Configurações

A página de **Configurações** permite ajustar:

1. **Proteção Anti-Alucinações**
   - ✅ Ativar/desativar verificação
   - ✅ Threshold de confiança (0.0 a 1.0)
   - ✅ Slider interativo

2. **Configurações do Modelo**
   - ✅ Temperatura (0.0 a 2.0)
   - ✅ Máximo de tokens por resposta

3. **Estilo de Resposta**
   - ✅ Amigável / Formal / Casual
   - ✅ Perguntar nome automaticamente

4. **Cache**
   - ✅ Ativar/desativar cache
   - ✅ TTL do cache (segundos)

## 📋 Instalação

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar variáveis de ambiente

Criar arquivo `.env` no diretório `frontend/`:

```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTc3YjA3Ni0zZDBhLTRiMGEtYjQwOS02ODZmOWQ5NDg0YjUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5NjQ4NTI5fQ.vGE6KW1YPSMIHZQs8OgquSIx8K9ymiWSY1BS6KurqRA
```

### 3. Iniciar servidor de desenvolvimento

```bash
npm run dev
```

Acesse: **http://localhost:3000**

## 🎨 Design

- **Tailwind CSS** para estilização moderna
- **Lucide React** para ícones
- **Layout com sidebar** para navegação
- **Cores primárias** personalizáveis
- **Responsivo** e moderno

## 🔗 Integração com Backend

O frontend se conecta automaticamente com a API FastAPI:

- **GET** `/api/v1/settings/{tenant_id}` - Carregar configurações
- **PUT** `/api/v1/settings/{tenant_id}` - Salvar configurações
- **POST** `/api/v1/qa/ask` - Fazer perguntas
- **GET** `/api/v1/training/documents` - Listar documentos
- **POST** `/api/v1/training/documents` - Salvar documento
- **DELETE** `/api/v1/training/documents/{id}` - Excluir documento

## ⚙️ Como Funciona

1. **Usuário ajusta configurações** na página de Settings
2. **Configurações são salvas** no arquivo `data/tenant_settings.json`
3. **Endpoint QA lê as configurações** do tenant automaticamente
4. **Respostas usam as configurações** personalizadas

## 🎯 Próximos Passos

1. Instalar dependências: `cd frontend && npm install`
2. Criar `.env` com suas credenciais
3. Iniciar: `npm run dev`
4. Acessar http://localhost:3000
5. Ir em **Configurações** e ajustar conforme necessário!

## 📝 Notas

- As configurações são **por tenant** (cada cliente tem suas próprias)
- Mudanças são **salvas imediatamente** no backend
- O endpoint QA **usa automaticamente** as configurações do tenant
