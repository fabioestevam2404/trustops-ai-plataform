# Integração — Bandit

Executa Bandit (SAST para Python) sobre o repositório avaliado, normaliza os findings (`issue_severity` LOW/MEDIUM/HIGH mapeado direto) e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 3.** Código em `backend/app/infrastructure/scanners/bandit_runner.py`.
