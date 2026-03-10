import os

import openai
from dotenv import load_dotenv


EXECUTOR_SYSTEM_PROMPT = (
    "Você é o Nexora Codex. Suas respostas devem ser estritamente em JSON, "
    "seguindo o ExecutorResponse schema. Analise a tarefa, proponha as mudanças "
    "e, se identificar riscos arquiteturais, use o campo advice para notificar "
    "o orquestrador."
)


class NexoraLLM:
    def __init__(self):
        load_dotenv()

        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self.api_key = os.getenv('OPENROUTER_API_KEY', '')

        if not self.api_key:
            self.client = None
            return

        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def call(self, model, prompt, stream=False, role=None):
        if not self.client:
            return '[ERRO] OPENROUTER_API_KEY nao configurada no .env.'

        try:
            messages = []
            if role == 'executor':
                messages.append({'role': 'system', 'content': EXECUTOR_SYSTEM_PROMPT})

            messages.append({'role': 'user', 'content': prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
            )

            if stream:
                parts = []
                for chunk in response:
                    content = ''
                    if chunk.choices and chunk.choices[0].delta:
                        content = chunk.choices[0].delta.content or ''
                    if content:
                        parts.append(content)
                return ''.join(parts)

            return response.choices[0].message.content
        except Exception as e:
            return f'[ERRO] Falha na comunicacao com OpenRouter: {str(e)}'


if __name__ == '__main__':
    llm = NexoraLLM()
    print('[TESTE] Chamando modelo default...')
    result = llm.call('openai/gpt-4o-mini', 'Diga "Nexora Online"')
    print(f'Resposta: {result}')
