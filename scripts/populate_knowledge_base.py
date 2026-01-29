"""Script to populate knowledge base with documents."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from app.db.vector_store import vector_store
from app.db.supabase_client import supabase_client
from app.utils.logger import logger


async def add_document(knowledge_base_id: str, content: str, metadata: dict = None):
    """Add a document to the knowledge base."""
    try:
        # Generate embedding
        embedding = await vector_store.get_embedding(content)
        
        # Insert into Supabase
        supabase = supabase_client.get_client()
        result = supabase.table('knowledge_documents').insert({
            'knowledge_base_id': knowledge_base_id,
            'content': content,
            'embedding': embedding,
            'metadata': metadata or {}
        }).execute()
        
        logger.info(f"Document added: {result.data[0]['id']}")
        return result.data[0]
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise


async def populate_autoescola_kb():
    """Populate knowledge base for driving school."""
    kb_id = "autoescola_ideal"
    
    documents = [
        {
            "content": """Para renovar a CNH vencida, você precisa:
1. Agendar o exame médico e psicológico
2. Realizar os exames em clínicas credenciadas
3. Pagar a taxa do DETRAN
4. Comparecer ao DETRAN para renovação

Documentos necessários:
- CPF
- RG
- Comprovante de residência
- Certificado dos exames médicos

Prazo: A CNH pode ser renovada até 30 dias antes do vencimento ou até 30 dias após.""",
            "metadata": {"category": "cnh", "topic": "renovacao"}
        },
        {
            "content": """Valores da CNH completa (categorias A+B):
- Taxa do DETRAN: R$ 150,00
- Exame médico/psicológico: R$ 120,00
- Aulas teóricas: R$ 400,00
- Aulas práticas: R$ 1.200,00 (mínimo 20 aulas)
- Taxa de exame teórico: R$ 50,00
- Taxa de exame prático: R$ 100,00

Total aproximado: R$ 2.020,00

Formas de pagamento: À vista com desconto de 10% ou parcelado em até 10x.""",
            "metadata": {"category": "precos", "topic": "cnh_completa"}
        },
        {
            "content": """Horários de funcionamento:
- Segunda a Sexta: 8h às 18h
- Sábado: 8h às 12h
- Domingo: Fechado

Aulas práticas:
- Manhã: 8h às 12h
- Tarde: 14h às 18h
- Noite: 19h às 22h (apenas segunda a quinta)

Agendamento de aulas: Pode ser feito pelo WhatsApp ou presencialmente.""",
            "metadata": {"category": "horarios", "topic": "funcionamento"}
        },
        {
            "content": """Documentação necessária para primeira habilitação:
1. CPF (original e cópia)
2. RG (original e cópia)
3. Comprovante de residência (últimos 3 meses)
4. Certidão de nascimento ou casamento
5. 2 fotos 3x4 recentes
6. Comprovante de escolaridade (mínimo ensino fundamental)
7. Certificado de conclusão do curso teórico

Idade mínima: 18 anos completos.""",
            "metadata": {"category": "documentacao", "topic": "primeira_habilitacao"}
        },
        {
            "content": """Tipos de CNH disponíveis:
- Categoria A: Motocicletas e similares
- Categoria B: Carros de passeio
- Categoria AB: Motos e carros
- Categoria C: Veículos de carga acima de 3.500kg
- Categoria D: Veículos de transporte de passageiros
- Categoria E: Veículos com reboque acima de 6.000kg

Para categoria B, é necessário ter no mínimo 18 anos e ser aprovado nos exames teórico e prático.""",
            "metadata": {"category": "categorias", "topic": "tipos_cnh"}
        }
    ]
    
    logger.info(f"Populating knowledge base: {kb_id}")
    
    for doc in documents:
        await add_document(kb_id, doc["content"], doc["metadata"])
        await asyncio.sleep(0.5)  # Rate limiting
    
    logger.info(f"Added {len(documents)} documents to {kb_id}")


async def main():
    """Main function."""
    try:
        await populate_autoescola_kb()
        logger.info("Knowledge base population completed!")
    except Exception as e:
        logger.error(f"Error populating knowledge base: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
