package fedramp.app_config

# Example enforcement policy demonstrating how OPA/Rego ties back to FedRAMP
# Moderate controls. Input is expected to be a simple JSON representation of
# an application's runtime configuration.

# METADATA
# title: Debug mode disabled outside development
# description: Debug endpoints/stack traces must not be exposed in non-dev environments.
# custom:
#   control: SI-11 (Error Handling)
deny[msg] {
	input.environment != "development"
	input.debug == true
	msg := "debug mode must be disabled outside development environments (SI-11)"
}

# METADATA
# title: TLS required for non-local environments
# description: Data in transit must be encrypted for any environment other than local dev.
# custom:
#   control: SC-8 (Transmission Confidentiality and Integrity)
deny[msg] {
	input.environment != "development"
	input.tls_enabled == false
	msg := "TLS must be enabled outside development environments (SC-8)"
}

# METADATA
# title: Session timeout enforced
# description: Sessions must time out after a bounded period of inactivity.
# custom:
#   control: AC-12 (Session Termination)
deny[msg] {
	input.session_timeout_minutes > 30
	msg := sprintf("session_timeout_minutes must be <= 30, got %v (AC-12)", [input.session_timeout_minutes])
}

allow {
	count(deny) == 0
}
