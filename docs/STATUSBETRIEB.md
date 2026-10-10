# Service status operations

Edit `status/service-status.json` in the public repository to change the status shown in the Standard installation. The app checks it at launch and every five minutes.

Allowed modes: `normal`, `limited_service`, `scheduled_maintenance`, `maintenance`, `outage`, `acute_outage`.

Allowed locked features: `source_import`, `playback`, `favorites`, `all`.

- Use `normal` and empty `locked_features` to clear a maintenance banner and remove all feature locks.
- Use `maintenance` or `acute_outage` without an explicit lock list to lock all core features.
- Use `scheduled_maintenance` without an explicit lock list to lock source import.
- Use `outage` without an explicit lock list to lock playback.
- `Stop` remains available so users can stop an active stream.
- If the file is unreachable or invalid, the client does not activate a new lock.

All messages and dates are informational text; use clear local/UTC time labels. Do not place secrets, personal information, credentials, or tokens in this public file.
