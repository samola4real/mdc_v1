# M3 provider/offering deletion and attribute-removal report

## Scope and baseline

- Milestone: M3 only.
- Focused branch: `phase4/lifecycle-delete`.
- Baseline and prompt commit: `4a3f7681fc785153c1a7b31b1fc2a52c2356db96` (`origin/main` at implementation start).
- Required M2 merge confirmed in ancestry: `12aa650689a1976c8cfe7a950cd40016cba08d2e`.
- Implementation commit: `334970a92e03ff9f7d51599c860353349304f0f4`.
- Work was performed in the separate clean linked worktree
  `C:\Users\Elahi\Desktop\mdc_v1_m3_worktree`.
- The original checkout remained on `main`; its pre-existing `.gitignore` and
  `mdc-catalog/demo-frontend/src/pages/demo/index.js` changes were not modified,
  staged, stashed, discarded, reset, or copied.
- The demo frontend was not changed. Nothing was merged or deployed, and no
  production, Vercel, Neon, Fuseki, or real-provider data was accessed.

## Final DELETE contract

The existing detail routes now support:

```text
DELETE /api/providers/{provider_id}
DELETE /api/offerings/{offering_id}
```

DELETE is governed by the existing publication enable flag, pilot bearer-auth
option, secure-mode bearer and actor policy, and existing ETag parser. Unlike
optional pilot PATCH concurrency, DELETE always requires the target's current
strong ETag. The client procedure is:

1. GET the provider or offering.
2. Preserve the exact quoted `ETag` response header.
3. Review the current representation.
4. Send DELETE with that value in `If-Match` (or the retained pilot
   `X-MDC-If-Match` compatibility header).

Example:

```http
DELETE /api/offerings/example_provider_precision_gears
Authorization: Bearer <trusted service credential>
X-MDC-Actor-Id: marketplace:user-42
If-Match: "<opaque current revision>"
```

An accepted operational deletion returns `200`, never a body-bearing `204`:

```json
{
  "contract_version": "1.0",
  "status": "accepted",
  "operation": "delete",
  "target": {
    "entity_type": "offering",
    "entity_id": "example_provider_precision_gears"
  },
  "provider_id": "example_provider",
  "publication_id": "<opaque publication UUID>",
  "publication_status": "sync_pending",
  "sync_status": "pending"
}
```

Provider receipts additionally contain the ordered `offering_ids` captured for
the deletion. Error behavior is precise: missing precondition `428`, malformed,
weak, wildcard, or list precondition `400`, stale ETag `412`, disabled
publication gate `403`, missing target `404`, and repeated DELETE with the prior
valid ETag `404`. Existing auth errors remain `401`/`503`, actor errors remain
`400`, and safe persistence failures remain `503`.

Provider DELETE locks the provider and its dependent operational rows, records
the deletion evidence, and permanently removes the provider, offerings,
certifications, capability data, and other cascading operational data. A
provider with zero offerings is supported. Unrelated providers and offerings
are not touched.

Offering DELETE locks the offering and parent provider, records its evidence,
removes only the target offering, then advances the parent revision. The parent,
all siblings, and same-category siblings remain unchanged; a stale aggregate
provider ETag is therefore invalidated.

## PATCH attribute-removal contract

No field-specific DELETE route or ambiguous null convention was added. Existing
PATCH semantics are now explicitly documented as whole-selected-map
replacement:

1. GET the current entity and ETag.
2. Copy the editable JSON map to change.
3. Remove exactly the optional key that should become not declared.
4. PATCH the complete replacement for that selected map with `If-Match`.

For example:

```json
{
  "custom_capability_fields": {
    "retained_key": {"value": 2},
    "explicitly_unknown_key": {"status": "unknown"}
  }
}
```

Omitted keys inside the supplied map are removed. Other keys in the replacement,
omitted top-level fields, the parent, and sibling offerings are preserved. `{}`
clears an optional map. `null` is rejected rather than interpreted as deletion.
Missing/not-declared remains distinct from a valid explicit unknown value.
Immutable IDs and controlled offering category/family fields cannot be removed
or changed. Existing controlled-field, numeric, provenance, forbidden-field,
and route-identity validation remains in effect.

## Transaction, retention, and outbox policy

