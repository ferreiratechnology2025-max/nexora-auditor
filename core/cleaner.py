import os
import shutil
import time
from pathlib import Path
from typing import Dict, Optional


class Cleaner:
    """Purifica o workspace removendo artefatos entre missões."""

    def __init__(self, workspace_root: Optional[str] = None):
        default_root = os.getenv('WORKSPACE_ROOT')
        self.workspace_root = Path(workspace_root or default_root or '').resolve() if (workspace_root or default_root) else None

    def _is_safe_workspace(self, path: Path) -> bool:
        resolved = path.resolve()
        if len(resolved.parts) <= 1:
            return False
        text = str(resolved).lower().replace('\\', '/')
        return '/workspace' in text or text.endswith('/workspace')

    def _remove_item_with_retry(self, item: Path, retries: int = 3, delay_seconds: float = 1.2) -> Optional[str]:
        for attempt in range(1, retries + 1):
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                return None
            except Exception as exc:
                if attempt == retries:
                    return f'{item}: {exc}'
                time.sleep(delay_seconds)
        return None

    def sanitize_workspace(self, workspace_path: Optional[str] = None) -> Dict[str, object]:
        target = Path(workspace_path).resolve() if workspace_path else self.workspace_root
        if target is None:
            return {'status': 'skipped', 'reason': 'Workspace root nao configurado.', 'removed_items': 0}

        if not target.exists() or not target.is_dir():
            return {'status': 'skipped', 'reason': 'Workspace inexistente.', 'removed_items': 0, 'workspace': str(target)}

        if not self._is_safe_workspace(target):
            return {
                'status': 'blocked',
                'reason': f'Caminho inseguro para limpeza: {target}',
                'removed_items': 0,
                'workspace': str(target),
            }

        removed_items = 0
        errors = []

        for item in list(target.iterdir()):
            error = self._remove_item_with_retry(item)
            if error:
                errors.append(error)
            else:
                removed_items += 1

        return {
            'status': 'success' if not errors else 'partial',
            'workspace': str(target),
            'removed_items': removed_items,
            'errors': errors,
            'workspace_purified': not errors,
        }
