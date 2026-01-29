# Erro ao abrir pgAdmin 4: ModuleNotFoundError: No module named 'pgadmin'

## Causa

A instalação do pgAdmin 4 que vem com o PostgreSQL 18 está **incompleta ou corrompida**: falta a pasta `pgadmin` (código principal) dentro de `pgAdmin 4\web\`.

## Soluções

### Opção 1: Reparar a instalação do PostgreSQL (recomendado)

1. Abra **Configurações do Windows** → **Aplicativos** → **Aplicativos instalados**.
2. Procure por **PostgreSQL 18** (ou **EDB PostgreSQL**).
3. Clique nos **três pontinhos** → **Modificar** (ou **Alterar**).
4. No instalador, escolha **Modify** e marque **pgAdmin 4** para **reinstalar/repair**.
5. Conclua e reinicie o computador se pedido.
6. Tente abrir o pgAdmin 4 de novo.

### Opção 2: Instalar pgAdmin 4 separadamente

Use a versão standalone do pgAdmin (não depende do instalador do PostgreSQL):

1. Acesse: **https://www.pgadmin.org/download/pgadmin-4-windows/**
2. Baixe o instalador do pgAdmin 4 para Windows.
3. Instale (pode conviver com o PostgreSQL 18 já instalado).
4. Abra o **pgAdmin 4** que você instalou.
5. Para conectar ao PostgreSQL 18:
   - **Servidor**: localhost (ou 127.0.0.1)
   - **Porta**: 5432
   - **Usuário**: postgres (ou ai_agent_user)
   - **Senha**: a que você definiu no .env / na instalação

### Opção 3: Usar só linha de comando e scripts (sem interface gráfica)

Você não precisa do pgAdmin para usar o PostgreSQL. Pode:

- **psql** (já instalado em `C:\Program Files\PostgreSQL\18\bin\psql.exe`).
- **Scripts do projeto**: depois que o PostgreSQL estiver rodando, use:
  ```powershell
  .\scripts\postgres_ready_setup.ps1
  ```
- **Outro cliente**: DBeaver, HeidiSQL, etc.

## Resumo

| Opção | Quando usar |
|-------|-------------|
| **Reparar instalação** | Quer manter o pgAdmin que veio com o PostgreSQL. |
| **pgAdmin standalone** | Quer interface gráfica confiável sem depender do instalador do Postgres. |
| **psql + scripts** | Quer só fazer funcionar o banco e o projeto, sem pgAdmin. |