Deletion is one database transaction. The service locks and validates the
current row, checks the ETag before mutation, captures stable external IDs,
redacts deleted-scope history, creates a `ProviderPublication` tombstone and
pending `CatalogueSyncEvent` rows, and only then deletes operational rows. Any
failure rolls the tombstone, history redaction, parent revision, and operational
deletion back together.

`ProviderPublication.Operation` now includes `delete`. Migration
`0003_alter_providerpublication_operation.py` is the only schema migration.
`ProviderPublication.provider` already used nullable `SET_NULL`, and sync events
already belonged to publications, so no unsafe cascade or FK redesign was
needed.

The irreversible-retention policy is:

- A deleted provider's prior submitted and normalized payloads, validation
  details, and historic actor identifiers are cleared before its operational
  aggregate is deleted.
- A deleted offering is removed from every retained aggregate snapshot that
  contained it; affected raw submitted payloads and validation details are
  cleared. Provider and sibling normalized state remains available.
- A new delete publication retains only contract/status/timestamps, deletion
  actor attribution, provider/entity external IDs, and for provider deletion the
  captured offering IDs needed by semantic cleanup.
- Existing and new outbox rows retain external entity IDs, operation, status,
  attempts, and processing metadata. No unrelated provider history is deleted.

This prevents nullable historical snapshots from becoming an accidental full
archive of permanently deleted identifying/capability data while preserving the
minimal durable evidence needed for synchronization and troubleshooting.

Provider deletion emits one pending `DELETE` event for the provider and one for
each captured offering. This is explicit enough for deterministic resource
removal and a complete catalogue rebuild. Offering deletion emits exactly one
pending offering `DELETE` event. The accepted response intentionally remains
`sync_pending`/`pending`: M3 does not perform automatic semantic publication and
does not claim immediate RDF/Fuseki or discovery-search removal. That automatic
handoff remains M4.

## Files changed

- `backend/apps/api/lifecycle_security.py`
- `backend/apps/api/views/get_views.py`
- `backend/apps/api/views/post_views.py`
- `backend/apps/providers/models.py`
- `backend/apps/providers/provider_lifecycle_write_service.py`
- `backend/apps/providers/migrations/0003_alter_providerpublication_operation.py`
- `backend/tests/test_provider_detail_api.py`
- `backend/tests/test_m3_lifecycle_deletion.py`
- `docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`
- `docs/codex/Reports/M3_provider_offering_delete_and_attribute_patch_report.md`

The repository tracks the partner-document directory with lowercase path casing
on this Windows checkout; its content is the requested Partner API document.

## Verification

All commands used the repository's existing virtual environment and only
disposable Django test databases or in-memory/mocked semantic components.

Baseline before implementation:

```text
python manage.py test tests.test_provider_lifecycle_write_api tests.test_provider_detail_api tests.test_m1_lifecycle_pilot_readiness tests.test_m2_multi_offering_management tests.test_m76_external_exposure_readiness tests.test_catalogue_sync_service tests.test_catalogue_sync_recovery tests.test_catalogue_sync_concurrency --verbosity 1
72 passed; 0 failed; 0 skipped
```

Focused M1–M3/security/sync regression after implementation:

```text
python manage.py test tests.test_provider_lifecycle_write_api tests.test_provider_detail_api tests.test_m1_lifecycle_pilot_readiness tests.test_m2_multi_offering_management tests.test_m3_lifecycle_deletion tests.test_m76_external_exposure_readiness tests.test_catalogue_sync_service tests.test_catalogue_sync_recovery tests.test_catalogue_sync_concurrency --verbosity 1
82 passed; 0 failed; 0 skipped
```

Full local Django suite (which applies migration `0003` to its disposable test
database):

```text
python manage.py test --verbosity 1
567 passed; 13 skipped; 0 failed
```

Final targeted M3 run:

```text
python manage.py test tests.test_m3_lifecycle_deletion --verbosity 1
10 passed; 0 failed; 0 skipped
```

Static Django/migration checks:

```text
python manage.py makemigrations --check --dry-run
No changes detected

python manage.py check
System check identified no issues (0 silenced)

git diff --check
No errors
```

## Limitations and handoff

- M3 records pending semantic deletion work but does not automatically invoke
  RDF generation, Fuseki, or search refresh. Automatic semantic publication is
  M4.
- No operator synchronization API was added.
- No external infrastructure or live search behavior was validated or changed.
- The work is committed only to the focused branch. It is not merged to `main`
  and is not deployed to Vercel.

Stop after M3 and await review before any M4 work.
