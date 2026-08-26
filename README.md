# TrustOps AI Platform

Plataforma de DevSecOps, Software Quality e AI Trust que avalia automaticamente repositórios de software, consolida evidências técnicas de múltiplas ferramentas (SonarQube, Trivy, Bandit, pytest, OWASP, RAGAS...) e produz um **Trust Score** e uma **certificação interna** por versão.

A plataforma consolida, não substitui: cada relatório bruto permanece acessível no Evidence Store, com rastreabilidade completa do score até a fonte. Veja a especificação completa em [`trustops-ai-platform.md`](trustops-ai-platform.md).

## Documentação

- [Especificação executiva](trustops-ai-platform.md) — visão, arquitetura, stack, backlog de sprints
- [Arquitetura](docs/architecture/README.md)
- [ADRs](docs/adr/)
- [Trust Framework](docs/trust-framework/README.md) — lógica de scoring e certificação

## Quick start (desenvolvimento local)

```bash
cp .env.example .env
docker compose up -d
```

A API sobe em `http://localhost:8001` (porta 8000 remapeada para 8001 no host para não colidir com outros projetos locais; internamente o container continua na 8000). Docs interativas em `http://localhost:8001/docs`. O dashboard sobe em `http://localhost:5173`.

Aplicar as migrations (cria as tabelas `projects`, `assessments`, `findings` e `certificates`):

```bash
docker compose exec backend alembic upgrade head
```

Rodar os testes do backend:

```bash
docker compose exec backend pytest
```

### Endpoints disponíveis

```
GET    /health
POST   /projects
GET    /projects
GET    /projects/{id}
PATCH  /projects/{id}
DELETE /projects/{id}

POST   /projects/{project_id}/assessments        cria e roda a avaliação completa (síncrono)
GET    /projects/{project_id}/assessments        lista avaliações do projeto
GET    /assessments/{id}                         status, quality/security/ai_trust/trust_score, certification_level
GET    /assessments/{id}/findings                findings normalizados
GET    /assessments/{id}/reports/{tool}           relatório bruto (pytest | coverage | ruff |
                                                   bandit | semgrep | gitleaks | trivy | ai-trust)
GET    /assessments/{id}/certificate              certificado emitido (automático ao concluir)
GET    /assessments/{id}/report                   relatório estruturado (project/version/scores/
                                                   status/findings por severidade)
GET    /projects/{project_id}/certificates        histórico de certificados do projeto
GET    /projects/{project_id}/risk-register       findings CRITICAL/HIGH do assessment mais recente
```

## Estrutura do repositório

Monorepo — ver [seção 8 da especificação](trustops-ai-platform.md#8-estrutura-do-repositório-github) para o racional.

```
backend/          API (FastAPI, Clean Architecture)
frontend/         Dashboard (React + Vite + Tailwind + Recharts)
trust-engine/     Motor de scoring e certificação (código real em backend/app/application)
integrations/     Adaptadores de ferramentas (Semgrep, Trivy, Gitleaks, pytest...)
infrastructure/   Docker, Terraform, Kubernetes
evidence/         Convenções do Evidence Store (relatórios brutos rastreáveis)
docs/             Arquitetura, ADRs, API, Trust Framework
```

## Status

Sprint 7 — AI Trust Assessment (avaliação heurística de RAG/hallucination e prompt injection via `ai-eval/dataset.json` no repositório-alvo, AI Trust Score, trust_score com pesos dinâmicos). Veja o backlog completo na [seção 9 da especificação](trustops-ai-platform.md#9-backlog-executivo-de-sprints).
