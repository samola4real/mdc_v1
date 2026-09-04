# Codex Prompt — MDC v1 Resume Audit + Vercel Deployment Readiness

## Runtime / reasoning guidance

Use a **cost-efficient Codex GPT-5.6-family setup**. If selectable, prefer a suitable intelligence tier such as **Sol or Luna** with **medium reasoning** or **standard/high reasoning**.  
**Do not use Ultra / Extra-High reasoning unless a specific blocker genuinely requires it.**

## Task

I am resuming work on the **MaaSAI MaaS Dynamic Catalogue (MDC)** after a couple of months away.

Repository root:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog
```

Perform a **read-only repository audit first**. Do not implement, refactor, delete, or modify application code during this task.

The audit has **two parts**:

1. Reconstruct the current state of `MDC_V1`: what has been completed, what works now, what remains, important design decisions, technical debt/gaps, and the recommended next development plan.
2. Assess exactly what is required to deploy the MDC Django backend on **Vercel** and expose its APIs publicly to other MaaSAI components such as the Cloud MaaS Marketplace.

Create one comprehensive Markdown report.

## Output file

Save the report here:

```text
C:\Users\Elahi\Desktop\mdc_v1\mdc-catalog\docs\Phase_2
```

Use this filename:

```text
00_mdc_v1_resume_and_vercel_deployment_audit.md
```

Do not overwrite an unrelated existing file. If that exact filename already exists, inspect it and update it only if it is clearly the same audit artifact; otherwise use the next integer prefix.

---

# Part 1 — MDC v1 Current-State Audit

Inspect the **actual repository**, not assumptions or memory.

Review at minimum:

- repository structure
- `README*`
- `docs/`
- `backend/`
- Django settings and URL configuration
- API views, serializers, services, loaders and validators
- ontology/RDF code
- SPARQL/Fuseki integration
- curated provider data
- tests
- scripts
- dependency files
- environment/configuration files
- Docker files, if present
- Git status and recent Git history, if available

Pay special attention to prior MDC v1 work around:

- Django foundation
- health endpoint
- catalogue/filter endpoints
- provider/offering retrieval
- provider publication
- controlled vocabularies
- seed-data validation
- RDF generation
- RDFLib retrieval
- optional remote Fuseki retrieval
- matching/alignment logic
- H1–H9 work/tests/evidence, if present in the repository
- Tasowheel seed data and ontology alignment
- provider staging/custom fields versus controlled ontology-compatible fields
- GET views under `views/get_views.py` and POST views under `views/post_views.py`, where applicable

### Verify, do not assume

There may be differences between old design documents and the code that was actually implemented.

For example, verify the **real API paths** in Django rather than assuming `/api/v1/...` or `/api/...`.

Where documentation and implementation differ, explicitly show:

```text
Documented:
Implemented:
Recommended source of truth:
Action required:
```

### Run verification

Run the relevant local/focused test suite if the environment permits.

Record:

- exact command(s)
- number of tests
- pass/fail result
- important skipped/optional tests
- failures or environment blockers

Do not claim a test passed unless you actually ran it in this audit or there is explicit repository evidence that you clearly label as historical evidence.

### Part 1 report structure

Include:

1. Executive summary
2. Current architecture
3. Current repository/component map
4. What has been completed
5. Current API inventory
6. Current data/ontology/RDF/Fuseki flow
7. Current provider-publication flow
8. Current search/matching flow
9. Testing status
10. Important design decisions already established
11. Documentation/code drift or inconsistencies
12. Known gaps and technical debt
13. What remains to complete MDC v1
14. Recommended Phase 2 backlog
15. Prioritized next actions:
   - **P0 — required before public deployment**
   - **P1 — required for reliable MaaSAI integration**
   - **P2 — later improvements**
16. A short **“Where I should restart coding”** section naming the best next task/file/module.

For completed work, cite repository paths and relevant tests so I can quickly re-orient myself.

---

# Part 2 — Vercel Deployment and Public API Readiness

Assume I have **never used Vercel**. Explain the deployment pragmatically and step by step.

First determine whether this MDC backend, **as currently implemented**, can reasonably run on Vercel.

Do not simply say “yes” or “no”.

Analyse at minimum:

- Django on Vercel/serverless Python
- WSGI/ASGI entry point
- dependency installation
- Python/runtime version
- `vercel.json` or equivalent configuration
- Django settings split for production
- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- trusted origins / CSRF settings where relevant
- CORS for MaaSAI Marketplace and other consumers
- environment variables/secrets
- static files, if relevant
- filesystem persistence limitations
- logging
- timeouts/serverless execution constraints
- health endpoint
- API authentication/authorization
- rate limiting/basic abuse protection
- HTTPS/public domain
- API versioning
- OpenAPI/API documentation, if present
- deployment verification using `curl` or equivalent

## Critical Fuseki/RDF question

The current MDC may rely on Apache Jena Fuseki and/or local RDF files.

Assess carefully:

1. Can Fuseki itself run appropriately inside the same Vercel deployment?
2. If not, where should Fuseki/RDF storage run?
3. What changes are required in MDC settings/configuration so Vercel can call it?
4. What happens if Fuseki is temporarily unavailable?
5. Which current endpoints can operate without Fuseki and which require it?

Do not silently replace Fuseki with another technology.

If Vercel + external Fuseki is the sensible architecture, state that clearly.

If Vercel is a poor fit for this backend, still explain the **minimum viable Vercel approach**, then compare it briefly with one or two more suitable hosting patterns.

## Required deployment recommendation

Provide:

### A. Feasibility verdict

Use one:

- `Suitable with minor changes`
- `Suitable with moderate changes`
- `Possible but not recommended`
- `Not suitable for the current architecture`

Explain why.

### B. Recommended target architecture

Show a simple text diagram, for example:

```text
Marketplace / MaaSAI components
        |
      HTTPS
        v
