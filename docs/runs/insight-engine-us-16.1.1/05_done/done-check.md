# Phase 5 — Done Check

## Definition of Done

| Item | Status |
|------|--------|
| All ACs satisfied (AC1, AC2, AC3) | ✅ |
| Solution design produced | ✅ `00_analysis/solution-design.md` |
| Spec produced | ✅ `01_spec/spec.md` |
| Task plan produced | ✅ `02_tasks/tasks.md` |
| Implementation complete | ✅ T-001 → T-005 |
| Static checks pass (`get_errors` clean) | ✅ |
| No new dependencies introduced | ✅ |
| RULE.md compliance maintained | ✅ |
| Vietnamese user-facing strings only | ✅ |
| Out-of-scope items not touched | ✅ (no other skills changed) |

## Files Changed

| File | Change |
|------|--------|
| `.github/skills/search/SKILL.md` | Insert Step 2.5; update References list; bump version 1.0 → 1.1 |
| `.github/skills/search/references/tool-availability-probe.md` | NEW — full probe algorithm + silent-failure contract |
| `docs/product/insight-engine/checklist.md` | Lock + (will be) mark DONE for US-16.1.1 |
| `docs/runs/insight-engine-us-16.1.1/.workflow-state.yaml` | Workflow state |
| `docs/runs/insight-engine-us-16.1.1/00_analysis/work-description.md` | Work description |
| `docs/runs/insight-engine-us-16.1.1/00_analysis/solution-design.md` | Phase 0 design |
| `docs/runs/insight-engine-us-16.1.1/01_spec/spec.md` | Phase 1 spec |
| `docs/runs/insight-engine-us-16.1.1/02_tasks/tasks.md` | Phase 2 task plan |
| `docs/runs/insight-engine-us-16.1.1/04_tests/test-notes.md` | Phase 4 verification |
| `docs/runs/insight-engine-us-16.1.1/05_done/done-check.md` | This file |

## Commit Message

```
feat(search): add tool availability probe before primary search execution (US-16.1.1)

- Insert Step 2.5 (Tool Availability Probe) before Step 3 in search/SKILL.md
- Add references/tool-availability-probe.md with full decision tree
- Document silent-failure contract: never surface Tavily/auth UI to user
- Define fallback-tier hook for US-16.1.2 (Playwright stealth)
- Bump search skill version 1.0 → 1.1
- Add Phase 0-5 workflow artifacts under docs/runs/insight-engine-us-16.1.1/
```

## Downstream Impact

Unblocks: US-16.1.2 (Playwright stealth fallback search tier).

## Self-Review Verdict

PASS — story delivered per spec, no scope creep, no regressions expected.
