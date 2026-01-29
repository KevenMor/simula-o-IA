"""Script para testar conexão com PostgreSQL local."""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.db.postgres_client import postgres_client


async def test_connection():
    """Testar conexão com PostgreSQL."""
    print("🔍 Testando conexão com PostgreSQL...")
    
    # Verificar se configurações estão presentes
    if not all([
        getattr(settings, 'postgres_host', None),
        getattr(settings, 'postgres_db', None),
        getattr(settings, 'postgres_user', None),
        getattr(settings, 'postgres_password', None),
    ]):
        print("❌ Configurações PostgreSQL não encontradas no .env")
        print("\nAdicione ao .env:")
        print("POSTGRES_HOST=localhost")
        print("POSTGRES_PORT=5432")
        print("POSTGRES_DB=ai_agent_db")
        print("POSTGRES_USER=ai_agent_user")
        print("POSTGRES_PASSWORD=sua_senha")
        return False
    
    try:
        # Inicializar cliente
        await postgres_client.initialize()
        
        if not postgres_client.pool:
            print("❌ Falha ao criar pool de conexões")
            return False
        
        # Testar conexão
        async with postgres_client.pool.acquire() as conn:
            # Testar versão do PostgreSQL
            version = await conn.fetchval("SELECT version()")
            print(f"✅ Conectado ao PostgreSQL!")
            print(f"   Versão: {version.split(',')[0]}")
            
            # Verificar extensão pgvector
            has_vector = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            )
            if has_vector:
                print("✅ Extensão pgvector instalada")
            else:
                print("⚠️ Extensão pgvector NÃO encontrada")
                print("   Execute: CREATE EXTENSION vector;")
            
            # Verificar tabelas
            tables = await conn.fetch("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            
            if tables:
                print(f"✅ Tabelas encontradas: {len(tables)}")
                for table in tables:
                    print(f"   - {table['tablename']}")
            else:
                print("⚠️ Nenhuma tabela encontrada")
                print("   Execute: scripts/create_postgres_tables.sql")
            
            # Contar documentos (se tabela existir)
            try:
                count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_documents")
                print(f"📊 Documentos na base: {count}")
            except:
                print("⚠️ Tabela knowledge_documents não existe")
        
        await postgres_client.close()
        print("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("\nVerifique:")
        print("1. PostgreSQL está rodando?")
        print("2. Credenciais no .env estão corretas?")
        print("3. Banco de dados 'ai_agent_db' existe?")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
