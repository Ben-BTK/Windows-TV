# FlemmauTV – Cloudflare Registration API

This is the Cloudflare Workers + D1 implementation of the registration/activation workflow. The existing FastAPI service remains in the repository as the local development/reference service; it is not automatically deployed by this Worker.

## Endpoints

- `GET /health`
- `POST /api/registration-requests`
- `GET /api/registration-requests/{request_id}` — returns status only, never contact/device information
- `GET /admin/api/registration-requests?status=pending|approved|rejected|all`
- `POST /admin/api/registration-requests/{request_id}/approve?lifetime_days=7` — returns a one-time code once
- `POST /admin/api/registration-requests/{request_id}/reject`
- `POST /api/activation/redeem`
- `GET /api/activation/{grant_id}`
- `POST /admin/api/activation/{grant_id}/revoke`

Admin endpoints require `Authorization: Bearer <ADMIN_TOKEN>`. Set the token as a Worker secret; do not commit it to Git. Use a long random value (at least 32 random bytes). This API currently exposes operator endpoints for API clients, not a graphical admin dashboard.

## Setup

Prerequisites: Node.js/npm and Wrangler CLI, plus a Cloudflare account with permission to create Workers and D1 databases.

1. From this directory, install Wrangler locally or use `npx wrangler`.
2. Create the D1 database:
   ```sh
   npx wrangler d1 create flemmau-tv-service
   ```
3. Copy the returned database ID into `wrangler.toml`, replacing `REPLACE_WITH_CREATED_D1_DATABASE_ID`.
4. Apply the migration locally, then remotely:
   ```sh
   npx wrangler d1 migrations apply flemmau-tv-service --local
   npx wrangler d1 migrations apply flemmau-tv-service --remote
   ```
5. Configure the admin secret:
   ```sh
   npx wrangler secret put ADMIN_TOKEN
   ```
   Paste a unique long random token when prompted. Never paste it into chat or commit it.
6. Test locally:
   ```sh
   npx wrangler dev
   ```
   Check `http://localhost:8787/health`.
7. Deploy only when the migration, endpoint tests, secret and account settings have been checked:
   ```sh
   npx wrangler deploy
   ```

## Security and release gates

- This is an initial implementation, not yet production-certified.
- Configure Cloudflare rate limiting/WAF rules for registration and code-redemption routes before public use. Worker memory is not a reliable shared rate limiter.
- Keep admin credentials out of the Windows client. Only the operator interface/tool may use the admin token.
- A grant ID is currently an opaque lookup identifier, not a cryptographic client credential. Before production, add a client-held secret or signed activation token so another person cannot activate by guessing/leaking a grant ID.
- Configure data retention/deletion, privacy notice and operator contact details before accepting real registrations.
- Do not enable permissive browser CORS; the Windows client does not need it.
- No public homepage is required for this API.
- Paid streaming providers remain research-only and are not added by this Worker to the provider catalog.
