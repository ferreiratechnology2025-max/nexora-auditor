from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class FileChange(BaseModel):
    file_path: str
    action: str = Field(..., description="create | update | delete")
    content: Optional[str] = None


class ExecutorResponse(BaseModel):
    status: str = Field(..., description="success | partial | error")
    analysis: str = Field(..., description="Análise técnica do que foi feito")
    changes: List[FileChange]
    issues: List[str] = Field(default_factory=list)
    advice: List[str] = Field(default_factory=list, description="Conselhos técnicos para o orquestrador")
    confidence: float = Field(..., ge=0, le=1)


# Este schema garante que o GPT-4o-mini não envie texto puro,
# mas sim uma estrutura que o Nexora saiba ler.
