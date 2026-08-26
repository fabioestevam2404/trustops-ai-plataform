# ADR 0003 — Evidence Store: consolidar sem substituir

## Status

Aceito

## Contexto

O Trust Score reduz múltiplos relatórios heterogêneos (SonarQube, Trivy, Bandit, pytest, OWASP, RAGAS...) a um número e um nível de certificação. Isso cria dois riscos identificados na análise do projeto:

1. **Perda de granularidade** — o score pode esconder qual foi o achado real que motivou uma penalidade, levando a um falso senso de segurança e a *automation bias* (confiar no score e parar de ler os relatórios originais).
2. **Falsos positivos amplificados** — sem preservar o relatório original, não há como auditar por que uma ferramenta específica gerou um finding questionável.

## Decisão

A plataforma nunca descarta os relatórios brutos das ferramentas. Cada execução de ferramenta persiste dois artefatos:

- **Finding normalizado** (`tool`, `severity`, `category`, `description`) — usado pelo Trust Engine.
- **Evidence** (relatório bruto original, `json`/`sarif`/`html`) — persistido no Evidence Store, indexado por `assessment_id` + `tool`.

A API expõe ambos separadamente:

```
GET /assessments/{id}                  → Trust Score consolidado
GET /assessments/{id}/findings         → findings normalizados
GET /assessments/{id}/reports/{tool}   → relatório bruto original
```

A captura de evidências começa já nas Sprints 2 e 3 (Quality e Security Assessment), não é deixada para o fim do projeto — senão os primeiros relatórios brutos nunca são capturados retroativamente.

## Consequências

- Todo nível de certificação é rastreável até o relatório original que o sustenta.
- Custo de armazenamento adicional (relatórios brutos de SAST/DAST podem ser grandes) — aceito, mitigado por não versionar `evidence/store/` no Git (ver `.gitignore`) e por ser um requisito de auditoria, não opcional.
- Cada integração (`integrations/<tool>/`) precisa manter um parser para dois formatos de saída (bruto + normalizado), não apenas um.
