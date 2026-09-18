package fedramp_20x.app_config

# Example enforcement policy tagged to FedRAMP 20x Key Security Indicators
# (KSIs) instead of Rev5/NIST 800-53 control IDs directly. See
# compliance-20x/README.md for what KSIs are and where these IDs come from.
# Input is the same simplified app-config shape used by fedramp_rev5, plus a
# couple of 20x-relevant fields (mfa_enabled, audit_logging_enabled).

# METADATA
# title: Information encrypted in transit
# description: Data in transit must be encrypted for any environment other than local dev.
# custom:
#   ksi: KSI-SVC-SIN (Securing Information)
deny contains msg if {
	input.environment != "development"
	input.tls_enabled == false
	msg := "TLS must be enabled outside development environments (KSI-SVC-SIN)"
}

# METADATA
# title: Phishing-resistant MFA required
# description: Non-dev environments must require MFA rather than password-only auth.
# custom:
#   ksi: KSI-IAM-APM (Adopting Passwordless Methods)
deny contains msg if {
	input.environment != "development"
	input.mfa_enabled == false
	msg := "MFA must be enabled outside development environments (KSI-IAM-APM)"
}

# METADATA
# title: Session timeout bounds least-privilege access
# description: Sessions must time out after a bounded period of inactivity.
# custom:
#   ksi: KSI-IAM-ELP (Ensuring Least Privilege)
deny contains msg if {
	input.session_timeout_minutes > 30
	msg := sprintf("session_timeout_minutes must be <= 30, got %v (KSI-IAM-ELP)", [input.session_timeout_minutes])
}

# METADATA
# title: Audit logging enabled for review
# description: Security-relevant events must be logged so they can be persistently reviewed.
# custom:
#   ksi: KSI-MLA-RVL (Reviewing Logs)
deny contains msg if {
	input.environment != "development"
	input.audit_logging_enabled == false
	msg := "audit logging must be enabled outside development environments (KSI-MLA-RVL)"
}

allow if {
	count(deny) == 0
}
