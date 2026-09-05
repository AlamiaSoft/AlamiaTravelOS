# ADR-001: Named Volumes for Production Compose

## Status
**Accepted**

## Context
When deploying `docker-compose.prod.yml` on a VPS via Portainer, the original configuration used bind mounts with relative host paths:
```yaml
- ./config/odoo.conf:/etc/odoo/odoo.conf:ro
- ./custom_addons:/mnt/extra-addons:ro
- ./third_party_addons:/mnt/third-party-addons:ro
```
This caused the error on VPS deployment:
```
failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/data/compose/67/config/odoo.conf" to rootfs at "/etc/odoo/odoo.conf": mount src=/data/compose/67/config/odoo.conf, dst=/etc/odoo/odoo.conf, dstFd=/proc/thread-self/fd/14, flags=MS_BIND|MS_REC: not a directory: Are you trying to mount a directory onto a file (or vice-versa)?
```

The host path `/data/compose/67/config/odoo.conf` didn't exist as a directory on the VPS, causing the mount to fail.

## Considered Options

### Option A: Keep Bind Mounts + Create Host Directories
- Manually create `/data/compose/67/config/` etc. on VPS via SSH
- Pros: Minimal compose changes; existing pattern preserved
- Cons: Requires host-specific setup; not portable across different VPS setups; violates "deploy anywhere" principle; human error risk

### Option B: Switch to Named Volumes
- Replace bind mounts with named volumes in compose file
- Add volume definitions at bottom of file
- Pros: Docker/Portainer manages volume creation automatically; portable across any host; eliminates mount type mismatch errors; standard Docker pattern for production
- Cons: Slightly larger compose file; volume data persists unless explicitly removed; doesn't map to host paths directly (intentional for portability)

### Option C: Use Absolute Host Paths + Pre-create Directories
- Change to `/etc/odoo/odoo.conf:/etc/odoo/odoo.conf:ro` (expect path to already exist on VPS)
- Pros: Simple compose change; no named volume syntax
- Cons: Still requires host-side directory existence; different from local dev pattern (`./config/`); ops burden to ensure paths exist on every VPS

## Decision
**Adopt Option B: Named Volumes**

Rationale:
1. **Portability** — Volumes are managed by Docker/Portainer; the same compose file works on any host (local, Hetzner, Oracle Cloud, etc.)
2. **Eliminates the Error** — No more "not a directory" mount errors since Docker handles volume creation
3. **Production Best Practice** — Named volumes are the recommended pattern for stateful data in Docker Compose production setups
4. **Consistency with Recent Fix** — The `docker-compose.prod.yml` was already updated in this session; formalizing as ADR locks in the pattern
5. **Future-Proof** — New team members don't need to understand host path requirements; just `docker compose up` works

## Consequences
### Positive
- `docker compose up` works out-of-the-box on any host with Docker/Portainer
- No more manual host directory creation required
- Eliminates the specific VPS deployment error experienced
- Aligns with Docker Inc. recommended production pattern

### Trade-offs
- Volumes are Docker-managed, not host-path visible (requires `docker volume ls`/`inspect` to view)
- Data in volumes persists across redeploys unless explicitly removed with `docker volume rm`
- Local dev still uses relative bind mounts (`docker-compose.yml`), so there is a slight divergence; however, the patterns are intentionally similar (both use volume mounting, just different syntax)

## Related Files
- Modified: `docker-compose.prod.yml` (lines 22-24, 66-80)
- Related: `docker-compose.yml` (dev still uses bind mounts for local convenience)
- References: `scripts/backup.sh` (backups volume data, not host paths)