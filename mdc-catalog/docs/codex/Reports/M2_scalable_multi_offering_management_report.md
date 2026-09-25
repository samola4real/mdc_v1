# M2 scalable multi-offering management report

## Result

M2 is complete on `phase4/multi-offering`. One provider can now register or
later add multiple independently identified offerings in the same controlled
service category, while existing single-offering requests keep their legacy
identifier. Exact offering IDs remain stable through persistence, lifecycle
reads and PATCH, publication snapshots, outbox events, RDF resources, and
discovery projection.

This work was tested locally only. It was **not merged**, **not deployed**, and
did not read or modify production, Neon, Vercel, Fuseki, Tasowheel, or Framo
Morat data.

## Baseline and worktree

| Item | Verified value |
| --- | --- |
| Repository | `https://github.com/samola4real/mdc_v1.git` |
| Fetched baseline | `origin/main` at `55b03d545e309d1e6e96bf7304899b94ada211c8` |
| M1 prerequisite | Reviewed merge `ad8c85e30280496d80b46d8ab076e1fc45d26f09` is an ancestor of the baseline |
| Prompt commit | `55b03d545e309d1e6e96bf7304899b94ada211c8` |
| Working branch | `phase4/multi-offering` |
| Isolated worktree | `C:\Users\Elahi\Desktop\mdc_v1_m2_worktree` |
| Implementation commit | `87fa1d3d2d482b36c1641e548bc066dc6c803ba6` |

The M2 worktree started clean. The original checkout stayed on `main`; its
pre-existing `.gitignore` and
`mdc-catalog/demo-frontend/src/pages/demo/index.js` edits were not modified,
stashed, discarded, copied, reset, or committed.

The report commit is the commit containing this document. Because a commit
cannot embed its own SHA, the authoritative final pushed branch-tip SHA is in
Git metadata and the completion summary.

## Former collision points

The active M2 audit found three application-level assumptions behind
`offering_id == provider_id + '_' + service_category`:

1. `ServiceDiscoveryPublicationSerializer._validate_offerings` rejected a
   second offering with the same `service_category` before persistence.
2. `normalize_service_discovery_publication` regenerated every ID solely from
   provider and category, so two accepted same-category items would collapse to
   the same value.
3. `add_provider_offering` and `_create_offering` generated that same legacy ID
   for every later offering in a category, producing a conflict.

Existing serializer/lifecycle tests and current manuals encoded those former
rules and were updated. Historical phase reports and old prompts were left
unchanged as historical records.

The following paths did **not** assume category uniqueness and already handled
exact offering IDs correctly: the `Offering` model, DB import/projection,
lifecycle repository, publication/outbox snapshots, RDF mapping/generation,
Fuseki/RDF candidate retrieval, local discovery matching, result ordering, and
public response mapping. These paths were retained and covered by new
end-to-end local tests.

## Selected creation and identity contract

- `provider_id` remains the stable provider identity.
- `offering_id` remains globally unique and immutable, and each offering has
  exactly one parent provider.
- `service_category` and `part_family` classify an offering; neither determines
  uniqueness.
- At initial `POST /api/provider-publication`, each `offerings[]` item may
  include an optional `offering_id`.
- At `POST /api/providers/{provider_id}/offerings`, the creation body may include
  the same optional `offering_id`.
- An explicit ID must be lower snake case, at most 512 characters, and begin
  with the owning `provider_id` plus `_`. It is preserved exactly.
- Explicit `offering_id` is accepted only at those two creation locations.
  Arbitrary nested IDs, other protected identifiers, and `offering_id` under
  PATCH remain rejected.
- If the ID is omitted and `{provider_id}_{service_category}` is free, MDC keeps
  that legacy ID. This preserves all existing first/single-offering behavior.
- If the legacy ID is taken, MDC derives
  `{provider_id}_{service_category}_{offering_name_slug}` using a deterministic
  lowercase ASCII snake-case slug.
- If the deterministic name form is also taken, MDC returns a clear conflict;
  it never silently numbers, overwrites, or transfers an identity. The client
  can retry with a distinct explicit ID.
- A name that cannot produce a safe fallback, or a generated fallback exceeding
  512 characters, receives `400 invalid_offering_id` and must use a valid
  explicit ID.

### Example: initial same-category registration

Input excerpt:

```json
{
  "provider_id": "example_forge",
  "offerings": [
    {
      "service_category": "precision_gears",
      "offering_name": "Standard gear line",
      "part_family": "gear",
      "support_status": "confirmed"
    },
    {
      "service_category": "precision_gears",
      "offering_name": "Heavy duty gear line",
      "part_family": "gear",
      "support_status": "confirmed"
    }
  ]
}
```

Resolved IDs, in submitted order:

```json
[
  "example_forge_precision_gears",
  "example_forge_precision_gears_heavy_duty_gear_line"
]
```

The existing single-offering response shape is unchanged.

### Example: explicit stable identity

```json
{
  "offering_id": "example_forge_northern_gear_cell",
  "service_category": "precision_gears",
  "offering_name": "Northern gear cell",
  "part_family": "gear",
  "support_status": "confirmed"
}
```

The explicit ID is used in the database row, response, outbox entity ID,
publication snapshot, lifecycle URL, RDF resource, and discovery result.

### Error behavior

