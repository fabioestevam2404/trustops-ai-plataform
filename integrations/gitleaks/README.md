# Integração — Gitleaks

Executa Gitleaks (detecção de secrets) sobre a árvore de trabalho do repositório avaliado e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)). Todo segredo encontrado vira um `Finding` de severidade `CRITICAL`.

**Implementado na Sprint 3.** Binário instalado no `backend/Dockerfile` (não é pacote pip — release Go, versão pinada `v8.30.1`). Código em `backend/app/infrastructure/scanners/gitleaks_runner.py`.
