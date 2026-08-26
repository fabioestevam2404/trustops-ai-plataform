variable "region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type running the full docker-compose stack."
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Name of an existing EC2 key pair for SSH access. Must already exist in the target AWS account/region."
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to reach port 22. Never leave this as 0.0.0.0/0 outside of a throwaway demo."
  type        = string
}

variable "git_repo_url" {
  description = "Repository the instance clones on boot. Must be reachable (i.e. already pushed) for user_data to succeed."
  type        = string
  default     = "https://github.com/fabioestevam2404/trustops-ai-plataform.git"
}

variable "git_ref" {
  description = "Branch, tag, or commit to check out after cloning."
  type        = string
  default     = "main"
}
