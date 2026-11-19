resource "aws_secretsmanager_secret" "database_url" {
  name       = "cac-demo/database-url"
  kms_key_id = aws_kms_key.main.arn
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql+psycopg://${aws_db_instance.main.username}:${random_password.db.result}@${aws_db_instance.main.address}:5432/${aws_db_instance.main.db_name}"
}

# Container for API keys; values are populated out-of-band (never in Terraform state).
resource "aws_secretsmanager_secret" "api_keys" {
  name       = "cac-demo/api-keys"
  kms_key_id = aws_kms_key.main.arn
}
