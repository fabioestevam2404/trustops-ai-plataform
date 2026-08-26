output "instance_public_ip" {
  description = "Public IP of the TrustOps AI Platform instance."
  value       = aws_instance.trustops.public_ip
}

output "api_url" {
  value = "http://${aws_instance.trustops.public_ip}:8001"
}

output "dashboard_url" {
  value = "http://${aws_instance.trustops.public_ip}:5173"
}

output "grafana_url" {
  value = "http://${aws_instance.trustops.public_ip}:3000"
}
