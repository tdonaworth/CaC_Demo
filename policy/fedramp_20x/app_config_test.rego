package fedramp_20x.app_config

test_denies_missing_tls_in_production if {
	deny["TLS must be enabled outside development environments (KSI-SVC-SIN)"] with input as {
		"environment": "production",
		"tls_enabled": false,
		"mfa_enabled": true,
		"session_timeout_minutes": 15,
		"audit_logging_enabled": true,
	}
}

test_denies_missing_mfa_in_production if {
	deny["MFA must be enabled outside development environments (KSI-IAM-APM)"] with input as {
		"environment": "production",
		"tls_enabled": true,
		"mfa_enabled": false,
		"session_timeout_minutes": 15,
		"audit_logging_enabled": true,
	}
}

test_denies_long_session_timeout if {
	deny[_] == sprintf("session_timeout_minutes must be <= 30, got %v (KSI-IAM-ELP)", [60]) with input as {
		"environment": "production",
		"tls_enabled": true,
		"mfa_enabled": true,
		"session_timeout_minutes": 60,
		"audit_logging_enabled": true,
	}
}

test_denies_missing_audit_logging_in_production if {
	deny["audit logging must be enabled outside development environments (KSI-MLA-RVL)"] with input as {
		"environment": "production",
		"tls_enabled": true,
		"mfa_enabled": true,
		"session_timeout_minutes": 15,
		"audit_logging_enabled": false,
	}
}

test_allows_relaxed_settings_in_development if {
	count(deny) == 0 with input as {
		"environment": "development",
		"tls_enabled": false,
		"mfa_enabled": false,
		"session_timeout_minutes": 15,
		"audit_logging_enabled": false,
	}
}

test_allow_when_compliant if {
	allow with input as {
		"environment": "production",
		"tls_enabled": true,
		"mfa_enabled": true,
		"session_timeout_minutes": 15,
		"audit_logging_enabled": true,
	}
}
