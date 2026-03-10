import os

try:
    import docker
    _docker_available = True
except ImportError:
    docker = None  # type: ignore
    _docker_available = False


class TestRunner:
    __test__ = False

    def __init__(self):
        self.client = None
        if _docker_available and docker is not None:
            try:
                self.client = docker.from_env()
                print('[INFO] Docker SDK conectado com sucesso.')
            except Exception:
                self.client = None
                print('[AVISO] Docker nao detectado. Testes reais desativados.')
        else:
            print('[AVISO] Docker nao instalado. Testes reais desativados.')

    def run_workspace_test(self, project_path):
        """
        Realiza o build da imagem para validar se o codigo gerado e compilavel.
        """
        if not self.client:
            return False

        # O contexto do build deve ser a raiz do projeto para que o COPY funcione
        dockerfile_rel = 'infra/docker/backend.dockerfile'

        print(f'[TESTE] Iniciando build de validacao em: {project_path}')
        try:
            self.client.images.build(
                path=project_path,  # Raiz do projeto (onde esta o backend/)
                dockerfile=dockerfile_rel,
                tag='nexora-test-build',
                rm=True,
            )
            return True
        except Exception as e:
            print(f'[FALHA] Build falhou: {e}')
            return False


if __name__ == '__main__':
    if not _docker_available:
        print("[AVISO] Pacote 'docker' nao instalado. Execute: pip install -r requirements.txt")
    else:
        try:
            runner = TestRunner()
            print('[OK] TestRunner pronto.' if runner.client else '[AVISO] Docker Desktop nao detectado.')
        except Exception as ex:
            print(f'[AVISO] {ex}')
