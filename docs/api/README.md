# API

Documentação da API será expandida na Sprint 1 (CRUD de projetos, modelo de Assessment) e crescerá junto com cada sprint subsequente.

Enquanto isso, a API expõe automaticamente OpenAPI/Swagger em `/docs` quando rodando localmente (`docker compose up`).

Contratos de rastreabilidade de evidências já definidos (ver [ADR 0003](../adr/0003-evidence-store-traceability.md)):

```
GET /assessments/{id}
GET /assessments/{id}/findings
GET /assessments/{id}/reports/{tool}
```