Vercel-hosted Django API
        |
        | SPARQL over HTTPS
        v
Externally hosted Fuseki
        |
        v
MDC RDF catalogue
```

Use the architecture actually justified by the repository.

### C. Exact repository changes needed

For every required change, provide:

- file/path
- purpose
- whether file already exists
- precise change required
- priority: P0/P1/P2

Examples may include:

```text
requirements.txt
vercel.json
api/index.py
config/settings/production.py
config/urls.py
.env.example
CORS configuration
Fuseki endpoint environment variables
```

These are examples only. Inspect the repo and use the correct files for this project.

### D. Step-by-step Vercel guide for a first-time user

Cover from zero to deployed API:

1. prerequisites
2. Git/GitHub preparation
3. Vercel account/project setup
4. importing the repository
5. project root configuration
6. build/runtime configuration
7. environment variables
8. deployment
9. reading deployment logs
10. testing `/health`
11. testing catalogue/provider/search APIs
12. configuring the Marketplace to call the public base URL
13. CORS/origin setup
14. redeployment workflow after future Git pushes
15. rollback/basic recovery

Make steps concrete and repository-specific.

### E. Environment-variable table

Include at least:

```text
Variable
Required?
Example/placeholder
Where used
Secret?
Vercel scope
```

Never expose real secrets from the repository. Flag any accidentally committed secrets.

### F. Public API integration contract

State what another MaaSAI component needs from MDC:

- public base URL
- endpoint paths/methods
- request content type
- authentication method, if any
- CORS requirements for browser-based Marketplace calls
- expected status codes
- timeout/retry considerations
- health/readiness check
- example `curl` calls using placeholders

### G. Deployment blockers checklist

Create a final checklist:

```text
[ ] blocker
[ ] blocker
...
```

Clearly distinguish:

- must fix before first Vercel deployment
- must fix before allowing other MaaSAI components to rely on the API
- optional production hardening

---

# Evidence and quality rules

- Ground findings in repository evidence.
- Mention exact file paths.
- Do not invent completed work.
- Do not treat old documentation as proof that code exists.
- Clearly distinguish:
  - **implemented and verified**
  - **implemented but not verified**
  - **documented/planned only**
  - **missing**
- If something cannot be verified, say so.
- Prefer concise tables over repetitive prose.
- Focus on practical next actions, not generic Django/Vercel tutorials.
- Do not make code changes in this audit.
- Do not create deployment resources or Vercel projects.
- Do not expose secrets.
- Do not spend tokens producing long explanations of basic Python/Django concepts unless necessary for deployment.

## Final console response

After creating the report, respond only with a concise summary containing:

1. report path
2. current MDC v1 status in 3–5 bullets
3. Vercel feasibility verdict
4. top 5 P0 actions
5. tests run and result
