# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in NAKLIYE NET, please report it responsibly:

**DO NOT create public GitHub issues for security vulnerabilities.**

Please email: security@nakliyenet.com or create a private security advisory on GitHub.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Measures

### API Key Management
- All API keys stored in environment variables only
- Never commit `.env` files to version control
- `.env.example` contains placeholder values only
- Regular API key rotation

### Google Maps API Key Security
- Domain restriction: nakliyenet.com only
- HTTP referrer restrictions enabled
- API restrictions: Maps JavaScript API only
- Application restrictions enforced

### GitHub Secret Scanning Alerts

**If you see alerts about leaked API keys in git history:**

⚠️ Keys in git history cannot be removed - they are public forever!

**Immediate Actions:**
1. ✅ Regenerate the leaked key in Google Cloud Console
2. ✅ Add domain restrictions (nakliyenet.com)
3. ✅ Update production `.env` file
4. ✅ Verify old key is disabled
5. ✅ Monitor for unauthorized usage

**Already Completed:**
- Old leaked keys have been regenerated
- New keys restricted to nakliyenet.com domain
- Production environment updated
- Secret scanning enabled on repository

### Authentication & Authorization
- Google OAuth 2.0 for user authentication
- Session cookies: Secure + HttpOnly flags
- CSRF protection enabled
- Password hashing with Django defaults

### Database Security
- PostgreSQL with SSL connections
- Strong password policies
- Regular automated backups
- Restricted network access

### HTTPS/SSL
- Forced HTTPS redirect (SECURE_SSL_REDIRECT=True)
- HSTS enabled (31536000 seconds = 1 year)
- Secure cookie settings
- Modern TLS configuration

## Best Practices

1. ❌ Never commit `.env` files
2. ✅ Use environment variables for all secrets
3. ✅ Enable GitHub secret scanning
4. ✅ Review PRs for accidental secrets
5. ✅ Rotate credentials regularly
6. ✅ Principle of least privilege for API keys

## Contact

Security issues: security@nakliyenet.com
