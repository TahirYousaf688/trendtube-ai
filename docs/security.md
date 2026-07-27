# Security recommendations

- Enforce JWT-based authentication and OAuth for Google login.
- Implement RBAC for administrators, creators, and reviewers.
- Use encrypted secrets in CI/CD and production clusters.
- Validate all request payloads, sanitize user-generated content, and enable audit logging.
- Apply rate limiting, WAF rules, and network policies for service isolation.
