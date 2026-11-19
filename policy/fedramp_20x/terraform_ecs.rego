package fedramp_20x.terraform_ecs

# Enforcement over `terraform show -json plan.bin` output for the ECS/RDS
# deployment in terraform/. Input is the plan JSON; we inspect
# resource_changes[*].change.after. IDs are FedRAMP 20x KSIs.

import rego.v1

resources(type) := [rc |
	some rc in input.resource_changes
	rc.type == type
	not "delete" in rc.change.actions
]

# METADATA
# custom:
#   ksi: KSI-SVC-SIN
deny contains msg if {
	some rc in resources("aws_db_instance")
	rc.change.after.storage_encrypted != true
	msg := sprintf("%s: RDS storage must be encrypted (KSI-SVC-SIN)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-CNA-ULN
deny contains msg if {
	some rc in resources("aws_db_instance")
	rc.change.after.publicly_accessible == true
	msg := sprintf("%s: RDS must not be publicly accessible (KSI-CNA-ULN)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-SVC-SIN
deny contains msg if {
	some rc in resources("aws_lb_listener")
	rc.change.after.protocol == "HTTP"
	some action in rc.change.after.default_action
	action.type != "redirect"
	msg := sprintf("%s: HTTP listener must only redirect to HTTPS (KSI-SVC-SIN)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-CNA-RNT
deny contains msg if {
	some rc in resources("aws_vpc_security_group_ingress_rule")
	rc.change.after.cidr_ipv4 == "0.0.0.0/0"
	not rc.change.after.to_port in {80, 443}
	msg := sprintf("%s: world-open ingress only allowed on 80/443 (KSI-CNA-RNT)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-CNA-RNT
deny contains msg if {
	some rc in resources("aws_ecs_service")
	some nc in rc.change.after.network_configuration
	nc.assign_public_ip == true
	msg := sprintf("%s: ECS tasks must not get public IPs (KSI-CNA-RNT)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-MLA-LET
deny contains msg if {
	some rc in resources("aws_cloudwatch_log_group")
	not rc.change.after.kms_key_id
	msg := sprintf("%s: log group must be KMS-encrypted (KSI-MLA-LET)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-MLA-LET
deny contains msg if {
	some rc in resources("aws_cloudwatch_log_group")
	rc.change.after.retention_in_days < 365
	msg := sprintf("%s: log retention must be >= 365 days (KSI-MLA-LET)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-SCR-MON
deny contains msg if {
	some rc in resources("aws_ecr_repository")
	not rc.change.after.image_scanning_configuration[0].scan_on_push
	msg := sprintf("%s: ECR scan_on_push must be enabled (KSI-SCR-MON)", [rc.address])
}

# METADATA
# custom:
#   ksi: KSI-SVC-VRI
deny contains msg if {
	some rc in resources("aws_ecr_repository")
	rc.change.after.image_tag_mutability != "IMMUTABLE"
	msg := sprintf("%s: ECR tags must be immutable (KSI-SVC-VRI)", [rc.address])
}

# Container-level checks on the ECS task definition.
container_defs(rc) := json.unmarshal(rc.change.after.container_definitions)

# METADATA
# custom:
#   ksi: KSI-IAM-ELP
deny contains msg if {
	some rc in resources("aws_ecs_task_definition")
	some c in container_defs(rc)
	not c.user
	msg := sprintf("%s: container %s must set a non-root user (KSI-IAM-ELP)", [rc.address, c.name])
}

# METADATA
# custom:
#   ksi: KSI-IAM-ELP
deny contains msg if {
	some rc in resources("aws_ecs_task_definition")
	some c in container_defs(rc)
	c.privileged == true
	msg := sprintf("%s: container %s must not be privileged (KSI-IAM-ELP)", [rc.address, c.name])
}

# METADATA
# custom:
#   ksi: KSI-SVC-VRI
deny contains msg if {
	some rc in resources("aws_ecs_task_definition")
	some c in container_defs(rc)
	not c.readonlyRootFilesystem
	msg := sprintf("%s: container %s must use a read-only root filesystem (KSI-SVC-VRI)", [rc.address, c.name])
}

# METADATA
# custom:
#   ksi: KSI-SVC-ASM
deny contains msg if {
	some rc in resources("aws_ecs_task_definition")
	some c in container_defs(rc)
	some e in c.environment
	regex.match(`(?i)(password|secret|api_?key|token)`, e.name)
	msg := sprintf("%s: secret-looking env var %s must use `secrets`, not `environment` (KSI-SVC-ASM)", [rc.address, e.name])
}

allow if count(deny) == 0
