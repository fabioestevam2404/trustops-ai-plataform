# Trust Engine

Motor de normalização, pesos, penalidades e cálculo do Trust Score. Ver [docs/trust-framework](../docs/trust-framework/README.md) e [seção 6](../trustops-ai-platform.md#6-trust-engine--o-núcleo-do-produto) da especificação.

**Implementado na Sprint 4.** Código em `backend/app/application/trust_engine.py` — esta pasta na raiz do monorepo é documentação, não código executável (mesmo motivo já registrado em `integrations/*`: o build do container do backend usa `./backend` como contexto).

```
scoring/         → compute_trust_score() em trust_engine.py: média ponderada de
                   quality_score + security_score (pesos em TRUST_WEIGHTS)
policies/        → classify_certification() em trust_engine.py: qualquer finding
                   CRITICAL de segurança bloqueia, independente do score
certification/   → mesma função — o nível de certificação é o resultado da
                   classificação (BLOCKED ou FOUNDATION/TRUSTED/HIGH_TRUST/ENTERPRISE_TRUST)
tests/           → backend/tests/test_trust_engine.py
```
