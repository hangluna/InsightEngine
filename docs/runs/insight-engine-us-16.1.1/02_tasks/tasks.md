# Phase 2 — Task Plan

| Task ID | Title | Files | Depends On |
|---------|-------|-------|------------|
| T-001 | Create probe reference doc | `.github/skills/search/references/tool-availability-probe.md` | — |
| T-002 | Insert Step 2.5 in SKILL.md | `.github/skills/search/SKILL.md` | T-001 |
| T-003 | Update SKILL.md References list to include the new doc | `.github/skills/search/SKILL.md` | T-002 |
| T-004 | Add changelog/version note in SKILL.md frontmatter (bump version to 1.1) | `.github/skills/search/SKILL.md` | T-003 |
| T-005 | Verify Markdown validity & cross-links | (read-only) | T-004 |

## Sequencing

Sequential. T-001 first (creates the reference target), then SKILL.md edits in
T-002 → T-003 → T-004, then T-005 verification.

## Self-Review Notes

- Tasks are minimal and granular.
- Each task has clear file targets.
- T-005 is the local "static gate" before Phase 4.
