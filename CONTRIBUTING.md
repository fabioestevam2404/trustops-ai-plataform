# Contribuindo

## Ambiente local

```bash
cp .env.example .env
docker compose up -d
```

## Padrões de código (backend)

- Lint: `ruff check .`
- Type checking: `mypy app`
- Testes: `pytest`
- Cobertura mínima e demais gates de qualidade são aplicados pelo próprio Trust Engine da plataforma sobre este repositório (dogfooding).

## Commits

Mensagens de commit devem descrever o "porquê", não apenas o "o quê". Uma mudança por commit sempre que possível.

## Decisões de arquitetura

Mudanças arquiteturais relevantes devem ser registradas como ADR em [`docs/adr/`](docs/adr/), seguindo o formato dos ADRs existentes.
