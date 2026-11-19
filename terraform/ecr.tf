resource "aws_ecr_repository" "app" {
  name                 = "cac-demo"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true # KSI-SCR-MON / KSI-CMT-VTD
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.main.arn
  }
}
