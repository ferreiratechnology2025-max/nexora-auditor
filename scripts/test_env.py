import os
from dotenv import load_dotenv

load_dotenv()
print(f"[OK] Workspace: {os.getenv('WORKSPACE_ROOT')}")
print(f"[OK] API Key configurada: {'Sim' if os.getenv('OPENROUTER_API_KEY') else 'Nao'}")
