# Integração — Semgrep

Executa Semgrep (SAST) sobre o repositório avaliado, normaliza os findings (severidade ERROR/WARNING/INFO → HIGH/MEDIUM/LOW) e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 3.** Código em `backend/app/infrastructure/scanners/semgrep_runner.py`.

**Limitação do MVP**: usa um ruleset **local**, bundlado em `backend/app/infrastructure/scanners/semgrep_rules.yml` (hardcoded secrets, `eval`/`exec`, `subprocess(shell=True)`, `yaml.load` inseguro, hash fraco) — não o registro completo de regras do Semgrep (`--config=auto`), que exigiria rede em tempo de execução e quebraria o isolamento dos testes. Expandir o ruleset ou integrar o registro completo fica para uma sprint futura.
