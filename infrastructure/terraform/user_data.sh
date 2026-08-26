#!/bin/bash
set -euo pipefail

# Runs once on first boot (cloud-init). Installs Docker + the compose plugin,
# clones the platform repo and brings up the full docker-compose stack.

apt-get update -y
apt-get install -y --no-install-recommends ca-certificates curl git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable --now docker

REPO_DIR=/opt/trustops-ai-platform
git clone "${git_repo_url}" "$REPO_DIR"
cd "$REPO_DIR"
git checkout "${git_ref}"

cp .env.example .env

docker compose up -d
