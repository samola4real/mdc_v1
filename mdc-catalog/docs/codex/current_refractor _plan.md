# MDC v1 — Refactoring and Testing Roadmap

We will proceed through 6 milestones, starting from the current Django backend and ending with a fully tested MDC deployment on Vercel.

The main objective is to support the complete provider lifecycle:

Register → Add offerings → Update → Delete → Automatically synchronize RDF → Search updated catalogue.

We will work milestone by milestone. Each milestone must pass its acceptance tests before moving to the next.

## Overall development roadmap

M1

Baseline and API readiness

Inspect existing implementation, establish a clean baseline, and configure temporary authentication bypass.

M2

Scalable provider and offering management

Enable multiple independent offerings per provider, including within the same service category.

M3

Complete lifecycle operations

Implement provider/offering deletion and consistent attribute removal through PATCH.

M4

Automatic semantic synchronization

Make successful lifecycle changes immediately visible through canonical service discovery.

M5

Vercel deployment and Postman validation

Deploy the completed backend and verify lifecycle operations against the intended Neon database and semantic catalogue.

M6

Marketplace integration and release

Finalize documentation, test Marketplace compatibility, and prepare the plenary demonstration.

## M1 — Baseline verification and API readiness

Start here

Goal: Confirm the current backend structure and prepare the existing trusted lifecycle for the next development phase without breaking working features.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M1.1

|

Verify local Git `main` against the current GitHub repository and create a working branch.

|
|

M1.2

|

Identify existing provider lifecycle views, serializers, services, database models and synchronization components.

|
|

M1.3

|

Confirm current API routes, lifecycle feature flags and database configuration.

|
|

M1.4

|

Preserve the existing authentication implementation and configure a temporary, explicit authentication bypass for the designated pilot environment.

|
|

M1.5

|

Verify the existing POST, GET and PATCH operations locally.

|
|

M1.6

|

Confirm the actual RDF/Fuseki backend used by service discovery.

|

### Testing

Test public health, filters, search and the existing provider lifecycle operations.

Confirm that changing the authentication configuration does not alter request schemas or disable the ability to restore authentication later.

Do not modify existing Tasowheel or Framo Morat records during baseline testing.

M1 completion criteria

Existing tests pass, the actual lifecycle and semantic-search paths are documented, and the temporary authentication configuration is isolated to the intended test deployment.

## M2 — Scalable provider and offering management

Goal: Allow one provider to maintain multiple independent offerings without service-category conflicts.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M2.1

|

Review current provider/offering database models and uniqueness constraints.

|
|

M2.2

|

Define stable, independent offering identifiers.

|
|

M2.3

|

Refactor offering creation to accept multiple offerings within the same service category.

|
|

M2.4

|

Update lifecycle serializers and provider/offering services.

|
|

M2.5

|

Update RDF resource identifiers to support independent offering IDs.

|
|

M2.6

|

Preserve existing provider and offering identifiers during migration.

|
|

M2.7

|

Ensure provider-specific capability data remains separate from generic search and lifecycle logic.

|

### Testing

Use a disposable test provider.

|
Test

|

Expected result

|
| --- | --- |
|

Register a provider with one offering

|

Provider and offering are created

|
|

Add a second offering in the same category

|

Both offerings exist independently

|
|

Add an offering in a different category

|

All offerings coexist

|
|

Register a duplicate offering ID

|

Request is rejected

|
|

Update one offering

|

Other offerings remain unchanged

|
|

Retrieve all provider offerings

|

Every offering appears with its own ID

|

M2 completion criteria

A provider can maintain multiple independently addressable offerings, including offerings sharing a service category. Existing provider data and IDs remain valid.

## M3 — Complete provider lifecycle and deletion

Goal: Implement full provider and offering management with consistent PATCH and DELETE behavior.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M3.1

|

Implement `DELETE /api/providers/{provider_id}`.

|
|

M3.2

|

Implement `DELETE /api/offerings/{offering_id}`.

|
|

M3.3

|

Define permanent deletion of dependent operational records.

|
|

M3.4

|

Finalize attribute-removal semantics through PATCH.

|
|

M3.5

|

Preserve unrelated capabilities when removing one attribute.

|
|

M3.6

|

Extend lifecycle persistence and outbox handling for deletion events.

|
|

M3.7

|

Define consistent responses for missing records, duplicate operations and invalid requests.

|

### Testing

Use disposable provider records.

|
Test

|

Expected result

|
| --- | --- |
|

Delete one offering

|

Only the selected offering is deleted

|
|

Retrieve the deleted offering

|

Returns 404

|
|

Delete provider

|

Provider and dependent operational offerings are removed

|
|

Delete nonexistent provider

|

Returns documented not-found response

|
|

Remove one attribute through PATCH

|

Other attributes remain unchanged

|
|

PATCH an existing offering

|

Updated values persist

|
|

Repeat a deletion

|

Returns documented response without affecting unrelated records

|

Keep the existing ETag support and test stale-update protection. The pilot authentication bypass should not require removing concurrency checks.

M3 completion criteria

Provider and offering CRUD operations work correctly at the database level, with no unintended changes to unrelated records.

## M4 — Automatic RDF and semantic catalogue synchronization

Critical plenary requirement

Goal: Ensure that successful provider lifecycle operations are reflected in the actual catalogue used by consumer service discovery.

The Marketplace must not need to call a separate synchronization API.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M4.1

|

Inspect the existing RDF generation, outbox and synchronization services.

|
|

M4.2

|

Refactor synchronization to support newly created, updated and deleted offerings.

|
|

M4.3

|

Automatically trigger semantic synchronization after accepted lifecycle writes.

