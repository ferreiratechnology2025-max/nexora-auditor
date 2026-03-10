import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class AdviceEngine:
    HARD_STOP_KEYWORDS = ('CRITICAL', 'SECURITY')

    def __init__(self, db_path: str | None = None):
        if db_path:
            self.db_path = db_path
        else:
            project_root = Path(__file__).resolve().parents[1]
            memory_root = os.getenv('MEMORY_ROOT') or str(project_root / 'memory')
            self.db_path = os.path.join(memory_root, 'sqlite', 'nexora_memory.db')

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._ensure_decisions_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_decisions_table(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
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
            conn.commit()
        finally:
            conn.close()

    def _clean_json_text(self, raw_text: str) -> str:
        return (raw_text or '').replace('```json', '').replace('```', '').strip()

    def parse_executor_payload(self, raw_text: str) -> Dict[str, Any]:
        clean = self._clean_json_text(raw_text)
        if not clean:
            return {}

        try:
            parsed = json.loads(clean)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def extract_advice(self, raw_text: str) -> List[str]:
        payload = self.parse_executor_payload(raw_text)
        advice_raw = payload.get('advice', []) if payload else []
        if not isinstance(advice_raw, list):
            return []

        advice_items: List[str] = []
        for item in advice_raw:
            if isinstance(item, str) and item.strip():
                advice_items.append(item.strip())
        return advice_items

    def has_hard_stop(self, advice_items: List[str]) -> bool:
        for advice in advice_items:
            upper = advice.upper()
            if any(keyword in upper for keyword in self.HARD_STOP_KEYWORDS):
                return True
        return False

    def register_advice(self, advice_items: List[str], task: str, outcome: str = 'advice_logged') -> int:
        if not advice_items:
            return 0

        timestamp = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        cursor = conn.cursor()
        try:
            for advice in advice_items:
                cursor.execute(
                    '''
                    INSERT INTO decisions (timestamp, agent, task, decision, outcome, tokens_used, cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (timestamp, 'advisor', task, advice, outcome, '', ''),
                )
            conn.commit()
            return len(advice_items)
        finally:
            conn.close()

    def analyze_and_record(self, raw_text: str, task: str) -> Dict[str, Any]:
        advice_items = self.extract_advice(raw_text)
        hard_stop = self.has_hard_stop(advice_items)

        saved_count = 0
        if advice_items:
            outcome = 'hard_stop' if hard_stop else 'advice_logged'
            saved_count = self.register_advice(advice_items, task=task, outcome=outcome)

        return {
            'advice': advice_items,
            'hard_stop': hard_stop,
            'saved_count': saved_count,
        }
