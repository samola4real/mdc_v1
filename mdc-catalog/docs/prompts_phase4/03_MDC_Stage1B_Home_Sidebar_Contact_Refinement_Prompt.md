# Stage 1B — Home, sidebar and Contact: locked specification and runtime correction

**Operator decision: previous delivery NOT ACCEPTED.** This revised prompt supersedes earlier versions of task 03. The operator has approved the specification below. Do not expand scope or redesign.

## 1. First resolve the runtime discrepancy

The latest operator screenshots show the old template in both anonymous and authenticated states: Brand and public Dashboard links, four public cards, three generic signed-in project cards, old welcome text, two old contacts with search/filter controls, and the Home navigation group missing after login. The committed refinement at `ca3853cfb1d273eb4a10efa908ac11d452e37863` already implements much of the requested behavior. Wrong server/build/checkout is a hypothesis, not established fact.

- Fetch latest refs; continue existing branch `phase4/stage1b-frontend-integration` from reviewed report head `de60b44212c8e7f42b51460d65f67aec9ae977ca` or its verified descendant. Existing worktree: `C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend`. Verify Git SHA/status; preserve newer work. Do not start again from main.
- Inspect listeners on ports 3000 and 3001 and their owning process/worktree/build (read-only Windows inspection using Get-NetTCPConnection/Get-CimInstance where useful). Verify the actual served Home and Contact content and assets. Never print secrets in process output.
- Correct the demonstrated cause. Reuse one existing task worktree and one confirmed local server/origin; prefer the correct existing server, not another project/worktree. Rebuild only that worktree if needed. Stop only positively identified obsolete frontend processes with operator approval; never terminate unknown processes or overwrite/reset/stash/clean the original checkout. Preserve its unrelated .gitignore and index.js changes.
- Give the operator one exact clickable Home URL and verify it is the same origin being tested. Coordinate browser refresh and real Keycloak login on that origin. Do not assume operator error or browser cache. If the committed code already meets the requirements, do not rewrite it.

## 2. Locked specification

Keep existing MaaSAI template, logo, footer, theme selector, layout, components, Outfit typography and Keycloak login/profile/logout. No new features or redesign.

| Element | Anonymous | Authenticated |
| --- | --- | --- |
| Home sidebar group | Home, Contact, Help | Home, Contact, Help |
| Brand and generic Workspace menu | Absent | Absent |
| MaaS Dynamic Catalogue sidebar group | Hidden | Visible; Dashboard and existing authorized role links |
| Welcome heading on / | Welcome to MaaSAI | Welcome to MaaS Dynamic Catalogue |
| More info | https://documentation.maasai-srv.cigip.upv.es/ | https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/ |
| Home information cards | Contact, Project Website only | Contact, Project Website only |
| Contact page | Same four contacts, no search/filter/count | Same four contacts, no search/filter/count |
| Existing topbar | Login | Existing profile/logout |

**Critical invariant:** Home, Contact and Help must NEVER disappear when authentication or selected role changes, or when navigating to Contact, Help, MDC Dashboard or its role pages. Home must always navigate to /. Preserve existing role authorization, selected-role filtering and protected routes. /demo and its three child routes require authentication; existing role guards still apply. Do not show protected content during initialization. No new permissions.

### Home (/)

Reuse DashboardContent banner and existing card styling. Exact heading and documentation links are in the table.

Anonymous description: MaaSAI advances Manufacturing as a Service by enabling connected, intelligent and collaborative manufacturing ecosystems. The project supports digital manufacturing services, interoperability and collaboration between manufacturing providers and consumers.

Authenticated description: The MaaS Dynamic Catalogue (MDC) enables manufacturing providers to publish, manage and update their manufacturing services and capabilities. Through ontology-based data harmonization and semantic service discovery, MDC supports the identification of suitable manufacturing services based on consumer requirements.

Use appropriate info/external-link icon for More info. Only two existing-style cards in BOTH states:
- Contact — Contact the MDC development team for technical information and enquiries. Internal /home/Contact; envelope icon.
- Project Website — Explore the MaaSAI project, its objectives, activities and results. https://maasai-project.eu/; globe icon.

Remove Help, Sign In, Create a Project, View your Projects and Register a Resource cards. Keep sidebar Help and topbar Login. Keep current card label/spacing unless a correction is necessary.

