# Codex Task 11 — Local `.env` Standardization and Managed PostgreSQL Gate Resume

## Recommended Codex configuration

- Label: `[mdc_env_postgres_resume]`
- Model: GPT-5.6 Sol
- Reasoning: Medium

Do not start M7.3 automatically.

---

# Context

Repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1
```

Project root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

The user copied the prepared standardization files into:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\mdc_env_standardization_files
```

That helper folder contains versions of:

```text
.gitignore
.env.example
.env
backend/config/settings.py
backend/config/settings_local.py
```

The tracked repository has also already received environment-standardization commits on `origin/main`. Therefore, do NOT blindly overwrite newer tracked files with helper-folder copies. Current synchronized Git content is the source of truth; the helper folder is only a local reference/starter.

The current managed PostgreSQL validation gate previously stopped with:

```text
BLOCKED_MANAGED_POSTGRES_DATABASE_URL_REQUIRED
```

because `DATABASE_URL` was not available to Codex.

The desired local configuration convention is now:

```text
mdc-catalog/.env
```

as the single canonical local MDC application configuration file.

`.env.local` remains tool/platform-specific and must not be merged into `.env` automatically.

---

# Goal

Set up the local MDC environment configuration correctly and safely, verify the ignore rules and Django loading behavior, and then resume the managed PostgreSQL validation gate only if a valid non-empty PostgreSQL `DATABASE_URL` is actually available.

Do not expose or print secrets.

---

# Step 1 — Synchronize and inspect

From repository root:

1. Run `git status`.
2. Fetch/pull `origin/main` normally if needed.
3. Do not discard unrelated user changes.
4. Confirm the tracked environment-standardization changes already present on `main`.
5. Inspect:
   - root `.gitignore`
   - `mdc-catalog/.env.example`
   - `mdc-catalog/backend/config/settings.py`
   - `mdc-catalog/backend/config/settings_local.py`
   - local helper folder `mdc-catalog/mdc_env_standardization_files/`
6. Treat current Git-tracked files as authoritative if helper-folder copies differ.

---

# Step 2 — Canonical local `.env`

The canonical local application file must be:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\.env
```

Requirements:

- If `mdc-catalog/.env` does not exist, create it locally from the helper-folder `.env` starter or from `.env.example`.
- If it already exists, preserve all existing non-empty secret values and merge only missing keys/comments where useful.
- NEVER overwrite an existing non-empty `DATABASE_URL`, `DJANGO_SECRET_KEY`, or other secret value with a blank/template placeholder.
- Do not print the `.env` contents.
- Do not print secret values in console output, reports, diffs, or errors.
- Do not copy `VERCEL_OIDC_TOKEN` or other Vercel CLI tokens from `.env.local` into `.env`.
- Do not commit `.env`.
- Do not commit `.env.local`.

Expected key categories in `.env`:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
DATABASE_URL
MDC_DEMO_API_ENABLED
MDC_PROVIDER_PUBLICATION_ENABLED
FUSEKI_BASE_URL
FUSEKI_DATASET
FUSEKI_QUERY_ENDPOINT
FUSEKI_UPDATE_ENDPOINT
SERVICE_DISCOVERY_FUSEKI_QUERY_ENDPOINT
FUSEKI_TIMEOUT_SECONDS
```

Do not invent credentials or a PostgreSQL URL.

---

# Step 3 — Verify `.gitignore`

The repository must protect all local secret files while tracking only the safe template.

Confirm the root `.gitignore` has equivalent semantics to:

```gitignore
# Local environment and secret files
.env
.env.*
!.env.example
!mdc-catalog/.env.example
```

Verify with Git commands, for example:

```powershell
git check-ignore -v mdc-catalog/.env
git check-ignore -v mdc-catalog/.env.local
git check-ignore -v mdc-catalog/.env.example
```

Expected behavior:

- `mdc-catalog/.env` -> ignored
- `mdc-catalog/.env.local` -> ignored
- `mdc-catalog/.env.example` -> NOT ignored / remains tracked

If current tracked `.gitignore` already satisfies this, do not change it unnecessarily.

