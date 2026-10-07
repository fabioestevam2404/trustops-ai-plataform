# ADR 0006 — Autenticação via API Key

## Status

Aceito

## Contexto

Até esta mudança, a API não tinha nenhuma camada de autenticação: qualquer cliente com acesso de rede ao backend podia criar, listar, alterar ou deletar projetos e assessments, e ler relatórios/certificados de qualquer projeto. Aceitável enquanto a plataforma rodava só localmente durante o MVP (Sprints 0–8), mas é o maior gap de segurança antes de qualquer exposição real.

## Decisão

Autenticação via **API Key estática**, não JWT/login de usuário nem OAuth2/gateway. Avaliadas três opções:

1. **API Key simples** — um segredo opaco por cliente/integração, validado em cada request via header.
2. **JWT com login de usuário** — pressupõe modelo de usuário, sessão, fluxo de login/refresh.
3. **OAuth2 / API Gateway na frente da API** — delega autenticação a um componente externo (Auth0, Cognito, Keycloak).

API Key foi escolhida porque o consumidor hoje é majoritariamente máquina-a-máquina (CI/CD de outros repositórios chamando a API, a própria dashboard), não uma base de usuários humanos distintos precisando de RBAC. JWT exigiria construir todo um subsistema de usuários sem um requisito real ainda, e gateway/OAuth2 é desproporcional a uma plataforma sem deploy cloud aplicado. Fica registrado que isso é a opção certa **para o estágio atual** — se a dashboard evoluir para multiusuário com permissões por pessoa/time, revisitar para JWT (ver "Revisão futura" abaixo).

## Implementação

- Tabela `api_keys` (migration `d4e6f8a1b2c3`): `id`, `name`, `key_hash` (SHA-256, único), `created_at`, `revoked_at` (nullable).
- Chave em texto puro (`tops_<43 chars aleatórios>`, `secrets.token_urlsafe(32)`) é mostrada **apenas uma vez**, na criação — só o hash é persistido. SHA-256 simples é suficiente aqui porque a chave já tem alta entropia (não é uma senha curta escolhida por humano, onde bcrypt/scrypt fariam sentido contra brute-force).
- Sem endpoint HTTP para criar chaves — criaria um problema de ovo-e-galinha (precisaria de uma chave pra chamar o endpoint que cria chaves). Em vez disso, um CLI operacional: `docker compose exec backend python -m app.cli create-api-key --name <nome>`.
- Dependency `require_api_key` (`app/api/security.py`) lê o header `X-API-Key`, valida contra o hash e rejeita com `401` se ausente, inválida ou revogada.
- Aplicada no nível do router (`dependencies=[Depends(require_api_key)]`) em `/projects` e `/projects/{id}/assessments` e sub-rotas — protege tudo que lê ou escreve dados de projetos/assessments/certificados.
- **Deliberadamente fora da proteção**: `GET /health` (liveness/readiness probe, usado por orquestradores sem credencial), `GET /metrics` (scraping do Prometheus, rede interna) e `GET /` (root informativo).

## Consequências

- Elimina o acesso anônimo a todas as rotas de negócio — era o gap de segurança mais crítico listado para esta plataforma.
- Sem RBAC: uma chave válida tem acesso total (todos os projetos, todas as operações). Não há isolamento por projeto/equipe — aceito nesta versão, revisitar se surgir necessidade real de multi-tenancy.
- Sem rotação automática nem expiração por tempo — revogação é manual via `revoked_at`. Se uma chave vazar, a mitigação é revogar e emitir uma nova.
- `/metrics` continua aberto — métricas de negócio (contagem de projetos, scores) ficam visíveis a quem tiver acesso de rede ao backend. Aceitável em rede interna; se a API for exposta publicamente, isolar `/metrics` por rede/firewall, não por API key (quebraria o scraping do Prometheus).

## Revisão futura

Migrar para JWT com login de usuário quando/se a dashboard precisar de múltiplos usuários humanos com permissões distintas (RBAC por projeto ou por papel). API Key continuaria existindo em paralelo para consumidores máquina-a-máquina (CI/CD) — os dois não são mutuamente exclusivos.
