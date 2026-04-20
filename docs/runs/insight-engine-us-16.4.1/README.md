# US-16.4.1 — Adaptive Re-Planning on Auditor Failure

**Status:** DONE
**Branch:** `feature/insight-engine-us-16.4.1`
**Phase:** 16 — Epic 16.4
**Blocked By:** US-16.2.1 ✅
**Blocks:** US-16.5.1

## Goal

Replace brute-force same-method retry on Auditor FAIL with a single
Advisory + Strategist (replan) + Execution-retry cycle. Hard budget = 1+1+1
per failed step. Distinct from US-16.2.2's pre-Auditor cascade-exhaustion path.

## Acceptance Criteria

| AC  | Statement | Where met |
|-----|-----------|-----------|
| AC1 | On failure (cascade exhausted OR auditor <60 after 2 attempts), Execution Agent calls Advisory with what was tried, what failed, original requirement | `references/adaptive-replanning.md` Hard Triggers + Advisory Request Format; `execution.agent.md` step_6_audit_feedback_replan |
| AC2 | Advisory returns 2-3 alternative approaches with rationale | Advisory request CONSTRAINTS block requires "2-3 alternatives, each must differ"; advisory.agent.md returns PERSPECTIVES + RECOMMENDATION |
| AC3 | Execution Agent picks best alternative and executes with new approach | "Forbidden: Same-Method Retry" rule + Strategist replan format (single replacement step) + execution loop GOTO step_6 → step_2 with new plan |
| AC4 | At most 1 Advisory + 1 Strategist call per failed step. Budget respected. | "Budget (Hard Cap)" — explicit `PER_FAILED_STEP` 1+1+1 table + `PER_PIPELINE_RUN` inheritance |

## Files Touched

```
.github/agents/references/adaptive-replanning.md      (A, full contract — triggers, formats, budget, US-16.2.2 vs US-16.4.1 disambiguation)
.github/agents/execution.agent.md                     (M, step_6_audit_feedback_replan + Adaptive Re-Planning section + AC mapping)
.github/RULE.md                                       (M, RULE-9 Failure Handling subsection now references both replan docs)
docs/runs/insight-engine-us-16.4.1/*                  (A, run artifacts)
docs/product/insight-engine/checklist.md              (M, status PLANNED→IN_PROGRESS→DONE)
```

## Design Notes

- **US-16.2.2 vs US-16.4.1 disambiguation** is critical and explicit in both
  reference docs. US-16.2.2 = pre-Auditor (cascade exhausted, never reached
  Auditor). US-16.4.1 = post-Auditor (output produced but scored low). A single
  failed step uses AT MOST one of the two — never both.
- **Score threshold logic**: `<60` triggers replan after a single attempt
  (small fixes unlikely to recover). `60-79` gets one same-method pivot first
  (existing RULE-2 behaviour), only escalating to replan after the second
  consecutive sub-80.
- **Budget integration**: PER_FAILED_STEP cap (1+1+1) is sufficient at the step
  level. PER_PIPELINE_RUN inherits the existing advisory=2 / strategist=5
  caps shared with child_workflow mode. When the per-pipeline budget exhausts
  before per-step, deliver partial (RULE-8).
- **Forbidden same-method retry** is stated three times (in
  adaptive-replanning.md, execution.agent.md, RULE-9) for redundancy because
  this is the single most important behaviour change of US-16.4.1.

## Validation

- All cross-references resolve (adaptive-replanning.md ↔ execution.agent.md ↔ RULE.md ↔ child-soft-flow.md)
- Budget arithmetic: 1+1+1 per step ≤ 2 advisory + 5 strategist per pipeline (consistent)
- No regressions to existing RULE-9 sections — only the Failure Handling subsection extended
- No conflicts with auditor.agent.md scoring (uses existing < 60 / < 80 thresholds)

## Commit Message

```
feat(execution+rule): add adaptive auditor-driven re-planning contract (US-16.4.1)
```
