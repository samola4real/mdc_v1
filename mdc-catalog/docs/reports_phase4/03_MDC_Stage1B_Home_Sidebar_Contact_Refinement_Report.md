# Stage 1B — Home, sidebar and Contact refinement

**Verdict — PARTIAL.** The approved light-theme refinement is implemented. Home, Contact, Help and the four anonymous MDC redirects passed in a local browser. The live Keycloak login form opened. A signed-in session was unavailable, so the authenticated Home, role-specific navigation and logout checks are pending.

| Reference | Value |
| --- | --- |
| Date | 2026-11-24 |
| Refreshed `origin/main` | `715c6a91472145d9811e4ce4f5a314899ad23654` |
| Stage 1B branch | `phase4/stage1b-frontend-integration` |
| Reviewed starting head | `4843ebf19ca047894c96f4cf1901397851a25bd2` |
| Earlier Stage 1B implementation | `8252d2abaf8683a63e9b6c598fcd40cd50bdb7b6` |
| Refinement implementation | [`ca3853cfb1d273eb4a10efa908ac11d452e37863`](https://github.com/samola4real/mdc_v1/commit/ca3853cfb1d273eb4a10efa908ac11d452e37863) |
| Report commit | [GitHub report history](https://github.com/samola4real/mdc_v1/commits/phase4/stage1b-frontend-integration/mdc-catalog/docs/reports_phase4/03_MDC_Stage1B_Home_Sidebar_Contact_Refinement_Report.md). The delivery message records the exact commit and its permalink. |

The fetched Stage 1B branch matched the reviewed head in the existing clean worktree. The implementation continued from that head. The prior integration report remains available at its original commit. [Refinement prompt at fetched main](https://github.com/samola4real/mdc_v1/blob/715c6a91472145d9811e4ce4f5a314899ad23654/mdc-catalog/docs/prompts_phase4/03_MDC_Stage1B_Home_Sidebar_Contact_Refinement_Prompt.md), [previous Stage 1B report](https://github.com/samola4real/mdc_v1/blob/4843ebf19ca047894c96f4cf1901397851a25bd2/mdc-catalog/docs/reports_phase4/02_MDC_Stage1B_Existing_Frontend_Integration_Report.md)

## Approved changes

- **Sidebar and access.** The public menu contains Home, Contact and Help, with the existing home, envelope and help icons. Brand.js remains the design reference and Workspace pages remain in the app. When Keycloak initialization completes with an authenticated session, the same navigation includes the MDC group and Dashboard. The three role links still require an authorized selected role. `/demo` now uses the same authentication requirement as its three child routes. The implementation reuses the topbar login and logout, demo role selection and `DemoRoleGuard` enforcement.
- **Home.** The existing banner shows the approved MaaSAI welcome for visitors and selects the approved MaaS Dynamic Catalogue welcome for authenticated users. More info uses the information icon and the link for the current state. Both states share two existing-style cards, Contact and Project Website, with the envelope and globe icons. [MaaSAI documentation](https://documentation.maasai-srv.cigip.upv.es/), [MDC documentation](https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/), [MaaSAI project website](https://maasai-project.eu/)
- **Contact.** Jose Martinez Lastra and Samuel Afolaranmi appear first, with the requested Tampere University — FAST-Lab affiliation, roles, email links and respective website links. The existing card falls back to TAU initials because the current assets contain no TAU logo. Miguel Angel Mateo-Casali retains his existing UPV details and logo. Georgia Apostolou was deliberately retained with her existing CERTH details and logo because the refinement did not request removing her entry. The page shows the four cards directly and retains the existing mailto and copy-email controls. [FAST-Lab homepage](https://research.tuni.fi/fast/), [MDC documentation](https://documentation.maasai-srv.cigip.upv.es/solutions/mdc/)
- **Light styling.** The relevant template styles at `06df31c` used white sidebar and welcome surfaces. The run restored the white sidebar and retained the white banner, Off-White canvas, Warm Sand active link, Ink heading and Ink on Orange for the CTA. Navy serves as an accent and participates in the keyboard focus ring. Outfit, the card treatment and the theme selector use the existing implementation. [Brand.js reference](../../demo-frontend/src/pages/home/Brand.js)

## Verification

| Check | Evidence |
| --- | --- |
| Desktop Home | Edge at 1440 px showed exactly Home, Contact and Help in the sidebar, `Welcome to MaaSAI` with the requested text, the exact More info destination, and the two requested card titles, descriptions and links. The existing Login control was visible. |
| Template palette | Computed sidebar and banner `#FFFFFF`, page `#F3F2EE`, selected sidebar row `#D8D1BE`, heading `#262626` and CTA `#E78C3A` with `#262626` text. Edge loaded Outfit. Keyboard Tab focused More info and showed the existing 2 px Navy and 4 px Orange ring. |
| Dark and HMI | The existing selector cycled through dark, HMI and back to light. The sidebar and banner used `#1A1F28` and `#1C212B` in dark, and `#0A0A0A` and `#0F0F0F` in HMI. |
| Contact | The Home card opened `/home/Contact`. Edge verified the four names in order, their affiliations, two FAST-Lab roles, four exact mailto links, the two new external link destinations, visible copy controls, TAU initials and both loaded logos. Search, filtering, contact count and empty-filter controls were absent. |
| Mobile and Help | Home and Contact used one card column at 390 px with no horizontal page overflow. Help opened publicly from its sidebar link. |
| Anonymous route protection | Four of four direct visits (`/demo`, `/demo/provider`, `/demo/consumer-search`, `/demo/admin-audit`) returned to Home. The browser observed no protected content or MDC navigation during those visits and recorded zero local JavaScript exceptions. |
| Keycloak and authenticated state | Login opened the real MAASAI Keycloak password form with client `myClient`, S256 PKCE and a `localhost:3001` return URL. The signed-in welcome and target link, authenticated sidebar, role access or denial, and logout need a real authorized session. |
| Regression | All 8 existing Stage 1B tests passed. The scoped route-policy probe passed all 7 route cases and 4 standalone role assertions. |
| Lint and build | Both passed on Node 22.15.0 and npm 10.9.2. The existing hook-dependency, manual stylesheet and Browserslist warnings were observed. |

Desktop screenshots were inspected locally and the browser observations above capture their relevant evidence. The separate Stage 1B authenticated lifecycle acceptance remains pending. This refinement used browser-side page and route checks.

## Local inspection

The verified build is running on loopback at [Home](http://localhost:3001/) and [Contact](http://localhost:3001/home/Contact). Port 3000 already had a listener, so the refinement uses port 3001. The local build server served both pages, styles and assets despite Next.js printing its standalone packaging warning on startup.

For a fresh development run when port 3001 is free, use the existing Stage 1B worktree.

```powershell
Set-Location -LiteralPath 'C:/Users/Elahi/AppData/Local/Temp/mdc-stage1b-20261124-4b9fc439/mdc-catalog/demo-frontend'
npm run dev -- --hostname 127.0.0.1 --port 3001
```

## Exact implementation files

Paths are relative to `mdc-catalog/demo-frontend/`.

| File | Change |
| --- | --- |
| `src/layout/AppMenu.js` | Public links, authenticated MDC group and existing selected-role filtering |
| `src/config/routes.js` | Authentication requirement for the MDC Dashboard |
| `src/components/home/DashboardContent.js` | Auth-dependent welcome and two shared information cards in the existing layout |
| `src/pages/home/Contact.js` | FAST-Lab contacts, external links, and removal of filters and count |
| `src/styles/layout/_main.scss` | Neutral light sidebar surface from the existing card background |
| `src/styles/layout/_menu.scss` | Ink navigation text, Warm Sand selection and Orange accent in light mode |
| `src/styles/layout/_content.scss` | Light Home action styling and focus, Contact link styling, and removal of unused filter styles |
| `src/styles/layout/_responsive.scss` | Existing responsive card collapse with stale card and filter rules removed |
