# Trust Framework

Lógica de scoring e certificação — especificada em detalhe nas seções [6](../../trustops-ai-platform.md#6-trust-engine--o-núcleo-do-produto) e [12](../../trustops-ai-platform.md#12-modelo-inicial-de-dados) da especificação executiva. Este documento não duplica a lógica; referencia a fonte única de verdade e evolui como changelog de decisões sobre pesos e thresholds.

## Princípios

1. **Bloqueadores primeiro**: vulnerabilidade crítica bloqueia certificação, independente do score.
2. **Consolidar, não substituir**: o score resume, mas cada finding é rastreável até o relatório bruto da ferramenta (ver [ADR 0003](../adr/0003-evidence-store-traceability.md)).
3. **Calibração empírica antes de gate de produção**: pesos e thresholds (75/85/95) definidos na especificação são o ponto de partida do MVP — não devem ser usados como gate obrigatório de release até serem validados contra dados reais de incidentes.

## Níveis de certificação (MVP)

| Score | Nível |
|---|---|
| < 75 | FOUNDATION |
| ≥ 75 | TRUSTED |
| ≥ 85 | HIGH_TRUST |
| ≥ 95 | ENTERPRISE_TRUST |

Implementação do motor: `trust-engine/` (Sprint 4).

## Quality Score (implementado na Sprint 2)

Primeiro sub-score real, calculado em `backend/app/application/quality_score.py`: `0.6 × cobertura + 0.4 × taxa de sucesso dos testes − penalidade Ruff (cap 20)`, resultado limitado a [0, 100]. É um score de domínio (qualidade), não o `trust_score` consolidado — este último só existe a partir do Trust Engine (Sprint 4), que combinará Quality Score, Security Score e demais dimensões com pesos.

**Limitação conhecida do MVP**: o scanner de qualidade (`integrations/pytest`, `integrations/ruff`) roda pytest/Ruff usando o ambiente Python do próprio backend, sem instalar as dependências do repositório-alvo. Funciona plenamente para repositórios sem dependências externas de teste (o alvo natural de dogfooding é o próprio `backend/` desta plataforma); repositórios-alvo com dependências próprias geram falhas de import capturadas honestamente como findings, não um crash silencioso. Isolamento de dependências por assessment (venv dedicado) fica para uma sprint futura.
