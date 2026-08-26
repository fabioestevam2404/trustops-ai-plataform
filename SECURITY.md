# Política de Segurança

## Reportando vulnerabilidades

Este é um projeto em fase inicial (Sprint 0). Se você identificar uma vulnerabilidade, abra uma issue privada (Security Advisory) no repositório GitHub em vez de uma issue pública.

## Segredos

Nunca commitar arquivos `.env` reais, chaves de API ou credenciais. Use `.env.example` como referência e mantenha segredos reais fora do controle de versão. O CI executa varredura de secrets (Gitleaks) a partir da Sprint 3.

## Escopo de segurança automatizada

A própria plataforma aplica a si mesma (dogfooding) os controles descritos no [Trust Framework](docs/trust-framework/README.md) — SAST, SCA, detecção de secrets e análise de dependências — conforme as integrações forem implementadas (Sprint 2/3).
