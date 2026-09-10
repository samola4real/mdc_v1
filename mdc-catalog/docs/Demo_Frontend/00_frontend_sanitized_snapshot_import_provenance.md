# MDC Demo Frontend Sanitized Snapshot Import Provenance

## Purpose and scope

The imported application is a MaaSAI MaaS Dynamic Catalogue demonstration frontend. It illustrates provider registration, provider updates, service discovery, role-oriented navigation, and demo administration before full Marketplace integration. It is not the real Cloud MaaS Marketplace (CMM).

## Source identity

- Historical source repository: `https://gitlab-cigip.alc.upv.es/maasai/tools/template-frontend.git`
- Source branch: `main`
- Source HEAD: `832ad57265bce0889ebea58bc69c031c3b394ee7`
- Preservation date: `2026-09-09`
- Operator-local preservation root: `C:\Users\Elahi\Desktop\mdc_frontend_preservation\2026-09-09`
- GitHub application target: `mdc-catalog/demo-frontend/`
- Imported application files: 134
- Imported historical reports: 30

The source working tree contained four approved tracked modifications and untracked MDC pages, components, services, and reports. The preservation milestone captured those changes and produced a sanitized staging snapshot. This import uses that staging snapshot exclusively.

## History and security boundary

The original GitLab history was intentionally not imported. Tracked GitLab history contains credential-bearing objects, so importing unsquashed history would make those objects reachable from personal GitHub even if current files were later redacted.

The snapshot excludes:

- original `.git` objects and history;
- `.env*` files and credential assignments;
- raw Keycloak realm exports containing credential material;
- editor state;
- dependencies, build output, caches, logs, and generated archives.

No trusted MDC lifecycle service token may be placed in browser source, public runtime configuration, or any client-delivered asset. Trusted lifecycle access requires an appropriate server-side identity boundary.

## Repository roles after approval

After this integration branch is reviewed and merged, personal GitHub `samola4real/mdc_v1` becomes the controlled daily development source for the snapshot. The MaaSAI GitLab frontend repository remains the historical and official release repository.

Future GitLab releases must use a fresh temporary GitLab checkout, a release branch, reviewed file synchronization, secret scanning, validation, explicit approval, and normal GitLab merge review. The normal `mdc_v1` working copy must not retain a GitLab remote. Releases must not use subtree push, unrelated-history merge, history replacement, or force push.
