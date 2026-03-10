import os
from pathlib import Path
from typing import List, Optional

from core.executor_schema import FileChange


class FileManager:
    """Gerencia leitura e escrita segura de arquivos no workspace."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else None

    def _resolve_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = Path.cwd() / path

        resolved = path.resolve()
        if self.workspace_root and not str(resolved).startswith(str(self.workspace_root)):
            raise ValueError(f'Arquivo fora do workspace permitido: {resolved}')

        return resolved

    def read_file(self, file_path: str) -> str:
        target = self._resolve_path(file_path)
        if not target.exists():
            raise FileNotFoundError(f'Arquivo nao encontrado: {target}')
        return target.read_text(encoding='utf-8')

    def atomic_write(self, file_path: str, content: str) -> str:
        target = self._resolve_path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = target.with_suffix(target.suffix + '.tmp')
        with open(tmp_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, target)
        return str(target)

    def apply_change(self, change: FileChange) -> str:
        target = self._resolve_path(change.file_path)

        if change.action == 'delete':
            if target.exists():
                target.unlink()
            return str(target)

        if change.action in {'create', 'update'}:
            if change.content is None:
                raise ValueError(f'content obrigatorio para acao {change.action}')
            return self.atomic_write(str(target), change.content)

        raise ValueError(f'Acao invalida: {change.action}')

    def apply_changes(self, changes: List[FileChange]) -> List[str]:
        return [self.apply_change(change) for change in changes]
