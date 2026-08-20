# Security Risk Assessment

## 1. Overview
This document assesses the current security posture of the APPS workspace. It identifies risks in authentication, authorization, data handling, API exposure, and application design based on the existing source code.

## 2. Scope
The assessment covers:
- Backend code: `main.py`, `api/*.py`, `services/*.py`, `database/db.py`
- Frontend code: `static/app.js`, `templates/*.html`
- Data and persistence: `database/schema.sql`, `data/*.json`
- Dependencies: `requirements.txt`

## 3. Summary Findings
| Risk Domain | Finding | Severity |
|---|---|---|
| Authentication/Authorization | Login page exists but is not enforced; protected views and APIs are publicly accessible. | High |
| CSRF / State-change protection | No CSRF tokens or request validation on POST actions (`/api/v1/ingest`, `/api/v1/score`, `/api/v1/deploy/{score_id}`). | High |
| Sensitive data handling | Login form sends credentials via GET and does not authenticate users. | High |
| API exposure | All API routes are accessible without authentication or rate limiting. | High |
| Input validation | No user input validation or sanitization logic was found. | Medium |
| Dependency management | Dependencies are unpinned, so reproducibility and known-vulnerability tracking are limited. | Medium |
| Data encryption / storage | SQLite file is stored unencrypted in project root; no data-at-rest protection. | Medium |
| Secure headers / web hardening | No CSP, no secure HTTP headers, and no security headers configured. | Medium |
| Error/exception handling | No error handling for API failures or malformed requests. | Low |

## 4. Detailed Findings

### 4.1 Authentication and Access Control
- `templates/login.html` provides a login form, but `main.py` does not validate credentials or protect any routes.
- `/dashboard`, `/vulnerabilities`, `/devices`, `/patches`, `/priorities`, and `/api/v1/*` endpoints are accessible without authentication.
- The login form uses `method="get"`, meaning credentials would be sent in the URL query string if it were functional.
- This design creates a false sense of security.

### 4.2 API and Endpoint Security
- `/api/v1/ingest`, `/api/v1/score`, and `/api/v1/deploy/{score_id}` perform state-changing operations with no authorization or CSRF protection.
- The deploy endpoint uses parameterized SQL, which is good, but the endpoint itself is publicly callable.
- No rate limiting or request throttling is implemented.

### 4.3 Input Validation and Output Encoding
- No explicit validation or sanitization is applied to any incoming data.
- The application currently ingests local JSON files only, but if any user-controllable data source is introduced later, there is no protection.
- Jinja2 templates tend to autoescape user-rendered values, which mitigates some XSS risk, but no explicit content security policy or sanitization rules are defined.

### 4.4 Database and Persistence
- `database/db.py` creates and uses `apps.db` in the workspace root without encryption.
- `services/ingestion_service.py` clears and reloads data from local JSON files. This is acceptable for mock ingestion, but it means `apps.db` contents can be modified or deleted if file system access is compromised.
- Some SQL statements are built using constants only, and parameterized queries are used for ingest and deploy operations.

### 4.5 Frontend Behavior
- `static/app.js` issues POST requests to state-changing endpoints with no CSRF token.
- The login form is not protected and could leak credentials into browser history if it were functional.
- No secure cookie or session handling exists because there is no session architecture.

### 4.6 Dependencies
- `requirements.txt` lists packages without pinned versions:
  - `fastapi`
  - `uvicorn`
  - `jinja2`
  - `python-multipart`
- This makes it difficult to track known CVEs and replicate a secure environment.

## 5. Risk Assessment
### High Priority Issues
- Missing authentication and authorization for all application routes.
- State-changing API endpoints can be triggered by any client.
- Login page design is insecure and non-functional.

### Medium Priority Issues
- No CSRF protection for POST actions.
- No secure headers or web hardening implemented.
- Unpinned dependencies limit vulnerability management.
- Database stored unencrypted.

### Low Priority Issues
- Lack of explicit error handling.
- No audit logging or monitoring.

## 6. Recommendations
1. Implement real authentication and authorization.
   - Add username/password validation, session tokens, or OAuth/JWT.
   - Protect dashboard and API routes behind an auth layer.
2. Enforce CSRF protection on all state-changing endpoints.
   - Use same-site cookies or CSRF tokens.
3. Do not use GET for credential submission.
   - Change login form to POST and validate server-side.
4. Add input validation and sanitization.
   - Validate any future user-submitted data and reject malformed values.
5. Harden the HTTP layer.
   - Add secure headers like `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`, and `X-Content-Type-Options`.
6. Pin and scan dependencies.
   - Use a `requirements.txt` with version constraints and run dependency vulnerability scans.
7. Protect data-at-rest.
   - Consider database encryption or storing sensitive data outside the repository.
8. Add logging and audit trails.
   - Record ingestion, scoring, deployment actions, and authentication attempts.

## 7. Recommended Security Controls
- Authentication: OAuth2 / JWT or session-based login.
- Authorization: role-based access control if multiple user types exist.
- CSRF: tokens or same-site cookies.
- Content security: CSP and secure headers.
- Error handling: consistent API error responses and no detailed stack traces in production.
- Dependency management: `pip-tools`, `pip freeze`, or `poetry.lock`.

## 8. Conclusion
The current workspace implements the functional core of the APPS system, but from a security perspective it is not production-ready. The highest risks are missing authentication/authorization, lack of CSRF protection, and exposed API endpoints. Addressing these will greatly improve the security posture.

## Recent Changes (Aug 2026)

- Approval audit trail: Deployments now require an approval action (`approver`, `timestamp`) stored in `Deployment_Actions`. This provides basic traceability for deployment decisions.
- Reduced accidental-deploy risk: The new approval step reduces accidental or automated deployments but does not replace authentication/authorization.
- Remaining risks: API endpoints remain unauthenticated and lack CSRF protection; add auth, CSRF tokens, secure headers, and input validation for production readiness.
