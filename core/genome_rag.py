import json
import os
import sqlite3
from datetime import date
from pathlib import Path


class GenomeRAGIndexer:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[1]
        memory_root = os.getenv('MEMORY_ROOT') or str(project_root / 'memory')
        genome_root = os.getenv('GENOME_ROOT') or str(project_root / 'code_genome')
        self.db_path = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')
        self.genome_root = Path(genome_root)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _upsert_gene(self, cursor, gene_id, name, path, description, dependencies, compatible_stacks, tags):
        cursor.execute(
            '''
            INSERT OR REPLACE INTO genome_index
            (id, name, path, description, dependencies, compatible_stacks, tags, last_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                gene_id,
                name,
                str(path),
                description,
                json.dumps(dependencies, ensure_ascii=False),
                json.dumps(compatible_stacks, ensure_ascii=False),
                json.dumps(tags, ensure_ascii=False),
                date.today().isoformat(),
            ),
        )

    def _index_legacy_core_genes(self, cursor):
        indexed = 0
        core_path = self.genome_root / 'core'
        if not core_path.exists():
            return indexed

        for folder in core_path.iterdir():
            if not folder.is_dir():
                continue
            if not (folder / 'GENOME.md').exists():
                continue

            gene_id = folder.name
            name = folder.name.replace('_', ' ').title()
            self._upsert_gene(
                cursor,
                gene_id=gene_id,
                name=name,
                path=folder,
                description=f'Componente auto-indexado: {name}',
                dependencies=[],
                compatible_stacks=['streamlit', 'python'],
                tags=[gene_id, 'core', 'ui'],
            )
            indexed += 1

        return indexed

    def _index_gene_json_packages(self, cursor):
        indexed = 0
        for folder in self.genome_root.iterdir():
            if not folder.is_dir() or folder.name == 'core':
                continue

            metadata_path = folder / 'gene.json'
            if not metadata_path.exists():
                continue

            try:
                metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
            except Exception:
                continue

            gene_id = metadata.get('id') or folder.name
            name = metadata.get('name') or folder.name.replace('_', ' ').title()
            description = metadata.get('description') or f'Gene auto-indexado: {name}'
            dependencies = metadata.get('dependencies') or []
            compatible_stacks = metadata.get('compatible_stacks') or ['python']
            tags = metadata.get('tags') or [gene_id]

            self._upsert_gene(
                cursor,
                gene_id=gene_id,
                name=name,
                path=folder,
                description=description,
                dependencies=dependencies,
                compatible_stacks=compatible_stacks,
                tags=tags,
            )
            indexed += 1

        return indexed

    def run(self):
        conn = self._connect()
        cursor = conn.cursor()

        legacy_count = self._index_legacy_core_genes(cursor)
        package_count = self._index_gene_json_packages(cursor)

        conn.commit()
        conn.close()

        total = legacy_count + package_count
        print(f'[OK] Genome RAG indexado. core={legacy_count}, gene_json={package_count}, total={total}')


if __name__ == '__main__':
    GenomeRAGIndexer().run()