Also confirm that the helper folder itself does not accidentally cause secret files to be staged. If it contains a real `.env`, make sure that file is ignored and is not committed.

---

# Step 4 — Verify Django `.env` loading

Confirm current `backend/config/settings.py` loads the canonical local file using `python-dotenv` with platform environment precedence, equivalent to:

```python
load_dotenv(PROJECT_ROOT / ".env", override=False)
```

The semantics must be:

```text
OS / platform environment variable exists
        -> use it
otherwise
        -> load value from mdc-catalog/.env
otherwise
        -> application default if allowed
```

Do not introduce environment-specific files such as `.env.postgres`, `.env.fuseki`, `.env.development`, etc.

Confirm production/cloud portability remains intact: Vercel today and AWS later may inject the same variable names through platform-managed environment/secrets without changing application code.

Confirm `settings_local.py` does not force provider-publication/demo behavior in a way that defeats values from the canonical `.env`.

---

# Step 5 — Safe local verification

Without exposing secrets, verify:

```powershell
python manage.py check
python manage.py test tests.test_database_configuration -v 2
```

Also verify programmatically/safely that Django sees either:

```text
SQLite fallback
```

or

```text
PostgreSQL engine
```

Do not print the connection URL, username, password, hostname, or query-string credentials.

If `DATABASE_URL` is present, only report a safe boolean/status such as:

```text
DATABASE_URL present: yes
Database engine: PostgreSQL
```

If absent/blank, report only:

```text
DATABASE_URL present: no
```

---

# Step 6 — Resume managed PostgreSQL validation gate only if ready

If and only if `DATABASE_URL` is non-empty and resolves to Django's PostgreSQL engine, resume the existing managed PostgreSQL validation gate defined in:

```text
mdc-catalog/docs/prompts/10_mdc_v1_m72_managed_postgres_validation_gate_codex_prompt.md
```

Continue from the previous blocker rather than restarting unrelated work.

The gate should validate the real managed PostgreSQL database, including the already-defined requirements for migrations, curated provider import, JSONB/schema behavior, exact DB/YAML parity, RDF parity, matcher parity, idempotency/rollback/locking behavior, and regression safety.

Do not start M7.3 automatically.

If `DATABASE_URL` is still absent or blank, stop cleanly with exactly:

```text
BLOCKED_MANAGED_POSTGRES_DATABASE_URL_REQUIRED
```

Do not invent or request credentials in chat output.

---

# Step 7 — Git safety

- Never stage or commit `.env`.
- Never stage or commit `.env.local`.
- Never stage or commit database credentials.
- Never stage or commit the helper-folder `.env` if it contains secrets.
- Commit only tracked configuration/docs changes if genuinely required after comparison with current `origin/main`.
- If no tracked change is needed, make no empty/no-op commit.
- Push only legitimate tracked changes.

Before committing, inspect:

```powershell
git status --short
git diff --check
```

Ensure no secret-bearing file appears in staged changes.

---

# Final console response

Return only a concise status summary with no secret values:

1. Git synchronization/worktree status
2. canonical `mdc-catalog/.env` exists: yes/no
3. `.env` ignored by Git: yes/no
4. `.env.local` ignored by Git: yes/no
5. `.env.example` tracked/not ignored: yes/no
6. Django canonical `.env` loading verified: yes/no
7. platform environment precedence (`override=False`) verified: yes/no
8. `DATABASE_URL` present: yes/no
9. database engine: SQLite or PostgreSQL
10. `manage.py check` result
11. database-configuration test result/count
12. tracked files changed, if any
13. Git commit hash/message, only if a real tracked change was needed
14. one final marker:

If the PostgreSQL gate completes successfully:

```text
READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
```

If the only remaining blocker is missing database URL:

```text
BLOCKED_MANAGED_POSTGRES_DATABASE_URL_REQUIRED
```

If another blocker exists, use:

```text
NOT_READY_FOR_M73_PROVIDER_VALIDATION_READ_LIFECYCLE
```

and state the blocker without exposing secrets.
