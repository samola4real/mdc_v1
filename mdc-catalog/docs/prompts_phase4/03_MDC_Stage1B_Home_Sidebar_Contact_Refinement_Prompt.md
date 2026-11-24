# Stage 1B — Focused home, sidebar and contact refinement

## Objective and scope

Apply the operator-approved corrections to the EXISTING MaaSAI demo frontend. This is a small UI refinement, not a new frontend or broader Stage 1B implementation. Keep current layout, reusable cards, Keycloak, roles, canonical API integration and existing functionality. No backend, database, Fuseki, Vercel, Keycloak server or unrelated page changes.

Continue `phase4/stage1b-frontend-integration` from the existing task worktree; reviewed head `4843ebf19ca047894c96f4cf1901397851a25bd2`, implementation `8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6`. Fetch latest refs and verify ancestry/status before changes; if newer work exists preserve it. Read this prompt from main. Do not restart from main or overwrite original checkout's unrelated edits. Do not repeat the frontend audit or Stage 1B implementation.

Focus on `mdc-catalog/demo-frontend/`:
- `src/layout/AppMenu.js`, `src/config/routes.js`, existing route guard only if necessary.
- `src/components/home/DashboardContent.js` (root Home via `src/pages/index.js`).
- `src/pages/home/Contact.js`.
- Relevant existing SCSS for sidebar, welcome banner and cards. Inspect `src/pages/home/Brand.js` for official brand guidance. Read only other directly required files.

## 1. Sidebar and MDC section (operator sections 1 and 2)

- Before login: show only Home, Contact, Help with existing logical icons. Remove Brand from navigation (retain Brand.js as design reference). Hide the entire MaaS Dynamic Catalogue menu group, including Dashboard, until Keycloak authentication completes. Hide generic Workspace/template menu items; do not delete their source pages.
- After login: retain Home, Contact, Help and expose the existing MaaS Dynamic Catalogue group. Preserve existing role selection and role-specific visibility/guards for Provider Area, Service Discovery and Demo Admin. Do not give new privileges or show unauthorized actions.
- Protect `/demo` itself as authenticated, not just the three child routes; use existing route access mechanism. Verify direct URL access is denied for anonymous users and existing role guards remain in force. Public Home, Contact and Help stay available in both states. Preserve existing topbar login/logout. Handle auth initialization without flashing protected content.

## 2. Welcome banner (section 3)

Reuse DashboardContent and the existing banner; make heading, text and More info destination conditional on authenticated state.

**Before login**
Heading: Welcome to MaaSAI
Text: MaaSAI advances Manufacturing as a Service by enabling connected, intelligent and collaborative manufacturing ecosystems. The project supports digital manufacturing services, interoperability and collaboration between manufacturing providers and consumers.
More info: https://documentation.maasai-srv.cigip.upv.es/

**After login**
Heading: Welcome to MaaS Dynamic Catalogue
Text: The MaaS Dynamic Catalogue (MDC) enables manufacturing providers to publish, manage and update their manufacturing services and capabilities. Through ontology-based data harmonization and semantic service discovery, MDC supports the identification of suitable manufacturing services based on consumer requirements.
More info: https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/

Use an appropriate information or external-link icon rather than the existing plus sign.

## 3. Information cards (section 4)

Both before and after login show only two existing-style cards:
- Contact — Contact the MDC development team for technical information and enquiries. Link to /home/Contact; envelope/contact icon.
- Project Website — Explore the MaaSAI project, its objectives, activities and results. Link to https://maasai-project.eu/; globe/external-link icon.

Remove duplicate Sign In and Help cards and generic authenticated Create a Project, View your Projects and Register a Resource cards from Home. No new cards or redesign. Keep existing topbar login, sidebar Help and separate MDC menu.

## 4. Contact page

Reuse existing card rendering and current logo assets (fallback initials if no TAU logo). Simplify: remove search field, filtering chips, count and unnecessary filter/empty-state UI. Retain practical email links and existing card layout. Add two Tampere University — FAST-Lab contacts before the existing project contacts:
- Jose Martinez Lastra — Unit Head — jose.martinezlastra@tuni.fi — group homepage https://research.tuni.fi/fast/
- Samuel Afolaranmi — Developer, MaaS Dynamic Catalogue — samuel.afolaranmi@tuni.fi — MDC documentation https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/

Preserve Miguel Angel Mateo-Casali's existing details and other existing contact records. The reviewed source also contains Georgia Apostolou; do not silently remove her because operator did not request deletion of that entry. Report this decision. Use logical existing icons, no invented portraits or external assets.

## 5. Visual correction — original MaaSAI template light styling

Operator explicitly rejects navy/blue-filled sidebar and welcome banner. Restore the original template's light/neutral presentation for these two areas, not the dark navy block from the earlier illustrative proposal. Compare only relevant original styles at committed frontend baseline `06df31c` if needed. Use existing white/neutral card surfaces, Off-White (#F3F2EE) and Warm Sand (#D8D1BE), Ink (#262626) text; Brand Orange (#E78C3A) for purposeful highlights/actions/focus. Brand Navy (#223F61) remains an official colour for appropriate accents/text, not a solid background for the sidebar or welcome banner. Do not impose a new theme or broadly recolour unrelated pages/topbar. Retain Outfit, existing spacing/layout, theme selector and accessible contrast/focus; preserve dark/HMI modes if present. Remove only incompatible sidebar-specific white-text overrides when restoring the light background. Use Brand.js as design guidance rather than adding a new Brand page. Keep changes small and use existing icons/SCSS variables.

## 6. Verification and report

Run scoped regression tests, lint and build from the existing worktree. Inspect Home and Contact at localhost in light theme; verify exact links, public sidebar/cards, non-blue sidebar/banner, protected /demo and child routes, and no generic workspace cards/menu. Verify authenticated Home/sidebar/role behavior and logout using real authorized session if available. Do not fabricate login or weaken guards; mark authenticated checks pending if credentials unavailable. Do not repeat backend lifecycle writes for this visual task. The separate Stage 1B live authenticated acceptance remains pending until independently passed.

Commit only focused frontend changes and report; push to existing Stage 1B branch (no merge or force-push). Report path:
`mdc-catalog/docs/reports_phase4/03_MDC_Stage1B_Home_Sidebar_Contact_Refinement_Report.md`

Report verdict, exact files changed, implementation/report SHAs, public/authenticated visual evidence or honest pending status, lint/build/regression results, local worktree path/startup command, and unresolved items. Keep the earlier 02 report intact. Stop after this small UI task; no Help-page content redesign, other pages, Stage 2, production deployment or additional infrastructure.
