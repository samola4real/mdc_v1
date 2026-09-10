# Frontend GitHub-to-GitLab Release Mapping

## Repository boundary

Personal GitHub is the controlled development location after the sanitized snapshot import is approved and merged. MaaSAI GitLab retains the original frontend history and remains the official release destination.

No permanent GitLab remote is required in the normal `mdc_v1` working copy.

## Path mapping

| GitHub source | GitLab destination | Default release treatment |
|---|---|---|
| `mdc-catalog/demo-frontend/**` | `subsystem/frontend/**` | Synchronize approved application files |
| Selected sanitized integration files | Their documented original GitLab locations | Synchronize only with explicit scope approval |
| `mdc-catalog/docs/Demo_Frontend/**` | None | GitHub-only documentation; exclude by default |
| Local `.env*`, credentials, editor files, dependencies, caches, builds and logs | None | Always exclude |

The snapshot provenance README may remain in GitHub. Its publication to the GitLab product tree requires separate approval.

## Controlled release procedure

1. Select a reviewed GitHub source commit and define the exact release scope.
2. Obtain approval to prepare a GitLab release candidate.
3. Create a fresh temporary checkout of the MaaSAI GitLab frontend repository.
4. Verify its expected base commit, clean status, branch, and official remote.
5. Create a GitLab release branch; never work directly on GitLab `main`.
6. Synchronize only approved application paths according to the mapping above.
7. Preserve unrelated GitLab files and exclude GitHub-only documentation and all local or sensitive material.
8. Run a secret scan that reports findings without exposing credential values.
9. Install from the approved lockfile only when authorized, then run the applicable lint, build, test, and browser/API gates.
10. Inspect `git status`, every changed path, and the complete Git diff.
11. Record the GitHub source commit and proposed GitLab release commit in a release report.
12. Obtain explicit approval for the concrete GitLab commit and push.
13. Push the release branch only and use the normal GitLab merge-review process.
14. Record the merged GitLab commit in GitHub release documentation.
15. Remove the temporary checkout and transient local configuration according to the approved cleanup process.

Never force-push, rewrite or replace GitLab history, merge unrelated histories, or use direct subtree publication.