|
|

M4.4

|

Ensure RDF generation preserves distinct offering identities and current capability values.

|
|

M4.5

|

Remove obsolete RDF evidence after attribute or offering deletion.

|
|

M4.6

|

Ensure provider deletion removes all associated searchable provider/offering resources.

|
|

M4.7

|

Verify that the deployed discovery service actually reads the updated semantic data.

|
|

M4.8

|

Handle synchronization failure without falsely reporting successful publication.

|

### Testing

|
Lifecycle action

|

Immediate discovery test

|
| --- | --- |
|

Register provider

|

New offering is discoverable after successful publication

|
|

Add offering

|

New offering appears alongside existing offerings

|
|

PATCH capability

|

Updated value is used in subsequent matching

|
|

Remove capability

|

Removed value is no longer used as matching evidence

|
|

Delete offering

|

Deleted offering disappears from discovery

|
|

Delete provider

|

All provider offerings disappear from discovery

|

Also test synchronization failures and retries.

M4 completion criteria

After MDC reports successful publication, the next canonical service-discovery request reflects the completed change without manual synchronization.

This milestone should include an end-to-end test that verifies the actual search backend, not merely successful RDF file generation.

## M5 — Vercel deployment and Postman testing

Goal: Verify the full lifecycle against the deployed MDC rather than relying exclusively on local unit tests.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M5.1

|

Deploy the tested implementation to a controlled Vercel Preview environment using a separate test database and semantic dataset.

|
|

M5.2

|

Verify the deployed API routes and runtime configuration.

|
|

M5.3

|

Verify PostgreSQL persistence and semantic synchronization.

|
|

M5.4

|

Import the complete Postman test collection and configure the target environment.

|
|

M5.5

|

Execute positive and negative lifecycle tests.

|
|

M5.6

|

Confirm temporary authentication settings are applied only to the intended pilot deployment.

|
|

M5.7

|

Deploy the validated implementation to the intended plenary environment.

|
|

M5.8

|

Repeat the key Postman tests on the deployed plenary backend using disposable records.

|

### Postman test sequence

1. GET health and catalogue filters.

2. POST a canonical service-discovery request.

3. POST a new test provider with one offering.

4. GET the newly registered provider.

5. POST a second offering under the same provider.

6. PATCH provider and offering information.

7. PATCH to remove an individual capability attribute.

8. Search and verify the updated catalogue after each successful change.

9. DELETE one offering and verify that the other remains.

10. DELETE the provider and verify that all its offerings disappear from discovery.

For each operation, inspect the actual HTTP status and response body, not just the success message in Postman.

M5 completion criteria

The complete provider lifecycle passes on the deployed backend, including immediate semantic discovery, without relying on the demonstration frontend.

## M6 — Marketplace integration and plenary release

Goal: Deliver a stable MDC backend that the Marketplace team can use without additional API redesign.

### Development tasks

|
ID

|

Task

|
| --- | --- |
|

M6.1

|

Freeze the canonical lifecycle API contract, including POST, GET, PATCH and DELETE.

|
|

M6.2

|

Document required request bodies, responses and error behavior.

|
|

M6.3

|

Provide the Marketplace team with the accepted Postman collection and integration examples.

|
|

M6.4

|

Conduct a joint provider registration and discovery test with the Marketplace team.

|
|

M6.5

|

Confirm that provider modifications are visible through consumer discovery.

|
|

M6.6

|

Prepare the demonstration dataset and recovery procedure.

|
|

M6.7

|

Create a release tag and document the accepted deployment.

|

### Final plenary acceptance scenario

Marketplace registers a new provider

Marketplace adds and updates offerings

MDC automatically updates the semantic catalogue

Consumer searches and receives the updated offerings

The demonstration should also show that deleting an offering removes only that offering, while deleting a provider removes all its dependent offerings from active discovery.

## How we will manage refactoring, testing and Git

I recommend a simple, consistent development cycle for every milestone.

1. Create a focused Git branch

2. Inspect only the relevant current implementation

3. Implement the milestone's scoped changes

4. Run focused tests and regression tests

5. Review the diff and document test evidence

6. Commit and merge the accepted changes

### Suggested Git branches and commit messages

|
Milestone

|

Branch

|

Commit message

|
| --- | --- | --- |
|

M1

|

`phase4/lifecycle-baseline`

|

`chore(lifecycle): establish pilot baseline`

|
|

M2

|

`phase4/multi-offering`

|

`feat(providers): support independent offering identities`

|
|

M3

|

`phase4/lifecycle-delete`

|

`feat(providers): implement provider and offering deletion`

|
|

M4

|

`phase4/automatic-semantic-sync`

|

`feat(ontology): synchronize lifecycle changes automatically`

|
|

M5

|

`phase4/deployment-validation`

|

`test(api): validate deployed provider lifecycle`

|
|

M6

|

`phase4/marketplace-integration`

|

`docs(api): finalize marketplace lifecycle integration`

|

For every milestone, Codex should produce a short report containing changed files, implemented behavior, tests run, results, limitations and Git commit hash.

Do not repeat old historical development reports. The current GitHub `main` implementation and its accepted tests should be the baseline.

## Recommended starting point

Start with M1 — Baseline verification and API readiness.

We should keep M1 short. Its purpose is to establish which existing components can be reused and which need modification, not to restart the entire MDC architecture discussion.

Once the current lifecycle, database and semantic-search implementation are confirmed, proceed directly to M2 and continue through the milestones.

The final release gate is simple: a successful provider lifecycle operation must be reflected in the next MDC consumer search, using the deployed backend and without requiring any manual action from the Marketplace.
