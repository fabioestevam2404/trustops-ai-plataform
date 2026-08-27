# ADR 0005 — Instalação de dependências do repositório-alvo

## Status

Aceito

## Contexto

Desde a Sprint 2 (ver limitação documentada em [Trust Framework](../trust-framework/README.md)), o scanner de qualidade roda pytest usando o ambiente Python do próprio backend, sem instalar as dependências do repositório avaliado. Funciona para o dogfooding natural (o próprio `backend/` desta plataforma), mas testando a plataforma contra um projeto real (`corporate-knowledge-assistant`, que usa `pyproject.toml` + `uv.lock` e depende de `structlog`/`sentence-transformers`/`torch`) essa limitação apareceu na prática: `quality_score: 0`, porque o `conftest.py` do alvo falha ao importar `structlog` e o pytest nem coletava os testes.

## Mudança de princípio

Até esta sprint, todo scanner do MVP foi deliberadamente hermético (sem rede): Trivy sem banco de CVE, Semgrep com ruleset local, AI Trust sem LLM-judge — todos documentados como simplificações explícitas do MVP, não omissões acidentais. A instalação de dependências é o **primeiro scanner que precisa de rede de propósito**: baixar pacotes do PyPI é o objetivo, não um efeito colateral a evitar.

Isso também amplia a superfície de execução de código arbitrário: a árvore de dependências transitiva do repositório-alvo passa a ser instalada e importada dentro do container do backend. Esse risco já existia em menor grau desde a Sprint 2 (o próprio pytest do repositório-alvo já é código arbitrário executado); esta mudança o estende à cadeia de dependências completa. **Sem sandboxing adicional nesta versão** (sem gVisor, sem container efêmero por assessment) — registrado aqui como limitação conhecida, não omitido.

## Decisões

1. **Detecção em ordem, com dois gerenciadores suportados**: `uv.lock` existe → `uv sync --all-groups`; senão `requirements.txt`/`requirements-dev.txt` → `uv venv` + `uv pip install -r`; senão `pyproject.toml` sozinho → `uv venv` + `uv pip install .` (só dependências base — extras como `.[dev]` ficam fora de escopo, seria uma segunda camada de heurística frágil); sem nenhum manifesto, comportamento idêntico ao pré-existente (`python_executable=None`). Implementado em `backend/app/infrastructure/scanners/dependency_installer.py`.

2. **`uv` como motor único de instalação, mesmo no fallback pip.** Descoberta durante a implementação: `uv venv` não faz bootstrap de pip via `ensurepip` (criação quase instantânea), e `uv pip install --python <exe>` instala em qualquer venv sem precisar que pip esteja fisicamente presente nele — ao contrário de `<venv_python> -m pip install`. A primeira versão usava `venv.create(with_pip=True)` da stdlib nos caminhos de fallback pip; o `ensurepip` neste ambiente é lento o bastante para levar a suíte de testes de ~4 minutos para 3h16min numa única execução. Reescrito para usar `uv venv` uniformemente nos três caminhos — nenhuma dependência de `venv`/`ensurepip` da stdlib restante.

3. **O venv é criado fora de `repo_path`, não dentro.** Primeira versão criava `.venv` dentro do próprio diretório clonado (conveniente: seria limpo de graça junto com o clone). Bug real encontrado na primeira validação end-to-end contra `corporate-knowledge-assistant`: Bandit e Trivy escaneiam `repo_path` recursivamente, então passaram a varrer também o `.venv` recém-instalado (133 pacotes, incluindo `torch`/`transformers`/`sentence-transformers`) como se fosse código do próprio repositório-alvo — atribuição errada, e grande o suficiente para estourar os timeouts das duas ferramentas (30s e 60s respectivamente). O timeout virava um `Finding` de categoria `execution` (que não bloqueia certificação nem zera o score), então o `security_score` subia de forma espúria por omissão de findings reais, não por segurança de fato melhor — exatamente o tipo de falso senso de segurança que o [ADR 0003](0003-evidence-store-traceability.md) existe para evitar.

   Corrigido movendo a criação do venv para fora de `repo_path`: `uv sync` é redirecionado via a variável de ambiente `UV_PROJECT_ENVIRONMENT`; os caminhos `uv venv` recebem diretamente um diretório temporário externo (`tempfile.mkdtemp`). `AssessmentService.run()` chama `shutil.rmtree(install_result.venv_dir)` explicitamente depois que o pytest termina de usá-lo, antes dos scanners de segurança rodarem — nenhum scanner estático nunca chega a ver o venv instalado. Validado: rerun real contra `corporate-knowledge-assistant` manteve `quality_score: 76`, mas `security_score` voltou ao valor real (65, igual ao obtido antes desta feature existir), sem nenhum finding de `execution`.

4. **Continua síncrono, sem migração para Celery.** Decisão confirmada com o usuário: o timeout de instalação (300s) e o timeout condicional do pytest (300s quando roda por um venv instalado, 90s no caminho original sem instalação) absorvem a demora extra sem precisar de execução assíncrona. Migração para Celery fica para se o timeout maior não for suficiente na prática.

5. **Falha isolada, mesmo padrão do resto do pipeline.** `install()` nunca propaga exceção — timeout ou erro de instalação vira um `Finding` `MEDIUM` de categoria `quality` explicando a causa, e o pytest roda no ambiente do próprio backend como fallback (comportamento idêntico ao pré-Sprint-2-fix). Sem manifesto reconhecido, o finding é `INFO` ("não aplicável").

## Consequências

- Repositórios-alvo com dependências de teste reais deixam de ficar presos em `quality_score: 0` por falha de coleta do pytest — validado end-to-end: `corporate-knowledge-assistant` foi de `quality_score: 0` para `76`.
- A plataforma passa a depender de rede em tempo de execução para este scanner especificamente — inconsistente com o princípio hermético dos demais, registrado aqui como exceção deliberada, não generalizada.
- Superfície de execução de código de terceiros aumenta sem sandboxing adicional — aceito nesta versão, mas deve ser revisitado antes de qualquer uso contra repositórios não confiáveis/públicos sem triagem prévia.
- Cada assessment com manifesto reconhecido agora reinstala dependências do zero (sem cache entre execuções) — mais lento, mas simples e sem gestão de invalidação de cache. Se a latência por assessment se tornar um problema, cache de dependências é o próximo passo natural, não escopo desta ADR.
