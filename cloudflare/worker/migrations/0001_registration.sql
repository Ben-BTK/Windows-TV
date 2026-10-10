CREATE TABLE IF NOT EXISTS registration_requests (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  contact TEXT NOT NULL DEFAULT '',
  reason TEXT NOT NULL DEFAULT '',
  device_id TEXT NOT NULL,
  app_version TEXT NOT NULL DEFAULT '',
  app_variant TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_registration_status_created
  ON registration_requests(status, created_at DESC);

CREATE TABLE IF NOT EXISTS activation_codes (
  code_hash TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES registration_requests(id),
  expires_at TEXT NOT NULL,
  redeemed_at TEXT NOT NULL DEFAULT '',
  revoked_at TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_activation_request ON activation_codes(request_id);

CREATE TABLE IF NOT EXISTS device_grants (
  id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL REFERENCES registration_requests(id),
  device_id TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_grants_request ON device_grants(request_id);
