package fedramp_rev5.app_config

test_denies_debug_in_production if {
	deny["debug mode must be disabled outside development environments (SI-11)"] with input as {
		"environment": "production",
		"debug": true,
		"tls_enabled": true,
		"session_timeout_minutes": 15,
	}
}

test_allows_debug_in_development if {
	count(deny) == 0 with input as {
		"environment": "development",
		"debug": true,
		"tls_enabled": false,
		"session_timeout_minutes": 15,
	}
}

test_denies_missing_tls_in_production if {
	deny["TLS must be enabled outside development environments (SC-8)"] with input as {
		"environment": "production",
		"debug": false,
		"tls_enabled": false,
		"session_timeout_minutes": 15,
	}
}

test_denies_long_session_timeout if {
	count(deny) == 1 with input as {
		"environment": "production",
		"debug": false,
		"tls_enabled": true,
		"session_timeout_minutes": 60,
	}
}

test_allow_when_compliant if {
	allow with input as {
		"environment": "production",
		"debug": false,
		"tls_enabled": true,
		"session_timeout_minutes": 15,
	}
}
