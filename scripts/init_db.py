import sqlite3
import os
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
memory_root = os.getenv('MEMORY_ROOT') or str(project_root / 'memory')
DB_PATH = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')


def init_databases():
    # Garante que o diretorio existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabela Virtual FTS5 para busca rapida de decisoes
    cursor.execute(
        '''
    CREATE VIRTUAL TABLE IF NOT EXISTS decisions USING fts5(
        timestamp,
        agent,
        task,
        decision,
        outcome,
        tokens_used,
        cost
    );
    '''
    )

    # 2. Indice de Genes
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS genome_index (
        id TEXT PRIMARY KEY,
        name TEXT,
        path TEXT,
        description TEXT,
        dependencies TEXT,
        compatible_stacks TEXT,
        tags TEXT,
        last_verified DATE
    );
    '''
    )

    # 3. Cache de Prompts
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS prompt_cache (
        prompt_hash TEXT PRIMARY KEY,
        response TEXT,
        model TEXT,
        tokens INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    '''
    )


    # 4. Tabela simplificada de genes (compatibilidade Dashboard)
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS genes (
        id TEXT PRIMARY KEY,
        name TEXT,
        path TEXT,
        tags TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    '''
    )
    conn.commit()
    conn.close()
    print(f'[OK] Bancos de dados inicializados com sucesso em: {DB_PATH}')


if __name__ == '__main__':
    init_databases()

