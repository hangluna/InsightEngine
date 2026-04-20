# US-16.2.2 — Execution Agent Child Soft-Flow Request

**Status:** DONE
**Branch:** `feature/insight-engine-us-16.2.2`
**Phase:** 16 — Epic 16.2 (Execution Agent)
**Blocked By:** US-16.2.1 ✅

## Goal

Make the Execution Agent's child soft-flow escalation paths concrete and
testable: explicit triggers for Strategist (decompose) vs Advisory (re-angle),
isolated child state, single-level recursion, return-to-parent contract.

## Acceptance Criteria

| AC  | Statement | Where |
|-----|-----------|-------|
| AC1 | >3 tools tried OR >2 failures → call Strategist for child sub-flow | `execution.agent.md` Child Soft-Flow Request → COMPLEXITY trigger; `references/child-soft-flow.md` |
| AC2 | Wrong angle suspected → call Advisory for alternative approach | `execution.agent.md` → WRONG_ANGLE trigger; `references/child-soft-flow.md` Advisory request format |
| AC3 | Child soft-flow has isolated state, completes, reports back; one level only | `references/child-soft-flow.md` "State Isolation" + "Recursion Limit" sections |

## Files Touched

```
.github/agents/execution.agent.md                     (M, replaced abstract hook with concrete contract + AC mapping)
.github/agents/strategist.agent.md                    (M, added Execution Agent as second caller of CHILD_WORKFLOW_MODE)
.github/agents/references/child-soft-flow.md          (A, full lifecycle reference — triggers, request formats, state isolation, recursion)
docs/runs/insight-engine-us-16.2.2/*                  (A, run artifacts)
docs/product/insight-engine/checklist.md              (M, status PLANNED→IN_PROGRESS→DONE)
```

## Design Notes

- **Mechanical decision rule** (no agent judgement needed): cascade exhausted
  with no useful partial → strategist (decompose); cascade exhausted with
  partials but wrong angle → advisory (re-angle); ≥2 low-confidence → advisory
  first (cheaper than decomposition); else → status=partial.
- **State isolation** uses an in-memory dict scoped to one Execution Agent
  invocation. The run state file (`.workflow-state.yaml`) only ever sees the
  consolidated parent step result, never child intermediate steps.
- **Recursion limit = 1**: a child step that itself fails MUST escalate upward
  with `escalation.target=none`. Prevents runaway tree expansion.
- **Budget accounting**: one strategist call per parent step (the initial
  CHILD_WORKFLOW_MODE call); child step executions consume the regular 8-call
  Execution Agent budget. Advisory escalations count against the standard
  2-call advisory budget.
- **Quality signal after child flow**: `confidence=medium` minimum,
  `suggested_audit=true` always — because child flows arose from a recovery
  path and warrant Auditor verification.

## Validation

- All cross-references resolve (execution.agent.md ↔ references/child-soft-flow.md ↔ strategist.agent.md)
- AC mapping table matches reference content
- No conflicts with existing strategist CHILD_WORKFLOW_MODE contract
- No new dependencies; pure documentation/protocol change

## Commit Message

```
feat(execution): concrete child soft-flow request contract — strategist + advisory paths (US-16.2.2)
```
