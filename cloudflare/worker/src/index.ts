export interface Env {
  DB: D1Database;
  ADMIN_TOKEN: string;
}

type RegistrationInput = {
  display_name: string;
  contact?: string;
  reason?: string;
  device_id: string;
  app_version?: string;
  app_variant?: string;
};

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

const nowIso = () => new Date().toISOString();
const randomHex = (bytes: number) => {
  const data = new Uint8Array(bytes);
  crypto.getRandomValues(data);
  return Array.from(data, (b) => b.toString(16).padStart(2, "0")).join("");
};
const randomToken = (bytes: number) => {
  const data = new Uint8Array(bytes);
  crypto.getRandomValues(data);
  let binary = "";
  for (const b of data) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
};
const sha256 = async (value: string) => {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
};
const isObject = (v: unknown): v is Record<string, unknown> =>
  typeof v === "object" && v !== null && !Array.isArray(v);
const str = (v: unknown) => typeof v === "string" ? v.trim() : "";
const bounded = (v: unknown, max: number) => str(v).slice(0, max);
const validId = (v: string) => /^[A-Z0-9-]{8,80}$/.test(v);

function requireAdmin(request: Request, env: Env): boolean {
  const auth = request.headers.get("authorization") || "";
  const expected = "Bearer " + env.ADMIN_TOKEN;
  if (!env.ADMIN_TOKEN || auth.length !== expected.length) return false;
  // Constant-time-ish comparison for equal-length values.
  let diff = 0;
  for (let i = 0; i < auth.length; i++) diff |= auth.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

async function bodyJson(request: Request): Promise<unknown> {
  const length = Number(request.headers.get("content-length") || "0");
  if (length > 12000) throw new Error("body_too_large");
  return await request.json();
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method.toUpperCase();

    if (method === "GET" && path === "/health") return json({ ok: true, service: "FlemmauTV registration API" });

    if (method === "POST" && path === "/api/registration-requests") {
      let raw: unknown;
      try { raw = await bodyJson(request); } catch { return json({ error: "invalid_json" }, 400); }
      if (!isObject(raw)) return json({ error: "invalid_request" }, 400);
      const displayName = bounded(raw.display_name, 80);
      const contact = bounded(raw.contact, 254);
      const reason = bounded(raw.reason, 1000);
      const deviceId = bounded(raw.device_id, 80);
      const appVersion = bounded(raw.app_version, 40);
      const appVariant = bounded(raw.app_variant, 20);
      if (!displayName || str(raw.display_name).length > 80 || deviceId.length < 16 ||
          !["", "basis", "standard"].includes(appVariant) ||
          (typeof raw.contact === "string" && raw.contact.length > 254) ||
          (typeof raw.reason === "string" && raw.reason.length > 1000)) {
        return json({ error: "validation_failed" }, 422);
      }
      const requestId = "FTR-" + randomHex(6).toUpperCase();
      const createdAt = nowIso();
      try {
        await env.DB.prepare(`INSERT INTO registration_requests
          (id, display_name, contact, reason, device_id, app_version, app_variant, status, created_at, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)`)
          .bind(requestId, displayName, contact, reason, deviceId, appVersion, appVariant, createdAt, createdAt).run();
      } catch {
        return json({ error: "storage_unavailable" }, 503);
      }
      return json({ accepted: true, request_id: requestId, status: "pending",
        message: "Anfrage gespeichert; eine Freigabe ist damit noch nicht erteilt.", created_at: createdAt }, 201);
    }

    const publicStatus = path.match(/^\/api\/registration-requests\/([^/]+)$/);
    if (method === "GET" && publicStatus) {
      const id = decodeURIComponent(publicStatus[1]);
      const row = await env.DB.prepare("SELECT id, status, created_at, updated_at FROM registration_requests WHERE id = ?")
        .bind(id).first();
      return row ? json(row) : json({ error: "not_found" }, 404);
    }

    if (path.startsWith("/admin/")) {
      if (!requireAdmin(request, env)) return json({ error: "unauthorized" }, 401);
      if (method === "GET" && path === "/admin/api/registration-requests") {
        const status = url.searchParams.get("status") || "pending";
        if (!["pending", "approved", "rejected", "all"].includes(status)) return json({ error: "invalid_filter" }, 400);
        const result = status === "all"
          ? await env.DB.prepare("SELECT id, display_name, contact, reason, device_id, app_version, app_variant, status, created_at, updated_at FROM registration_requests ORDER BY created_at DESC LIMIT 200").all()
          : await env.DB.prepare("SELECT id, display_name, contact, reason, device_id, app_version, app_variant, status, created_at, updated_at FROM registration_requests WHERE status = ? ORDER BY created_at DESC LIMIT 200").bind(status).all();
        return json({ items: result.results, count: result.results.length });
      }

      const approve = path.match(/^\/admin\/api\/registration-requests\/([^/]+)\/approve$/);
      if (method === "POST" && approve) {
        const id = decodeURIComponent(approve[1]);
        const days = Number(url.searchParams.get("lifetime_days") || "7");
        if (!Number.isInteger(days) || days < 1 || days > 30) return json({ error: "invalid_lifetime" }, 400);
        const row = await env.DB.prepare("SELECT id, status FROM registration_requests WHERE id = ?").bind(id).first<{id:string;status:string}>();
        if (!row) return json({ error: "not_found" }, 404);
        if (row.status !== "pending") return json({ error: "request_not_pending" }, 409);
        const code = randomToken(24);
        const created = new Date();
        const expires = new Date(created.getTime() + days * 86400000);
        const hash = await sha256(code);
        const update = await env.DB.prepare("UPDATE registration_requests SET status='approved', updated_at=? WHERE id=? AND status='pending'")
          .bind(created.toISOString(), id).run();
        if (!update.meta.changes) return json({ error: "request_not_pending" }, 409);
        await env.DB.prepare("INSERT INTO activation_codes (code_hash, request_id, expires_at, redeemed_at, revoked_at, created_at) VALUES (?, ?, ?, '', '', ?)")
          .bind(hash, id, expires.toISOString(), created.toISOString()).run();
        return json({ approved: true, request_id: id, activation_code: code, expires_at: expires.toISOString(),
          note: "Code jetzt sicher übermitteln; er wird nicht erneut im Klartext angezeigt." });
      }

      const reject = path.match(/^\/admin\/api\/registration-requests\/([^/]+)\/reject$/);
      if (method === "POST" && reject) {
        const id = decodeURIComponent(reject[1]);
        const result = await env.DB.prepare("UPDATE registration_requests SET status='rejected', updated_at=? WHERE id=? AND status='pending'")
          .bind(nowIso(), id).run();
        if (!result.meta.changes) {
          const row = await env.DB.prepare("SELECT id FROM registration_requests WHERE id=?").bind(id).first();
          return row ? json({ error: "request_not_pending" }, 409) : json({ error: "not_found" }, 404);
        }
        return json({ rejected: true, request_id: id });
      }

      const revoke = path.match(/^\/admin\/api\/activation\/([^/]+)\/revoke$/);
      if (method === "POST" && revoke) {
        const grantId = decodeURIComponent(revoke[1]);
        const result = await env.DB.prepare("UPDATE device_grants SET revoked_at=? WHERE id=? AND revoked_at=''")
          .bind(nowIso(), grantId).run();
        return result.meta.changes ? json({ revoked: true, grant_id: grantId }) : json({ error: "grant_not_found_or_revoked" }, 404);
      }
      return json({ error: "not_found" }, 404);
    }

    if (method === "POST" && path === "/api/activation/redeem") {
      let raw: unknown;
      try { raw = await bodyJson(request); } catch { return json({ error: "invalid_json" }, 400); }
      if (!isObject(raw)) return json({ error: "invalid_request" }, 400);
      const code = str(raw.code);
      const deviceId = str(raw.device_id);
      if (code.length < 12 || code.length > 100 || deviceId.length < 16 || deviceId.length > 80) return json({ error: "validation_failed" }, 422);
      const codeHash = await sha256(code);
      const entry = await env.DB.prepare(`SELECT c.code_hash, c.request_id, c.expires_at, c.redeemed_at, c.revoked_at,
        r.status, r.device_id FROM activation_codes c JOIN registration_requests r ON r.id=c.request_id
        WHERE c.code_hash=?`).bind(codeHash).first<any>();
      if (!entry || entry.redeemed_at || entry.revoked_at) return json({ error: "invalid_or_used_code" }, 400);
      if (Date.parse(entry.expires_at) <= Date.now()) return json({ error: "code_expired" }, 400);
      if (entry.status !== "approved" || entry.device_id !== deviceId) return json({ error: "device_mismatch" }, 400);
      const grantId = "FTG-" + randomHex(16);
      const created = new Date();
      const expires = new Date(created.getTime() + 30 * 86400000);
      // Conditional update prevents successful reuse if two requests race.
      const used = await env.DB.prepare("UPDATE activation_codes SET redeemed_at=? WHERE code_hash=? AND redeemed_at='' AND revoked_at='' AND expires_at>?")
        .bind(created.toISOString(), codeHash, created.toISOString()).run();
      if (!used.meta.changes) return json({ error: "invalid_or_used_code" }, 400);
      await env.DB.prepare("INSERT INTO device_grants (id, request_id, device_id, expires_at, revoked_at, created_at) VALUES (?, ?, ?, ?, '', ?)")
        .bind(grantId, entry.request_id, deviceId, expires.toISOString(), created.toISOString()).run();
      return json({ activated: true, grant_id: grantId, expires_at: expires.toISOString(), message: "Testgerät freigeschaltet." });
    }

    const grant = path.match(/^\/api\/activation\/([^/]+)$/);
    if (method === "GET" && grant) {
      const id = decodeURIComponent(grant[1]);
      const row = await env.DB.prepare("SELECT id, expires_at, revoked_at FROM device_grants WHERE id=?").bind(id).first<any>();
      if (!row) return json({ active: false }, 404);
      const active = !row.revoked_at && Date.parse(row.expires_at) > Date.now();
      return json({ active, expires_at: row.expires_at });
    }

    return json({ error: "not_found" }, 404);
  },
};
