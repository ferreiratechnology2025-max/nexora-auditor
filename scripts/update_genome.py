import sqlite3
import json
import os
from datetime import date
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
memory_root = os.getenv('MEMORY_ROOT') or str(project_root / 'memory')
genome_root = os.getenv('GENOME_ROOT') or str(project_root / 'code_genome')
DB_PATH = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')
GENOME_PATH = genome_root


def scan_genome_folders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Percorre pastas em code_genome/core/
    core_path = os.path.join(GENOME_PATH, 'core')
    for folder in os.listdir(core_path):
        folder_path = os.path.join(core_path, folder)
        metadata_file = os.path.join(folder_path, 'GENOME.md')

        if os.path.isdir(folder_path) and os.path.exists(metadata_file):
            # Logica simplificada de extracao de tags do GENOME.md
            gene_id = folder
            name = folder.replace('_', ' ').title()

            cursor.execute(
                '''
            INSERT OR REPLACE INTO genome_index
            (id, name, path, description, dependencies, compatible_stacks, tags, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                (
                    gene_id,
                    name,
                    folder_path,
                    f'Componente auto-indexado: {name}',
                    json.dumps([]),
                    json.dumps(['streamlit', 'python']),
                    json.dumps([gene_id, 'core', 'ui']),
                    date.today().isoformat(),
                ),
            )

    conn.commit()
    conn.close()
    print('[OK] Scanner finalizado: Todos os genes foram indexados.')


if __name__ == '__main__':
    scan_genome_folders()
