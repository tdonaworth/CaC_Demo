variable "region" {
  type    = string
  default = "us-gov-west-1" # FedRAMP workloads typically target GovCloud or a US commercial region
}

variable "environment" {
  type    = string
  default = "production"
}

variable "image_uri" {
  description = "Full ECR image URI incl. tag/digest to deploy."
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM cert for the ALB HTTPS listener."
  type        = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "log_retention_days" {
  type    = number
  default = 365
}
