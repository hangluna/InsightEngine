# Child Soft-Flow Lifecycle (Execution Agent ↔ Strategist / Advisory)

> Implements **US-16.2.2**. Concrete contract for the child soft-flow request
> hooks declared in `execution.agent.md` (US-16.2.1).

## What is a Child Soft-Flow?

A **child soft-flow** is a small, isolated 2–5 step sub-workflow that the
**Execution Agent** spawns when a single parent step proves too complex or its
tool cascade is exhausted. The child runs in **isolated state**, completes, and
returns a single consolidated result to the parent step. It never modifies the
parent's pipeline state directly.

```
Parent Step (Execution Agent)
   │ tool cascade exhausted (>3 tools tried, >2 low-quality results)
   ▼
runSubagent(strategist, CHILD_WORKFLOW_MODE) ─► returns child plan (2–5 steps)
   │
   ▼
Execute child steps with isolated state
   │ all child steps complete
   ▼
Consolidated result returned to parent → parent step status = success
```

## Two Escalation Paths

| Path | Target | Trigger | Returns |
|------|--------|---------|---------|
| **Decompose** | `strategist` (CHILD_WORKFLOW_MODE) | Step is *too big*: cascade exhausted, complexity high | A 2–5 step child plan |
| **Re-angle** | `advisory` | Strategy seems *wrong*: tools succeed but quality stays low | 2–3 alternative approaches with rationale |

The Execution Agent picks **at most one** escalation path per parent step. The
choice is mechanical:

```yaml
DECISION:
  if cascade_exhausted AND no_partial_result_was_useful:
    target = strategist  # decompose
  elif cascade_exhausted AND partial_results_exist_but_wrong_angle:
    target = advisory    # re-angle
  elif quality_signal.confidence == "low" for >=2 attempts:
    target = advisory    # re-angle (try different approach before decomposing)
  else:
    target = none        # return status=partial, let Auditor decide
```

## Trigger Thresholds (concrete)

```yaml
COMPLEXITY_TRIGGER (→ strategist):
  - tools_tried >= 3 from the cascade AND no tool produced success_criteria match
  - OR: 2+ consecutive attempts returned quality_signal.confidence = "low"
  - OR: parent_context.complexity_hint == "high" AND first attempt failed

WRONG_ANGLE_TRIGGER (→ advisory):
  - quality_signal.notes mention "off-topic", "wrong angle", "irrelevant" 2+ times
  - OR: result_size > 0 but success_criteria semantically not satisfied
  - OR: caller skill explicitly hints "consult advisory if first angle fails"
```

## Request Format

### Strategist (CHILD_WORKFLOW_MODE)

```python
runSubagent(
    agentName="strategist",
    description="Generate child soft-flow for failed step",
    prompt="""
CHILD_WORKFLOW_MODE: true

PARENT_STEP: {soft_flow_step.step_id}
PARENT_PURPOSE: {soft_flow_step.step_purpose}
SUCCESS_CRITERIA: {soft_flow_step.success_criteria}

ATTEMPTED_TOOLS:
- {tool_1}: {outcome_1}
- {tool_2}: {outcome_2}
- {tool_3}: {outcome_3}

FAILURE_PATTERN: {one-line diagnosis}

CONSTRAINTS:
- Child plan MUST be 2–5 steps (no nested children allowed)
- Each step MUST be independently executable
- Total wall time budget: <= 3× the parent step's original budget
"""
)
```

Strategist returns the standard `CHILD_WORKFLOW_FOR / CHILD_STEPS / STEPS / MERGE_STEP`
block (see `strategist.agent.md` Child Workflow Mode section).

### Advisory

```python
runSubagent(
    agentName="advisory",
    description="Alternative angle for stuck step",
    prompt="""
QUESTION: How should I re-approach this step?
SEVERITY: moderate

CURRENT_APPROACH: {summary of attempted angle}
DEAD_END_OBSERVATION: {why current angle is exhausted — 1-2 lines}

OPTIONS_TO_RANK:
1. Switch source/tool to {alternative_1}
2. Switch source/tool to {alternative_2}
3. Re-frame the question as {alternative_3}
"""
)
```

Advisory returns the standard `PERSPECTIVES / RECOMMENDATION / CONFIDENCE` block.
Execution Agent applies the recommendation if `CONFIDENCE >= 0.7`; otherwise
returns `status=partial` to Auditor.

## State Isolation

Child soft-flow state MUST NOT leak into the parent pipeline state file. Use a
temporary in-memory dict inside the Execution Agent invocation:

```python
child_state = {
    "parent_step_id": soft_flow_step.step_id,
    "child_steps": [],          # filled as each child step completes
    "child_results": {},        # keyed by child step name
    "started_at": iso_timestamp(),
}
```

After child workflow completes, **only the consolidated result** is written to
the parent return object:

```yaml
RETURN:
  status: success
  result:
    data: <consolidated child result>
    tool_used: child_soft_flow
    attempts: [<original parent attempts>, child_workflow_summary]
  quality_signal:
    confidence: medium  # child workflows always ship at confidence=medium minimum
    suggested_audit: true  # always audit results from child flows
    notes: "Child soft-flow with N steps used to recover from cascade exhaustion"
```

The child's intermediate steps and tool choices are summarised in `attempts` for
post-mortem auditability but are not persisted to the run state file.

## Recursion Limit

**Hard rule:** child soft-flows are **one level only**. A child step that itself
fails MUST NOT spawn another child. If a child step's tool cascade also exhausts:

```yaml
ON_CHILD_STEP_CASCADE_EXHAUSTED:
  status: failed
  escalation:
    needed: true
    target: none
    reason: "Child soft-flow step exhausted; recursion limit reached"
  # Auditor + Orchestrator decide whether to mark parent task FAILED.
```

## Budget Accounting

Each child soft-flow counts against the strategist budget at most **once**
(the initial CHILD_WORKFLOW_MODE call). Subsequent child step executions
consume the Execution Agent's regular 8-call budget.

Each advisory escalation counts against the standard 2-call advisory budget.

## Acceptance Criteria Mapping (US-16.2.2)

| AC | Requirement | Where met |
|----|------------|-----------|
| AC1 | Step >3 tools tried OR >2 failures → call Strategist for child sub-flow | `COMPLEXITY_TRIGGER` table + `Request Format → Strategist` |
| AC2 | Wrong-angle suspected → call Advisory for alternative | `WRONG_ANGLE_TRIGGER` table + `Request Format → Advisory` |
| AC3 | Child soft-flow has isolated state, completes, reports back | `State Isolation` section + `Recursion Limit` rule |
