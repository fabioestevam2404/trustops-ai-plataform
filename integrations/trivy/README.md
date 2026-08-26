# Integração — Trivy

Executa `trivy fs` (scanners `secret` e `misconfig`) sobre o repositório avaliado e persiste o relatório bruto no Evidence Store (ver [ADR 0003](../../docs/adr/0003-evidence-store-traceability.md)).

**Implementado na Sprint 3.** Binário instalado no `backend/Dockerfile` (não é pacote pip — release Go, versão pinada `v0.74.0`). Código em `backend/app/infrastructure/scanners/trivy_runner.py`.

**Limitação do MVP**: roda **sem o scanner `vuln`** (CVEs de dependências / SCA), que exigiria baixar e manter um banco de vulnerabilidades — dependência de rede em tempo de execução ou imagem Docker maior (decisão registrada em `docs/trust-framework/README.md`). SCA de dependências fica para uma sprint futura.
