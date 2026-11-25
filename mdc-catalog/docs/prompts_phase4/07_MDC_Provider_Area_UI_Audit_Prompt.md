# Task 07 — Provider Area UI audit (read-only)

**Objective:** Establish exactly how the current Provider Area works before discussing redesign. Produce an extensive, evidence-based audit of this UI only; do not implement improvements.

## Scope

Use the permanent checkout `C:/Users/Elahi/Desktop/mdc_v1`. Fetch latest main and inspect the actual local source, preserving all uncommitted changes. Record the reviewed SHA and relevant local differences. Limit inspection to `mdc-catalog/demo-frontend` Provider Area (`/demo/provider`), its rendered components, form state, helpers, catalogue-filter/service clients and directly relevant payload mappings. Trace adjacent code only when needed to explain Provider Area behavior. No whole-repository, backend, infrastructure or authentication audit.

## Audit requirements

1. **Component inventory and rendering hierarchy.** Map the page → Provider panel → sections/subcomponents, in actual screen order. For every section list rendered fields, input type, default, options/source, requiredness, editability, units and show/hide/disable conditions. Distinguish explicit UI checks, backend validation assumptions and unknowns. Cover provider information, offering information, additional offering fields, capability fields, custom capability fields, lookup/table, payload preview, result panel and action buttons.
2. **Interaction and dependency matrix.** Trace each controlling input through state changes, dependent rendering and payload construction. In particular, enumerate every available Part family and its supported part types, automatic service category, family-specific fields, and part-type-specific fields. Compare no part type, one part type and multiple part types (including block + roller, gear and shaft examples). Explain what happens when selection changes, fields become hidden, or a previously selected item is removed. Include material selection (zero/one/multiple materials), grade input, processes, support status, certifications, custom field additions/removals, duplicate names and repeated values. Identify any hidden/stale state, disappearing values, unsupported combinations or silent overwrites.
3. **Lifecycle modes and data flow.** Explain Register New Provider, Update Existing Provider, selecting an offering, Add offering, validation, save provider/save offering and deletion: triggers, state transitions, hydration/reload, edit restrictions, enablement, request and response handling. Map each UI field to its canonical JSON path or custom map, and identify any data not rendered, loss of fidelity on round trip, or differences between create and update. Distinguish controlled vocabulary from flexible provider-supplied data. Include actual endpoint/method names only as relevant to UI behavior.
4. **Evidence and critical findings.** Inspect source and, if available, use the already running local frontend for read-only observation. Use offline form/payload examples to demonstrate meaningful selection transitions and round trips; no actual registration, update or deletion, no changes to test fixtures or application code. Identify concrete usability and correctness problems with severity, reproduction, source file/line references and impact on providers. Separate confirmed source behavior, observed browser behavior and unverified assumptions. Include concise illustrative current-state payload snippets for gear, shaft and metal part; do not invent backend vocabulary or capabilities.

## Deliverable

Write one self-contained report at `mdc-catalog/docs/reports_phase4/07_MDC_Provider_Area_UI_Audit_Report.md` containing:
- Executive summary and current screen/component tree.
- Complete field inventory and dependency/rendering matrices.
- Current-state user flows and UI-to-payload mapping.
- Concrete findings, edge cases and open questions for the subsequent redesign discussion.

Use tables and simple diagrams where they clarify relationships. Report facts and problems, not a proposed redesign. No application changes, new deployment, dependency install/upgrade, worktree creation or infrastructure changes. Keep the existing local configuration and secrets intact. If live read-only checks are useful, reuse the standing approval for the saved server-only bypass at the pinned Stage 1 Preview host; respect mandatory runtime approvals and omit credentials from evidence. Static evidence is sufficient when browser access is unavailable; label that limitation. Commit/push only the audit report (follow existing branch rules; do not include unrelated local edits). Return report link, reviewed SHA, principal findings and verification limitations.