### Contact (/home/Contact)

Public in both states. Existing card layout, logos or fallback initials, email links and copy-email controls. Heading Contact Detail; introductory text: MDC development team and MaaSAI project contacts. Show these four contacts in this order:
1. Jose Martinez Lastra — Tampere University — FAST-Lab; Unit Head; jose.martinezlastra@tuni.fi; group homepage https://research.tuni.fi/fast/
2. Samuel Afolaranmi — Tampere University — FAST-Lab; Developer, MaaS Dynamic Catalogue; samuel.afolaranmi@tuni.fi; MDC documentation https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/
3. Miguel Angel Mateo-Casali — retain existing UPV affiliation, logo and email.
4. Georgia Apostolou — retain existing CERTH affiliation, logo and email.

No search bar, filtering chips, contact count or empty-filter controls. Do not invent photos/logos.

### MDC Dashboard and role pages

Home (/) is informational. Dashboard (/demo) is the existing authenticated MDC role-selection page; Provider Area (/demo/provider), Service Discovery (/demo/consumer-search), Admin (/demo/admin-audit) retain current functionality and role restrictions. Do not redesign or modify these pages in this task except if absolutely necessary to restore shared navigation. Help content unchanged.

### Visual requirements

Original MaaSAI light template appearance: white/neutral sidebar, welcome banner and cards, Off-White #F3F2EE page canvas, Warm Sand #D8D1BE supporting surfaces, Ink #262626 text, Brand Orange #E78C3A purposeful highlights/actions, Navy #223F61 appropriate accents only. **No solid navy/blue sidebar or welcome banner.** Preserve Outfit, existing logo/footer, spacing, logical icons, responsiveness, keyboard focus and dark/HMI modes. Brand.js remains design reference, not a navigation item. No broad recoloring or new components.

## 3. Minimal implementation and actual browser acceptance

Inspect only relevant files if changes are necessary: src/layout/AppMenu.js, src/config/routes.js, src/components/home/DashboardContent.js, src/pages/home/Contact.js, and relevant existing SCSS/route guard under mdc-catalog/demo-frontend/. Existing Brand.js for guidance. Do not repeat full frontend audit or implementation. No backend/API relay, Keycloak server/configuration, database, Vercel or Fuseki changes; no live lifecycle writes. UI-only login/navigation verification does not require MDC audience or Preview bypass setup.

Use actual served UI on the confirmed localhost origin. Operator logs in via existing Keycloak form personally; never request passwords/tokens. Verify and record:
- Anonymous Home: correct heading/link, exactly two cards, only Home/Contact/Help, Brand absent, MDC hidden; correct Contact details and no search/filter/count.
- Real signed-in Home: correct MDC heading/link, exactly the same two cards, Home/Contact/Help retained, Dashboard and authorized role links visible, no generic project cards.
- Both states: Home -> Contact -> Home and Home -> Help -> Home work, same four contact cards in correct order. Signed-in Dashboard -> Home works; shared public navigation stays visible. Logout restores public state; anonymous direct protected-route visits remain denied.
- Light visual style and basic responsive behavior. If source changes are needed, run scoped regression tests, lint and build. If no source changes, reuse existing successful checks with actual new runtime evidence; do not unnecessarily repeat the entire test suite.

Provide one verified local URL, exact served Git SHA/worktree/port and concise observed results (sanitized screenshots if feasible). Do not declare PASS based solely on source, fixture tests or previous report. Authenticated checks must use real session; report missing checks honestly. Operator visual acceptance is mandatory before closing task. If awaiting inspection, mark READY FOR OPERATOR REVIEW / PARTIAL, not accepted.

## 4. Deliver and stop

Update existing report (preserve earlier evidence and record rejection/root cause/actual corrections):
`mdc-catalog/docs/reports_phase4/03_MDC_Stage1B_Home_Sidebar_Contact_Refinement_Report.md`

Push only necessary implementation corrections and report to existing Stage 1B branch, no merge/force-push. Report exact files changed (or no source change), SHA, runtime root cause or remaining uncertainty, anonymous/authenticated checks, one URL, and operator acceptance status. Keep 02 report intact. Stop after this UI task. Separate Stage 1B live provider/discovery acceptance remains pending. No further pages, Stage 2, infrastructure or production changes.
