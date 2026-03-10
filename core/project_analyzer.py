import ast
from pathlib import Path
from typing import Dict, List, Set


class ProjectAnalyzer:
    CREATOR_IMPORT_PREFIXES = ('core', 'scripts', 'config', 'memory', 'app')

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()

    def _iter_python_files(self) -> List[Path]:
        if not self.project_path.exists() or not self.project_path.is_dir():
            return []

        ignored_parts = {'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules'}
        files: List[Path] = []
        for path in self.project_path.rglob('*.py'):
            if any(part in ignored_parts for part in path.parts):
                continue
            files.append(path)
        return files

    def _is_test_file(self, file_path: Path) -> bool:
        lowered_parts = {part.lower() for part in file_path.parts}
        name = file_path.name.lower()
        return 'tests' in lowered_parts or name.startswith('test_') or name.endswith('_test.py')

    def _module_name(self, file_path: Path) -> str:
        rel = file_path.relative_to(self.project_path)
        return '.'.join(rel.with_suffix('').parts)

    def _has_corresponding_test(self, code_file: Path, test_files: List[Path]) -> bool:
        code_stem = code_file.stem.lower()
        test_rel_set = {
            str(test_file.relative_to(self.project_path)).replace('\\', '/').lower()
            for test_file in test_files
        }

        candidates = {
            f'tests/test_{code_stem}.py',
            f'tests/{code_stem}_test.py',
        }

        parent_parts = [p.lower() for p in code_file.relative_to(self.project_path).parts]
        if 'app' in parent_parts:
            app_idx = parent_parts.index('app')
            module_parts = parent_parts[app_idx + 1:-1]
            if module_parts:
                path_prefix = '/'.join(module_parts)
                candidates.add(f'tests/{path_prefix}/test_{code_stem}.py')
                candidates.add(f'tests/{path_prefix}/{code_stem}_test.py')

        if candidates.intersection(test_rel_set):
            return True

        expected_tokens = {f'test_{code_stem}', f'{code_stem}_test'}
        for test_file in test_files:
            if test_file.stem.lower() in expected_tokens:
                return True

        return False

    def _collect_creator_leaks(self, py_files: List[Path]) -> List[str]:
        leaks: List[str] = []

        for file_path in py_files:
            if self._is_test_file(file_path):
                continue

            rel_name = str(file_path.relative_to(self.project_path)).replace('\\', '/')
            try:
                tree = ast.parse(file_path.read_text(encoding='utf-8'))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name
                        if import_name.startswith(self.CREATOR_IMPORT_PREFIXES):
                            leaks.append(f'{rel_name} -> import {import_name}')
                elif isinstance(node, ast.ImportFrom) and node.module:
                    import_name = node.module
                    if import_name.startswith(self.CREATOR_IMPORT_PREFIXES):
                        leaks.append(f'{rel_name} -> from {import_name} import ...')

        return sorted(set(leaks))

    def get_health_score(self) -> Dict[str, object]:
        py_files = self._iter_python_files()
        test_files = [f for f in py_files if self._is_test_file(f)]
        code_files = [f for f in py_files if not self._is_test_file(f)]

        coverage_hits = [f for f in code_files if self._has_corresponding_test(f, test_files)]
        untested_files = [
            str(f.relative_to(self.project_path)).replace('\\', '/')
            for f in code_files
            if f not in coverage_hits
        ]

        coverage_ratio = (len(coverage_hits) / len(code_files)) if code_files else 1.0

        complex_files: List[str] = []
        for file_path in code_files:
            try:
                line_count = len(file_path.read_text(encoding='utf-8').splitlines())
            except Exception:
                continue
            if line_count > 200:
                rel = str(file_path.relative_to(self.project_path)).replace('\\', '/')
                complex_files.append(f'{rel} ({line_count} linhas)')

        creator_leaks = self._collect_creator_leaks(py_files)

        score = 100
        score -= int((1 - coverage_ratio) * 50)
        score -= min(len(complex_files) * 12, 30)
        score -= min(len(creator_leaks) * 20, 40)
        score = max(0, min(100, score))

        return {
            'score': score,
            'metrics': {
                'python_files': len(py_files),
                'code_files': len(code_files),
                'test_files': len(test_files),
                'coverage_ratio': round(coverage_ratio, 2),
                'untested_files': untested_files,
                'complex_files_over_200_lines': complex_files,
                'creator_to_creature_import_leaks': creator_leaks,
            },
        }

    def map_dependencies(self) -> Dict[str, object]:
        py_files = self._iter_python_files()
        module_by_file = {file_path: self._module_name(file_path) for file_path in py_files}
        known_modules = set(module_by_file.values())

        dependency_map: Dict[str, List[str]] = {}
        for file_path, module_name in module_by_file.items():
            deps: Set[str] = set()
            try:
                tree = ast.parse(file_path.read_text(encoding='utf-8'))
            except Exception:
                dependency_map[module_name] = []
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported = alias.name
                        for known in known_modules:
                            if imported == known or imported.startswith(f'{known}.'):
                                deps.add(known)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported = node.module
                    for known in known_modules:
                        if imported == known or imported.startswith(f'{known}.'):
                            deps.add(known)

            deps.discard(module_name)
            dependency_map[module_name] = sorted(deps)

        cycles: List[List[str]] = []
        visiting: Set[str] = set()
        visited: Set[str] = set()

        def dfs(node: str, stack: List[str]) -> None:
            if node in visiting:
                if node in stack:
                    cycle = stack[stack.index(node):] + [node]
                    if cycle not in cycles:
                        cycles.append(cycle)
                return
            if node in visited:
                return

            visiting.add(node)
            stack.append(node)
            for dep in dependency_map.get(node, []):
                dfs(dep, stack)
            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for module_name in dependency_map:
            dfs(module_name, [])

        return {
            'dependencies': dependency_map,
            'potential_cycles': cycles,
        }
