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

Implementação do motor: `backend/app/application/trust_engine.py` (Sprint 4) — a pasta `trust-engine/` na raiz é documentação (ver seu README).

## Quality Score (implementado na Sprint 2)

Primeiro sub-score real, calculado em `backend/app/application/quality_score.py`: `0.6 × cobertura + 0.4 × taxa de sucesso dos testes − penalidade Ruff (cap 20)`, resultado limitado a [0, 100]. É um score de domínio (qualidade), não o `trust_score` consolidado — este último só existe a partir do Trust Engine (Sprint 4), que combinará Quality Score, Security Score e demais dimensões com pesos.

**Limitação conhecida do MVP**: o scanner de qualidade (`integrations/pytest`, `integrations/ruff`) roda pytest/Ruff usando o ambiente Python do próprio backend, sem instalar as dependências do repositório-alvo. Funciona plenamente para repositórios sem dependências externas de teste (o alvo natural de dogfooding é o próprio `backend/` desta plataforma); repositórios-alvo com dependências próprias geram falhas de import capturadas honestamente como findings, não um crash silencioso. Isolamento de dependências por assessment (venv dedicado) fica para uma sprint futura.

## Security Score (implementado na Sprint 3)

Segundo sub-score de domínio, calculado em `backend/app/application/security_score.py`: parte de 100 e subtrai uma penalidade por severidade de cada finding de segurança (`CRITICAL` -25, `HIGH` -10, `MEDIUM` -3, `LOW` -0.5), limitado a [0, 100]. Mesmo status do Quality Score: não é o `trust_score` consolidado (Sprint 4), e os pesos não são calibrados empiricamente.

Alimentado por quatro ferramentas (`integrations/bandit`, `integrations/semgrep`, `integrations/gitleaks`, `integrations/trivy`), cada uma rodando isolada — a falha de uma não invalida o assessment inteiro, vira um `Finding` de categoria `execution` visível nos resultados.

**Limitações conhecidas do MVP**:
- **Trivy roda sem o scanner `vuln`** (CVEs de dependências / SCA) — só `secret` e `misconfig`. Rodar `vuln` exigiria baixar e manter um banco de vulnerabilidades (dependência de rede em tempo de execução, ou imagem Docker maior se embutido no build). SCA de dependências fica para uma sprint futura.
- **Semgrep usa um ruleset local mínimo** (`backend/app/infrastructure/scanners/semgrep_rules.yml`), não o registro completo (`--config=auto`), para manter os scans herméticos (sem rede) e os testes determinísticos.

## Trust Score (implementado na Sprint 4)

Consolida os dois sub-scores em `backend/app/application/trust_engine.py`:

```python
trust_score = round(TRUST_WEIGHTS["quality"] * quality_score + TRUST_WEIGHTS["security"] * security_score)
```

Pesos iguais (`TRUST_WEIGHTS = {"quality": 0.5, "security": 0.5}`) como ponto de partida do MVP — a especificação não define valores; mesmo aviso de "não calibrado" dos demais scores.

A classificação segue exatamente a pseudológica da [seção 6](../../trustops-ai-platform.md#6-trust-engine--o-núcleo-do-produto): qualquer `Finding` `CRITICAL` em categoria de segurança (`security`/`secrets`/`misconfig`) força `certification_level = BLOCKED`, **independente do `trust_score`** — um `Finding` `CRITICAL` de categoria `execution` (falha de ferramenta, não vulnerabilidade real) não bloqueia. Sem bloqueio, o `trust_score` é classificado pela tabela de níveis acima.

Validado manualmente: um repositório com um segredo exposto obteve `trust_score: 25` mas `certification_level: BLOCKED` (a regra de bloqueio prevaleceu sobre o score); um repositório limpo obteve `trust_score: 100` e `certification_level: ENTERPRISE_TRUST`.

## Certification Engine (implementado na Sprint 6)

A entidade `Certificate` (id, assessment_id, project_id, version, certification_level, status, issued_at) é emitida **automaticamente** dentro de `AssessmentService.run()`, logo após o `certification_level` ser calculado — para todo assessment que chega a `COMPLETED`, inclusive os `BLOCKED` (um certificado `BLOCKED` também é um registro válido: "esta versão foi avaliada e reprovou"). Código em `backend/app/application/certificate_service.py`.

Novos endpoints:

```text
GET /assessments/{id}/certificate      certificado emitido para este assessment
GET /projects/{id}/certificates        histórico de certificados do projeto
GET /assessments/{id}/report           relatório estruturado (backend/app/application/report.py):
                                        project, version, trust_score, certification_level,
                                        status (APPROVED/BLOCKED/PENDING), findings por severidade
GET /projects/{id}/risk-register       findings CRITICAL/HIGH do assessment COMPLETED mais
                                        recente do projeto (backend/app/application/risk_register.py)
```

**Rastreabilidade do certificado até a evidência bruta**: o certificado referencia `assessment_id`; como `GET /assessments/{id}/reports/{tool}` (Sprint 2/3, ADR 0003) já dá acesso a todo relatório bruto daquele assessment, a cadeia completa (certificado → findings → relatório bruto da ferramenta) já existe sem duplicar armazenamento.

**Fora de escopo desta sprint**: revogação de certificado (`CertificateStatus` só tem `ISSUED`); exportação em PDF/HTML do relatório (fica JSON estruturado); Risk Register histórico entre múltiplos assessments (só reflete o mais recente, para não duplicar o mesmo risco a cada nova avaliação).
