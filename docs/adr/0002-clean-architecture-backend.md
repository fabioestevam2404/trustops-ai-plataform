# ADR 0002 — Clean Architecture + DDD simplificado no backend

## Status

Aceito

## Contexto

O backend precisa orquestrar múltiplas ferramentas externas (SonarQube, Trivy, Bandit, RAGAS...), aplicar regras de negócio próprias (scoring, quality gates, certificação) e expor uma API estável — mantendo essas três preocupações desacopladas.

## Decisão

Estruturar o backend em camadas, conforme [seção 5.1](../../trustops-ai-platform.md#51-backend--trustops-api):

```
API Layer          → contratos HTTP (FastAPI routers)
Application Layer   → Assessment Service, Scoring Service, Certification Service
Domain Layer         → Project, Assessment, Finding, Certificate (entidades e regras)
Infrastructure Layer → PostgreSQL, Redis, Evidence Store, adaptadores de ferramentas externas
```

A camada de Domain não depende de nenhuma outra; Infrastructure implementa interfaces que o Domain/Application definem (inversão de dependência).

## Consequências

- Adaptadores de ferramentas (Semgrep, Trivy, etc.) trocáveis sem afetar a lógica de scoring.
- Mais boilerplate inicial (interfaces, injeção de dependência) comparado a uma estrutura MVC simples — aceito como custo do domínio ter regras de negócio não triviais (Trust Engine).
