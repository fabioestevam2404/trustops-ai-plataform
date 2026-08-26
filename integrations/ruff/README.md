# Integração — Ruff

Executa Ruff (`ruff check --output-format=json`) sobre o repositório avaliado, normaliza as violações em Quality Findings (severidade MEDIUM para códigos `E`/`F`, LOW para o restante) e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 2.** O código real vive em `backend/app/infrastructure/scanners/ruff_runner.py` — esta pasta na raiz do monorepo é documentação, não código executável (o build do container do backend usa `./backend` como contexto).
