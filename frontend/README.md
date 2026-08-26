# Frontend

Dashboard executivo — React + TypeScript + Vite + Tailwind CSS + Recharts, `react-router-dom` para roteamento e `@tanstack/react-query` para data fetching.

**Implementado na Sprint 5.**

## Views

- **Lista de projetos** (`/`) — projetos cadastrados + formulário para adicionar um novo (`POST /projects`).
- **Detalhe do projeto** (`/projects/:projectId`) — botão "Rodar avaliação" (`POST /projects/{id}/assessments`, síncrono — pode levar de segundos a poucos minutos), histórico de avaliações e gráfico de Trust Score ao longo do tempo (Recharts).
- **Detalhe do assessment** (`/assessments/:assessmentId`) — quality/security/trust score, badge de certificação, findings críticos destacados e tabela completa de findings.

## Desenvolvimento local

Via `docker compose up -d` (raiz do projeto) — sobe em `http://localhost:5173`, aponta para a API em `http://localhost:8001` (`VITE_API_BASE_URL`).

```bash
npm run dev      # servidor de desenvolvimento
npm run build    # type-check (tsc) + build de produção
npm run lint     # oxlint
npm test         # vitest
```

## Limitação conhecida

Sem verificação visual automatizada (não há ferramenta de browser disponível no ambiente de desenvolvimento assistido) — validado via build, testes de componente (Vitest + React Testing Library) e checagem manual das respostas da API/CORS via `curl`.
