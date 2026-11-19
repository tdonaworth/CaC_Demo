package fedramp_20x.terraform_ecs_test

import rego.v1

import data.fedramp_20x.terraform_ecs

rc(type, after) := {"address": sprintf("%s.t", [type]), "type": type, "change": {"actions": ["create"], "after": after}}

good_container := {"name": "app", "user": "10001", "readonlyRootFilesystem": true, "privileged": false, "environment": [{"name": "APP_ENVIRONMENT", "value": "production"}]}

good_plan := {"resource_changes": [
	rc("aws_db_instance", {"storage_encrypted": true, "publicly_accessible": false}),
	rc("aws_lb_listener", {"protocol": "HTTP", "default_action": [{"type": "redirect"}]}),
	rc("aws_vpc_security_group_ingress_rule", {"cidr_ipv4": "0.0.0.0/0", "to_port": 443}),
	rc("aws_ecs_service", {"network_configuration": [{"assign_public_ip": false}]}),
	rc("aws_cloudwatch_log_group", {"kms_key_id": "arn:k", "retention_in_days": 365}),
	rc("aws_ecr_repository", {"image_tag_mutability": "IMMUTABLE", "image_scanning_configuration": [{"scan_on_push": true}]}),
	rc("aws_ecs_task_definition", {"container_definitions": json.marshal([good_container])}),
]}

with_change(type, after) := {"resource_changes": [rc(type, after)]}

test_good_plan_allowed if terraform_ecs.allow with input as good_plan

test_unencrypted_rds_denied if {
	some m in terraform_ecs.deny with input as with_change("aws_db_instance", {"storage_encrypted": false, "publicly_accessible": false})
	contains(m, "KSI-SVC-SIN")
}

test_public_rds_denied if {
	some m in terraform_ecs.deny with input as with_change("aws_db_instance", {"storage_encrypted": true, "publicly_accessible": true})
	contains(m, "KSI-CNA-ULN")
}

test_http_forward_denied if {
	count(terraform_ecs.deny) == 1 with input as with_change("aws_lb_listener", {"protocol": "HTTP", "default_action": [{"type": "forward"}]})
}

test_open_ssh_denied if {
	count(terraform_ecs.deny) == 1 with input as with_change("aws_vpc_security_group_ingress_rule", {"cidr_ipv4": "0.0.0.0/0", "to_port": 22})
}

test_public_ip_denied if {
	count(terraform_ecs.deny) == 1 with input as with_change("aws_ecs_service", {"network_configuration": [{"assign_public_ip": true}]})
}

test_unencrypted_short_retention_log_group_denied if {
	count(terraform_ecs.deny) == 2 with input as with_change("aws_cloudwatch_log_group", {"retention_in_days": 7})
}

test_ecr_mutable_unscanned_denied if {
	count(terraform_ecs.deny) == 2 with input as with_change("aws_ecr_repository", {"image_tag_mutability": "MUTABLE", "image_scanning_configuration": [{"scan_on_push": false}]})
}

test_bad_container_denied if {
	bad := {"name": "app", "privileged": true, "environment": [{"name": "DB_PASSWORD", "value": "x"}]}
	count(terraform_ecs.deny) == 4 with input as with_change("aws_ecs_task_definition", {"container_definitions": json.marshal([bad])})
}

test_deleted_resources_ignored if {
	plan := {"resource_changes": [{"address": "a", "type": "aws_db_instance", "change": {"actions": ["delete"], "after": null}}]}
	terraform_ecs.allow with input as plan
}
