# Integração — AI Trust

Avalia RAG/hallucination e resistência a prompt injection a partir de um dataset fornecido pelo repositório-alvo (`ai-eval/dataset.json`), e persiste o relatório bruto (métricas por entrada) no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 7.** Código em `backend/app/infrastructure/scanners/ai_trust_runner.py`.

**Decisão de escopo do MVP**: não usa RAGAS/DeepEval reais (que dependem de um LLM externo como "juiz" — API key, custo por avaliação, resultados não-determinísticos). Usa uma heurística determinística de overlap léxico (similaridade de Jaccard) entre resposta/contexto e detecção de vazamento de marcador para prompt injection — hermético, sem rede, sem custo. Documentado em detalhe em [Trust Framework](../../docs/trust-framework/README.md#ai-trust-score-implementado-na-sprint-7).

Se o repositório-alvo não tiver `ai-eval/dataset.json`, esta dimensão simplesmente não se aplica (`ai_trust_score: null`).
