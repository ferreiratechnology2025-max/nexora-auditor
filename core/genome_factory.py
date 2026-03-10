import ast
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class GenomeFactory:
    """Extrai expertise de alto valor e promove para gene plug-and-play."""

    def __init__(self, genome_root: Optional[str] = None):
        project_root = Path(__file__).resolve().parents[1]
        self.genome_root = Path(genome_root or os.getenv('GENOME_ROOT') or (project_root / 'code_genome')).resolve()

    def _iter_python_files(self, project_path: Path) -> List[Path]:
        ignored = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules', 'tests'}
        files: List[Path] = []
        for file_path in project_path.rglob('*.py'):
            if any(part in ignored for part in file_path.parts):
                continue
            files.append(file_path)
        return files

    def _symbol_quality_score(self, node: ast.AST, source_lines: List[str]) -> int:
        start = getattr(node, 'lineno', None)
        end = getattr(node, 'end_lineno', None)
        if start is None or end is None:
            return 0

        length = max(1, end - start + 1)
        score = 100

        if length < 8:
            score -= 25
        elif length > 80:
            score -= min(35, (length - 80) // 2)

        if ast.get_docstring(node) is None:
            score -= 10

        has_annotations = False
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_annotations = bool(node.returns) or any(arg.annotation for arg in node.args.args)
            if len(node.args.args) > 6:
                score -= 10
        if not has_annotations:
            score -= 5

        body_src = '\n'.join(source_lines[start - 1:end]).lower()
        if 'todo' in body_src or 'pass' in body_src:
            score -= 10

        return max(0, min(100, score))

    def _decouple_source(self, source: str) -> str:
        # Remove imports acoplados ao projeto "criador".
        blocked_prefixes = ('core.', 'scripts.', 'config.', 'workspace.', 'memory.')
        cleaned_lines: List[str] = []
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                lower = stripped.lower()
                if any(prefix in lower for prefix in blocked_prefixes):
                    continue
            cleaned_lines.append(line)

        cleaned = '\n'.join(cleaned_lines).strip()
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        return cleaned + '\n'

    def _infer_category(self, extracted_symbols: List[Dict[str, object]]) -> str:
        names = ' '.join(str(item.get('name', '')).lower() for item in extracted_symbols)
        if any(token in names for token in ('auth', 'login', 'token', 'jwt', 'password')):
            return 'auth'
        if any(token in names for token in ('db', 'database', 'repository', 'query')):
            return 'data'
        if any(token in names for token in ('api', 'route', 'endpoint')):
            return 'api'
        return 'core'

    def _infer_complexity(self, extracted_symbols: List[Dict[str, object]]) -> str:
        avg_score = sum(int(item.get('score', 0)) for item in extracted_symbols) / max(1, len(extracted_symbols))
        if avg_score >= 95:
            return 'high'
        if avg_score >= 85:
            return 'medium'
        return 'low'

    def extract_high_value_symbols(self, project_path: str, min_score: int = 90) -> List[Dict[str, object]]:
        root = Path(project_path).resolve()
        if not root.exists() or not root.is_dir():
            return []

        extracted: List[Dict[str, object]] = []
        for file_path in self._iter_python_files(root):
            try:
                source = file_path.read_text(encoding='utf-8')
                tree = ast.parse(source)
                lines = source.splitlines()
            except Exception:
                continue

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    score = self._symbol_quality_score(node, lines)
                    if score < min_score:
                        continue

                    start = getattr(node, 'lineno', 1)
                    end = getattr(node, 'end_lineno', start)
                    snippet = '\n'.join(lines[start - 1:end])
                    extracted.append(
                        {
                            'name': node.name,
                            'type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                            'score': score,
                            'source': self._decouple_source(snippet),
                            'origin': str(file_path.relative_to(root)).replace('\\', '/'),
                        }
                    )

        extracted.sort(key=lambda item: int(item.get('score', 0)), reverse=True)
        return extracted

    def promote_to_gene(self, project_path: str, health_score: int, min_health: int = 90, preferred_name: Optional[str] = None) -> Dict[str, object]:
        if health_score < min_health:
            return {
                'status': 'skipped',
                'reason': f'Health score insuficiente para promover gene ({health_score} < {min_health}).',
            }

        symbols = self.extract_high_value_symbols(project_path, min_score=90)
        if not symbols:
            return {
                'status': 'skipped',
                'reason': 'Nenhuma classe/funcao com score > 90 encontrada para extracao.',
            }

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        category = self._infer_category(symbols)
        gene_name = preferred_name.strip() if (preferred_name and preferred_name.strip()) else f'{category}_autogene_{timestamp}'

        gene_path = self.genome_root / gene_name
        code_dir = gene_path / 'code'
        tests_dir = gene_path / 'tests'
        code_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)

        extracted_code = '\n\n'.join(item['source'] for item in symbols)
        (code_dir / 'module.py').write_text(extracted_code + '\n', encoding='utf-8')

        complexity = self._infer_complexity(symbols)
        metadata = {
            'id': gene_name,
            'name': f'AutoGene {gene_name}',
            'version': '1.0.0',
            'category': category,
            'complexity': complexity,
            'tags': [category, 'autogene', 'extracted'],
            'source_project': str(Path(project_path).resolve()),
            'symbols': [
                {
                    'name': item['name'],
                    'type': item['type'],
                    'score': item['score'],
                    'origin': item['origin'],
                }
                for item in symbols
            ],
        }
        (gene_path / 'gene.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')

        # Reindexa genoma para o orquestrador enxergar o novo DNA.
        subprocess.run(['python', 'core/genome_rag.py'], cwd=str(Path(__file__).resolve().parents[1]), check=False)

        return {
            'status': 'promoted',
            'gene_name': gene_name,
            'gene_path': str(gene_path),
            'symbol_count': len(symbols),
            'top_score': int(symbols[0]['score']),
            'category': category,
        }

