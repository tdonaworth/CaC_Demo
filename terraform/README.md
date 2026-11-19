# Terraform (mock AWS/ECS deployment)

**Mock infrastructure** — written to be realistic enough for the policies in
`policy/` to evaluate, never intended to be applied as-is (no remote state,
no ALB-log bucket policy, no DNS, no alarms).

Topology: ALB (HTTPS only, WAF) → ECS Fargate tasks in private subnets →
RDS Postgres (Multi-AZ, KMS-encrypted). Secrets via Secrets Manager, logs
to KMS-encrypted CloudWatch groups, images in an immutable scan-on-push ECR repo.

## Check it

```sh
terraform init -backend=false
terraform validate
terraform plan -var image_uri=x -var acm_certificate_arn=arn:aws:acm:us-gov-west-1:111111111111:certificate/x -out plan.bin
terraform show -json plan.bin > plan.json
opa eval -d policy/ -i plan.json 'data.fedramp_20x.terraform.deny'
```

(`plan` needs AWS credentials for data sources; for a no-credentials check,
use `terraform validate` only, or feed `policy/` a hand-written plan JSON as
the unit tests do.)
