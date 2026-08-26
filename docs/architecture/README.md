# Arquitetura

Visão de alto nível e arquitetura de componentes: ver seções [4](../../trustops-ai-platform.md#4-arquitetura-técnica-completa) e [5](../../trustops-ai-platform.md#5-arquitetura-de-componentes) da especificação executiva.

Resumo:

- **Backend**: Python + FastAPI, Clean Architecture + DDD simplificado (API → Application → Domain → Infrastructure).
- **Trust Engine**: motor de normalização, pesos, penalidades e cálculo do Trust Score — módulo dedicado (`trust-engine/`), consumido pelo backend.
- **Evidence Store**: armazenamento dos relatórios brutos de cada ferramenta, indexado por `assessment_id` + `tool` — ver [ADR 0003](../adr/0003-evidence-store-traceability.md).
- **Persistência**: PostgreSQL (dados relacionais) + Redis (cache/broker).
- **Frontend**: React + TypeScript, consome a API via REST.
- **Observabilidade**: logs estruturados (JSON, stdlib `logging`), métricas via `prometheus-client`/`fastapi-instrumentator` (`GET /metrics`), Prometheus + Alertmanager + Grafana como serviços locais no `docker-compose.yml`, dashboard e alertas provisionados automaticamente — ver [ADR 0004](../adr/0004-observability-and-deployment.md).
- **Deploy**: Terraform em `infrastructure/terraform/` mirando uma instância EC2 rodando a stack via docker-compose — código validado (`terraform validate`), **não aplicado** nesta sessão (sem credenciais de nuvem). Ver [ADR 0004](../adr/0004-observability-and-deployment.md) e o README da pasta.

Decisões arquiteturais registradas como ADRs ficam em [`../adr/`](../adr/).
