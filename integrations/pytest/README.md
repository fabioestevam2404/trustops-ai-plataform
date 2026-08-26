# Integração — pytest

Executa pytest + coverage.py sobre o repositório avaliado, normaliza os resultados em Quality Findings e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 2.** O código real vive em `backend/app/infrastructure/scanners/pytest_runner.py` — esta pasta na raiz do monorepo é documentação, não código executável: o build do container do backend usa `./backend` como contexto (ver `docker-compose.yml`), então a implementação fica dentro de `backend/`.

Limitação atual do MVP: o scanner roda pytest usando o ambiente Python do próprio backend, sem instalar as dependências do repositório-alvo. Funciona plenamente para repositórios sem dependências externas de teste; repositórios com dependências próprias podem gerar falhas de import, capturadas como findings. Ver [Trust Framework](../../docs/trust-framework/README.md).
