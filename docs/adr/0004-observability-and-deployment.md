# ADR 0004 — Observability e deploy: escopo da Sprint 8

## Status

Aceito

## Contexto

A Sprint 8 do backlog pede Prometheus, Grafana, logs estruturados, alertas, Terraform e "deploy cloud". Duas categorias bem diferentes de trabalho: (1) observabilidade, que roda e é testável de verdade neste ambiente de desenvolvimento; (2) deploy em nuvem, que não pode ser executado de verdade aqui — não há credenciais de nenhum provedor cloud configuradas nesta sessão.

## Decisões

1. **Logging estruturado via `logging` da stdlib, não `structlog`.** Um `JsonFormatter` customizado (`backend/app/core/logging.py`) é suficiente para emitir JSON com os campos necessários (`timestamp`, `level`, `logger`, `message`, campos extras via `extra=`) sem adicionar uma dependência nova. Aplicado também aos loggers do uvicorn (`uvicorn`, `uvicorn.access`, `uvicorn.error`).

2. **Métricas via `prometheus-client` + `prometheus-fastapi-instrumentator`.** O instrumentator cobre métricas HTTP padrão (latência/status por rota) automaticamente; métricas de negócio (`trustops_assessments_total`, `trustops_assessment_duration_seconds`, `trustops_scanner_duration_seconds`, `trustops_scanner_errors_total`) são instrumentadas manualmente em `AssessmentService.run()`, no único ponto (`_run_tool`) por onde passam a maioria dos scanners, mais os dois blocos especiais (pytest, ai-trust).

3. **Prometheus + Alertmanager + Grafana como serviços locais no `docker-compose.yml`**, com provisioning automático (datasource + dashboard do Grafana carregam sozinhos ao subir). Validado de ponta a ponta nesta sessão: target `backend` `up` no Prometheus, métrica `trustops_assessments_total` visível após rodar um assessment real, dashboard "TrustOps Overview" com 5 painéis carregado via API do Grafana.

4. **Alertmanager com receiver placeholder.** As 3 regras de alerta (`HighScannerErrorRate`, `AssessmentFailureSpike`, `APIHighErrorRate`) carregam e avaliam de verdade no Prometheus, mas o Alertmanager não notifica ninguém — não há credenciais de Slack/e-mail/etc. configuradas. Documentado explicitamente como pendência de configuração antes de depender disso operacionalmente.

5. **Terraform mira uma única instância EC2 rodando `docker-compose`, não serviços gerenciados (ECS/Fargate/RDS/ElastiCache).** Decisão explícita para manter o escopo auditável e coerente com o que já existe e foi validado localmente — uma arquitetura gerenciada completa (VPC, IAM, task definitions) seria muito mais código sem poder ser testado contra uma conta AWS real neste ambiente.

6. **`terraform apply` não foi executado.** Sem credenciais AWS nesta sessão — rodar `apply` criaria recursos reais e geraria cobrança sem autorização explícita do usuário para uma ação dessas. O que foi validado: `terraform init -backend=false` (baixa o provider do registry público, não toca em nenhuma conta) e `terraform validate` (sucesso). Ver `infrastructure/terraform/README.md` para o passo a passo de aplicação real com credenciais próprias.

## Consequências

- A plataforma tem observabilidade real e testável hoje, mesmo sem nunca ter sido implantada em nuvem.
- O caminho para produção de verdade (aplicar o Terraform, configurar um receiver real no Alertmanager, adicionar TLS/backend remoto de state) fica claramente documentado como próximo passo, não como algo que este projeto finge ter feito.
- Se o projeto crescer a ponto de precisar de alta disponibilidade / múltiplos ambientes, a decisão de EC2+compose (ADR 0004) e sem backend remoto de state precisam ser revisitadas antes de qualquer uso em equipe.
