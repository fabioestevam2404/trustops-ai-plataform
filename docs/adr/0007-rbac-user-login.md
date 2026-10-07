# ADR 0007 — RBAC via login de usuário (JWT) ao lado da API Key

## Status

Aceito

## Contexto

A [ADR 0006](0006-api-key-authentication.md) resolveu o acesso anônimo à API, mas deixou todo portador de uma API Key com acesso total — sem distinção entre "pode alterar/deletar projetos" e "só precisa consultar". A própria ADR 0006 já previa essa evolução: "migrar para JWT com login de usuário quando/se a dashboard precisar de múltiplos usuários humanos com permissões distintas".

## Decisão

1. **Papéis globais, não por projeto.** Dois papéis: `admin` (tudo) e `viewer` (somente leitura). Sem conceito de "dono do projeto" ou membership por projeto — não há ainda necessidade real de isolar projetos entre times/clientes na mesma instância. Se isso surgir, é a próxima evolução natural (ver ADR 0006, mesma lógica de "resolver o problema de agora, não o hipotético").

2. **API Key e JWT coexistem, não se substituem.** API Key continua sendo para clientes máquina-a-máquina (CI/CD, integrações) e carrega acesso total por definição — não tem papel associado, não é uma pessoa. JWT é para humanos logados na dashboard e carrega o papel escolhido na criação do usuário. As duas formas de autenticação são aceitas em qualquer rota protegida; a regra de autorização (`require_admin` vs `require_authenticated`) decide o que cada uma pode fazer.

3. **JWT stateless, sem round-trip ao banco por request.** O token carrega `sub` (id), `email` e `role` como claims, assinados com `JWT_SECRET_KEY` (HS256, expiração de 8h). Validar o token é decodificar e confiar nas claims — não há consulta ao usuário no banco a cada request. Consequência aceita: se o papel de um usuário mudar ou a conta for revogada, isso só reflete depois que os tokens emitidos antes expirarem (até 8h) — igual à maioria dos sistemas JWT stateless, e adequado à janela curta de expiração escolhida.

4. **Sem endpoint de registro.** Mesma lógica da ADR 0006 para API Keys: usuários são criados via CLI (`docker compose exec backend python -m app.cli create-user --email <email> --role admin|viewer`, senha digitada interativamente via `getpass`, nunca em texto plano na linha de comando), não por um endpoint público — evita abrir de novo a porta que a ADR 0006 fechou.

5. **Senha com bcrypt, não SHA-256.** Diferente da API Key (ADR 0006, SHA-256 simples porque a chave já tem alta entropia), senha de usuário é escolhida por humano e de baixa entropia — aqui o custo computacional do bcrypt contra brute-force é o ponto, não um detalhe de implementação.

## Consequências

- Rotas de leitura (`GET`) aceitam qualquer principal autenticado (API Key ou JWT, qualquer papel); rotas de escrita (`POST`/`PATCH`/`DELETE`) exigem `is_admin` — verdadeiro sempre para API Key, e para JWT apenas quando o papel é `admin`.
- `JWT_SECRET_KEY` tem um valor default inseguro para dev (`dev-insecure-change-me`) — **deve** ser sobrescrito em qualquer ambiente real; documentado no `.env.example` e aqui, não enforced em código (seria preciso falhar o boot em produção se não sobrescrito — fora de escopo desta ADR, mas é o próximo passo de hardening óbvio antes de um deploy real).
- Sem refresh token, sem revogação ativa de sessão, sem MFA — aceitos nesta versão; se a base de usuários crescer ou sessões precisarem ser revogadas antes da expiração, é o gatilho para reconsiderar.
- Sem permissão por projeto — todo `admin` vê e altera todos os projetos, todo `viewer` lê todos os projetos. Revisitar se surgir necessidade real de isolamento entre times/clientes na mesma instância.
