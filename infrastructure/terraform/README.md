# Terraform

Infraestrutura como código para rodar a plataforma em produção. **Implementado na Sprint 8.**

## Alvo escolhido: AWS EC2 + docker-compose

Uma única instância EC2 roda a stack inteira via `docker compose up -d` (o mesmo `docker-compose.yml` usado em desenvolvimento) — não ECS/Fargate/RDS/ElastiCache gerenciados. Decisão explícita: mais simples, mais próxima do que já existe e já foi validado localmente, evita escrever uma arquitetura gerenciada complexa (VPC, subnets, IAM roles, task definitions) que não pode ser testada contra uma conta real neste ambiente.

```
main.tf        # provider aws, aws_instance (EC2), security group
variables.tf   # region, instance_type, key_name, allowed_ssh_cidr, git_repo_url, git_ref
outputs.tf     # IP público, URLs da API/dashboard/Grafana
user_data.sh   # cloud-init: instala Docker, clona o repo, docker compose up -d
```

## ⚠️ Não aplicado nesta sessão

Não há credenciais de nenhuma conta AWS neste ambiente de desenvolvimento assistido. O que **foi** feito e validado:

```bash
terraform init -backend=false   # baixa o provider AWS do registry público — OK, sem credenciais
terraform validate              # Success! The configuration is valid.
terraform fmt -check            # sem diffs
```

`terraform plan`/`terraform apply` **não foram executados** — exigiriam credenciais AWS reais e criariam recursos reais (cobrança). Para aplicar de verdade:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
terraform init
terraform plan -var="key_name=sua-chave" -var="allowed_ssh_cidr=SEU_IP/32"
terraform apply -var="key_name=sua-chave" -var="allowed_ssh_cidr=SEU_IP/32"
```

**Pré-requisito**: `git_repo_url` (default aponta para o remoto já configurado no repositório local) precisa estar acessível — ou seja, o código precisa ter sido enviado ao GitHub antes. Até aqui, cada sprint deste projeto ficou só local, por decisão do usuário; o push é responsabilidade de quem for aplicar isto de verdade.

## Limitações conhecidas / fora de escopo do MVP

- Sem TLS/reverse proxy — a API, o dashboard e o Grafana ficam expostos diretamente nas portas 8001/5173/3000. Adequado para demo, não para produção de verdade sem um Nginx/ALB + certificado na frente.
- Sem backend remoto de state (S3 + DynamoDB lock) — state fica local. Necessário antes de qualquer uso em equipe.
- Postgres/Redis rodam como containers na mesma instância (não RDS/ElastiCache gerenciados) — sem backup automático, sem alta disponibilidade.
- `allowed_ssh_cidr` não tem default — precisa ser passado explicitamente (não force `0.0.0.0/0` em uso real).
