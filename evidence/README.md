# Evidence Store

Convenção de armazenamento dos relatórios brutos gerados por cada ferramenta integrada (SonarQube, Trivy, Bandit, pytest, Semgrep, Gitleaks, RAGAS...). Ver [ADR 0003](../docs/adr/0003-evidence-store-traceability.md) para o racional completo: a plataforma consolida evidências no Trust Score, mas nunca descarta o relatório original.

## Layout (MVP — filesystem local)

```
evidence/store/{assessment_id}/{tool}.{json|sarif|html}
```

`evidence/store/` **não é versionado** (ver `.gitignore`) — é o volume montado pelo container `backend` via `docker-compose.yml`, apontado por `EVIDENCE_STORE_PATH`. Em produção (Sprint 8+), este layout migra para object storage (ex.: S3-compatible), mantendo a mesma convenção de chave `{assessment_id}/{tool}`.
