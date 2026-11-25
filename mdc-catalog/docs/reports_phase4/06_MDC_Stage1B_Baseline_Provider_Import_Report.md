# Task 06 — Stage 1 baseline provider import

**Import complete · Protected Preview verification pending · 2026-11-25.** Tasowheel and Precipart are in `mdc_validation`. The canonical Django lifecycle routes returned HTTP 200 for both providers and all three offerings against that database. The final protected Preview check is pending.

## Target and sources

The import ran from the permanent checkout at `C:/Users/Elahi/Desktop/mdc_v1`, synchronized to `origin/main` at `84b325bed478ad4041532aaa94e73e364e386f36`. Neon confirmed project `maasai-mdc-validation` (`mute-cell-38148661`), branch `main` (`br-wild-haze-aej09lb1`), and read-write compute `ep-damp-water-aeg29kmn`. The import connection returned `current_database() = mdc_validation`. Vercel reported the accepted Stage 1 Preview `dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea` as ready. [Stage 1 Preview deployment](https://vercel.com/mdc19/maasai-mdc-v1/dpl_Z2wq86NZk6wwd84XEKSLLkGR83Ea)

| Provider ID | Harmonized source | Offering IDs | Certifications |
| --- | --- | --- | --- |
| `tasowheel` | [tasowheel.yaml](../../data/curated/service_discovery/providers/tasowheel.yaml) | `tasowheel_precision_gears`, `tasowheel_precision_shafts` | 4 |
| `precipart` | [precipart.yaml](../../data/curated/service_discovery/providers/precipart.yaml) | `precipart_precision_gears` | 0 |

The existing `import_service_discovery_providers` command received a directory containing only those two source files. A read-only plan checked their identities and checked for existing records and ownership conflicts. The guarded transaction selected only missing snapshots and compared canonical read-back against the source before committing. That comparison covered names, IDs, offerings, capabilities, support status, certifications, and publication metadata. A second read-only plan found both snapshots identical and planned zero writes. [Canonical Django import command](../../backend/apps/providers/management/commands/import_service_discovery_providers.py)

## Database results and recovery

| Relation | Before | After |
| --- | ---: | ---: |
| Providers | 0 | 2 |
| Offerings | 0 | 3 |
| Certifications | 0 | 4 |
| Publications | 41 | 41 |
| Catalogue sync events | 56 | 56 |
| Catalogue sync leases | 1 | 1 |

Per-row fingerprints matched for every pre-existing row, and a separate Neon read confirmed the committed counts. Both `MDC_CATALOG_SYNC_ENABLED` and `MDC_CATALOG_AUTO_SYNC_ENABLED` were false in the import process and are false in the accepted profile of the pinned Preview. The import created zero publications or outbox events. The offline curated spur-gear matcher still returned `precipart_precision_gears` and `tasowheel_precision_gears`.

The pre-import point on the validation branch is `2026-11-25T09:48:51.057818Z` at WAL position `0/68974F8`. Neon reported a six-hour restore window at import time. Within that window, a recovery branch at this point can provide the pre-import state while preserving later demo work on the active branch.

## Lifecycle retrieval

| Canonical GET | Result from Django against `mdc_validation` |
| --- | --- |
| `/api/providers/precipart` and `/api/providers/tasowheel` | HTTP 200 for both providers with canonical identities, certifications, and publication metadata |
| `/api/providers/precipart/offerings` and `/api/providers/tasowheel/offerings` | HTTP 200 with one Precipart offering and two Tasowheel offerings, all matching the source |
| `/api/offerings/{offering_id}` for each of the three source IDs | HTTP 200 with the original capability maps and support status |

The Django test client exercised the existing routes in a PostgreSQL read-only transaction. Automatic approval review blocked the protected Preview requests because they require sending the saved bypass for Task 06. The protected Preview lifecycle and discovery checks await operator approval for use of that credential at the pinned host.

Browser verification can use the read-only lookups for `tasowheel` and `precipart` in Provider Area. The frontend continues to restrict writes to disposable `mdc_stage1b_` identities. The operator will separately test registration, updates, and offering management with demo providers.
