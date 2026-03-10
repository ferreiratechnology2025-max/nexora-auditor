from typing import Dict, List

from core.project_analyzer import ProjectAnalyzer


class SelfImprovementEngine:
    def run(self, project_path: str) -> Dict[str, object]:
        analyzer = ProjectAnalyzer(project_path)
        health = analyzer.get_health_score()
        dependencies = analyzer.map_dependencies()
        refactoring_suggestions = self._build_refactoring_suggestions(health, dependencies)

        return {
            'health': health,
            'dependencies': dependencies,
            'refactoring_suggestions': refactoring_suggestions,
        }

    def _build_refactoring_suggestions(self, health: Dict[str, object], dependencies: Dict[str, object]) -> List[str]:
        metrics = (health.get('metrics') or {}) if isinstance(health, dict) else {}

        suggestions: List[str] = []

        untested_files = metrics.get('untested_files', []) or []
        if untested_files:
            sample = ', '.join(untested_files[:2])
            suggestions.append(
                f'Sugerido criar testes unitarios correspondentes em tests/ para: {sample}.'
            )

        complex_files = metrics.get('complex_files_over_200_lines', []) or []
        if complex_files:
            sample = ', '.join(complex_files[:2])
            suggestions.append(
                f'Sugerido dividir arquivos muito grandes em modulos menores para reduzir acoplamento: {sample}.'
            )

        import_leaks = metrics.get('creator_to_creature_import_leaks', []) or []
        if import_leaks:
            sample = '; '.join(import_leaks[:2])
            suggestions.append(
                f'Sugerido isolar fronteiras de arquitetura removendo imports do Criador na Criatura: {sample}.'
            )

        cycles = dependencies.get('potential_cycles', []) if isinstance(dependencies, dict) else []
        if cycles:
            sample_cycle = ' -> '.join(cycles[0])
            suggestions.append(
                f'Sugerido quebrar dependencia circular detectada: {sample_cycle}.'
            )

        while len(suggestions) < 2:
            suggestions.append(
                'Sugerido isolar a logica de DB em repositorio separado e padronizar interfaces de servico.'
            )

        return suggestions[:3]
