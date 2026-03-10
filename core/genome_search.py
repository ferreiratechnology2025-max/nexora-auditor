import sqlite3
import json
import os
from pathlib import Path


class GenomeSearch:
    def __init__(self):
        memory_root = os.getenv('MEMORY_ROOT')
        if not memory_root:
            project_root = Path(__file__).resolve().parents[1]
            memory_root = str(project_root / 'memory')
        self.db_path = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')

    def find_matches(self, query):
        """
        Busca genes que correspondam à necessidade do projeto.
        Retorna uma lista de dicionários com os metadados do gene.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        cursor = conn.cursor()

        # Busca simples por tags ou descrição (pode ser expandido para FTS5 completo)
        search_query = f'%{query}%'
        cursor.execute(
            '''
            SELECT id, name, path, dependencies, tags
            FROM genome_index
            WHERE tags LIKE ? OR description LIKE ? OR name LIKE ?
            ''',
            (search_query, search_query, search_query),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                {
                    'id': row['id'],
                    'name': row['name'],
                    'path': row['path'],
                    'dependencies': json.loads(row['dependencies']),
                    'tags': json.loads(row['tags']),
                }
            )

        conn.close()
        return results


if __name__ == '__main__':
    # Teste rápido do motor de busca
    search = GenomeSearch()
    matches = search.find_matches('auth')
    if matches:
        print(f"[OK] Encontrado {len(matches)} gene(s) para sua busca:")
        for m in matches:
            print(f" - {m['name']} em {m['path']}")
    else:
        print('[AVISO] Nenhum gene encontrado para o termo buscado.')
