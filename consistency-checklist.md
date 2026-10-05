# Specification consistency checklist

Antes de implementar:

- [x] User model is represented in domain, persistence and OpenAPI.
- [x] `status` is boolean and documented as active/inactive.
- [x] `DELETE` is logical deactivation, not physical deletion.
- [x] `PUT` does not modify email or status (extra fields → 422).
- [x] Email is unique and case-insensitive (normalized + unique index on `lower(email)`).
- [x] `second_lastname` is optional.
- [x] Name fields have a 30-character maximum.
- [x] GET collection is defined as active users only.
- [x] GET by ID may return inactive users.
- [x] Define pagination contract for GET /users (ADR-0007).
- [x] Define exact allowed characters for names and surnames (`spec/domain/user.md`).
- [x] Decide whether an explicit reactivation endpoint is needed (out of scope for v1).
- [x] Decide HTTP framework and migration tooling (ADR-0004, ADR-0005).
- [x] `DELETE` on an inactive user is idempotent (204).
- [x] OpenAPI version matches syntax used (3.1.0, nullable via `type: 'null'`).
- [x] Health endpoint defined in contract.
- [x] Availability requirement (24×7, SLA 99 %) reflected in requirements, acceptance, feature spec and ADR-0008.
- [x] Health endpoints split into liveness and readiness in the contract.
- [x] Migration policy is expand/contract (zero downtime).
- [ ] Confirm proposed ADRs 0004–0008 (status: Propuesto → Aceptado).
- [ ] Choose deployment platform and managed PostgreSQL provider.
- [ ] Define authentication/authorization strategy before production.
- [ ] Define rate limiting limits.
