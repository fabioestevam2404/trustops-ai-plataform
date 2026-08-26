# Docker

Configuração local já vive em [`docker-compose.yml`](../../docker-compose.yml) na raiz e [`backend/Dockerfile`](../../backend/Dockerfile). O deploy da Sprint 8 (ver [`infrastructure/terraform/`](../terraform/)) reusa exatamente esse mesmo `docker-compose.yml` numa instância EC2 — não há ainda imagens de produção multi-stage separadas; fica registrado como limitação conhecida em [ADR 0004](../../docs/adr/0004-observability-and-deployment.md), não implementado neste MVP.
