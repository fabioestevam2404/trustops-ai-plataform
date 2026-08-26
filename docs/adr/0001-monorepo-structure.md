# ADR 0001 — Monorepo para o MVP

## Status

Aceito

## Contexto

O projeto tem múltiplos componentes desde o início: API backend, frontend, trust engine, integrações com ferramentas de terceiros e infraestrutura. É preciso decidir entre um monorepo ou múltiplos repositórios independentes.

## Decisão

Adotar um **monorepo** durante o MVP e as sprints iniciais (0 a 8), com a estrutura descrita na [seção 8](../../trustops-ai-platform.md#8-estrutura-do-repositório-github) da especificação.

## Consequências

- Facilita mudanças que atravessam backend, trust-engine e integrações no mesmo commit/PR, o que é comum nesta fase (o domínio ainda está sendo definido).
- CI único mais simples de manter enquanto o time é pequeno.
- Revisitar esta decisão se o projeto crescer a ponto de times/deploys independentes por componente justificarem repos separados (ex.: quando o frontend tiver ciclo de release próprio).
