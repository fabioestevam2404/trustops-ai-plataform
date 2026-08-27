# Integração — pytest

Executa pytest + coverage.py sobre o repositório avaliado, normaliza os resultados em Quality Findings e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 2.** O código real vive em `backend/app/infrastructure/scanners/pytest_runner.py` — esta pasta na raiz do monorepo é documentação, não código executável: o build do container do backend usa `./backend` como contexto (ver `docker-compose.yml`), então a implementação fica dentro de `backend/`.

Antes de rodar, o scanner tenta instalar as dependências do próprio repositório-alvo (`uv.lock`, `requirements.txt` ou `pyproject.toml`) num venv isolado via `backend/app/infrastructure/scanners/dependency_installer.py` — ver [ADR 0005](../../docs/adr/0005-target-dependency-installation.md). Quando bem-sucedido, pytest roda pelo Python desse venv em vez do ambiente do próprio backend, então importa as dependências reais do alvo. Sem manifesto reconhecido, ou em caso de falha/timeout na instalação, o comportamento cai no original: roda no ambiente Python do próprio backend, e falhas de import viram findings, não crash silencioso. Ver [Trust Framework](../../docs/trust-framework/README.md).