| Case | Result |
| --- | --- |
| Unsafe, uppercase/hyphenated, overlong, or cross-provider explicit ID | `400 invalid_offering` with field details, or `400 invalid_provider_publication` during initial registration |
| Duplicate explicit ID within one initial payload | `400 invalid_provider_publication` |
| Existing explicit ID or deterministic same-name fallback | `409 offering_already_exists` |
| Concurrent duplicate insert losing the DB uniqueness race | Safe `409`, with atomic rollback and no partial history/outbox rows |
| `offering_id` nested in custom/capability data | `400` |
| Attempt to PATCH `offering_id` | `400`; stored identity remains unchanged |

## Model and migration decision

No schema migration is required. `Offering.offering_id` is already a globally
unique `CharField(max_length=512)` in both the model and initial migration, and
the provider foreign key already expresses one parent provider. There was no
database uniqueness constraint on `(provider, service_category)` to remove.

The collision was exclusively in serializer rejection and ID generation. No
existing row or identifier was renamed or rewritten. `manage.py makemigrations
--check --dry-run` reported `No changes detected` (with a local warning that the
ordinary SQLite file was unavailable from the isolated sandbox); the test
databases applied the existing two provider migrations successfully.

## Implementation and propagation

- Added shared safe-ID validation, deterministic offering-name slug generation,
  ordered resolution, and explicit collision errors.
- Narrowed protected-identifier rejection only for `offerings[].offering_id` and
  the single offering-creation body; all other protected/nested locations remain
  closed.
- Initial registration resolves all identities before its atomic write and
  checks persistent/global conflicts. Later offering creation resolves under
  the locked provider transaction. The existing unique database column remains
  the final concurrent-write guard.
- Registration and later creation pass the resolved ID into `_create_offering`
  rather than recomputing identity from category.
- Existing repository/snapshot/outbox/RDF/search code consumes the stored exact
  ID. Focused tests demonstrate two RDF offering nodes, separate capability
  evidence values, and two discovery results for one provider/category.
- Offering order, evidence dictionaries, null/absent behavior, controlled
  taxonomy validation, custom fields, public discovery contract, unversioned
  routes, M1 pilot configuration, secured-mode auth/actor rules, and PATCH ETag
  concurrency were preserved.

## Tests and evidence

All write tests used disposable Django test databases. RDF/discovery tests used
in-memory graphs and local records. The full suite's generated RDF artifact was
written to the operating-system temporary directory. No external service was
called.

| Command | Result |
| --- | --- |
| `python manage.py test tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_provider_publication_api tests.test_provider_lifecycle_write_api tests.test_provider_detail_api tests.test_service_discovery_db_repository tests.test_service_discovery_rdf_generator tests.test_service_discovery_matching_alignment tests.test_m1_lifecycle_pilot_readiness tests.test_m76_external_exposure_readiness --verbosity 1` | Baseline before implementation: 150 passed, 0 failed, 0 skipped |
| `python manage.py test tests.test_m2_multi_offering_management tests.test_service_discovery_publication_serializer tests.test_service_discovery_publication_normalizer tests.test_provider_publication_api tests.test_provider_publication_validation_api tests.test_provider_lifecycle_write_api tests.test_provider_detail_api tests.test_service_discovery_db_repository tests.test_service_discovery_rdf_generator tests.test_service_discovery_matching_alignment tests.test_m1_lifecycle_pilot_readiness tests.test_m76_external_exposure_readiness --verbosity 1` | 176 passed, 0 failed, 0 skipped |
| `python manage.py test tests --verbosity 1` | 557 passed, 0 failed, 13 skipped |
| `python manage.py check` | Passed; no system-check issues |
| `python manage.py makemigrations --check --dry-run` | No model changes detected; no migration created |

The suite used the existing local virtual environment on Python 3.11.9 even
though `pyproject.toml` declares Python `>=3.12`. This was not a test failure,
but later deployment validation should use a declared Python version.

Remote Fuseki integration tests and deployed/Postman tests were **not run**.
They belong to later synchronization/deployment milestones.

## Files changed

- `backend/apps/providers/service_discovery_publication.py`
- `backend/apps/providers/provider_lifecycle_write_service.py`
- `backend/apps/api/service_discovery_publication_serializers.py`
- `backend/apps/api/provider_lifecycle_serializers.py`
- `backend/apps/api/views/post_views.py`
- `backend/tests/test_m2_multi_offering_management.py`
- `backend/tests/test_provider_lifecycle_write_api.py`
- `backend/tests/test_service_discovery_publication_serializer.py`
- `docs/Partner_API/mdc_v1_trusted_provider_lifecycle_integration.md`
- `docs/MDC_Comprehensive_Implementation_Report_and_User_Manual.md`
- `docs/codex/Reports/M2_scalable_multi_offering_management_report.md`

No frontend, provider data, migration, route, auth setting, ETag behavior,
automatic sync behavior, deployment configuration, or external infrastructure
was changed.

## Remaining M3/M4 risks

- **M3:** DELETE and final attribute-removal semantics remain unimplemented. Any
  deletion design must target stable offering IDs and preserve siblings in the
  same category.
- **M4:** lifecycle writes still only enqueue pending outbox events. Automatic
  DB-to-RDF-to-Fuseki processing is not connected, so newly accepted offerings
  are not guaranteed to appear in the next deployed canonical discovery call.
- M4 must retain the distinct offering IDs through updates/deletes and ensure
  stale RDF/YAML fallbacks do not collapse or resurrect sibling offerings.
- Actual PostgreSQL concurrency and deployed query/write dataset alignment need
  later environment tests; local tests cover DB uniqueness-race handling but do
  not claim deployed behavior.

## Blockers and state

There are no blockers to M2 review. The branch is **not merged** and the work is
**not deployed**. Stop here and await review before M3.
