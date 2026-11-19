resource "aws_db_subnet_group" "main" {
  name       = "cac-demo"
  subnet_ids = aws_subnet.private[*].id
}

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_instance" "main" {
  identifier                      = "cac-demo"
  engine                          = "postgres"
  engine_version                  = "16.4"
  instance_class                  = "db.t4g.medium"
  allocated_storage               = 20
  db_name                         = "app"
  username                        = "app"
  password                        = random_password.db.result
  db_subnet_group_name            = aws_db_subnet_group.main.name
  vpc_security_group_ids          = [aws_security_group.db.id]
  publicly_accessible             = false
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.main.arn
  multi_az                        = true
  backup_retention_period         = 14
  deletion_protection             = true
  skip_final_snapshot             = false
  final_snapshot_identifier       = "cac-demo-final"
  auto_minor_version_upgrade      = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.main.arn
}
