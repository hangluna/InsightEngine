# Phase 0 — Solution Design

## Problem

Search skill currently calls `vscode-websearchforcopilot_webSearch` blindly. When the
extension lacks a Tavily API key, an auth popup blocks non-tech users with no recovery
path. There is no decision layer between "user asks to search" and "primary tool
invoked".

## Design Decision

Insert a **probe step** as `Step 2.5` in `search/SKILL.md`, immediately before
`Step 3: Execute Search & Fetch`. The probe is a **decision procedure executed by
Copilot** (not a Python script), because Copilot is the agent that selects which tool
to invoke.

### Probe Decision Tree

```
START
  │
  ├─ Is there a session-level "primary_unavailable" flag set?
  │     ├─ YES → mark UNAVAILABLE, skip probe, go to fallback tier
  │     └─ NO  → continue
  │
  ├─ Has the user (in this session) previously declined Tavily auth,
  │   or has a previous search call surfaced a Tavily/auth error?
  │     ├─ YES → set session flag, mark UNAVAILABLE
  │     └─ NO  → continue
  │
  ├─ Attempt primary tool with a minimal lightweight query.
  │   IF the call returns results without raising an auth/config error:
  │     → mark AVAILABLE, cache decision for the rest of the session
  │   IF the call surfaces an auth popup, returns config error,
  │   or throws an "extension not configured" error:
  │     → set session flag "primary_unavailable: true"
  │     → mark UNAVAILABLE
  │     → swallow the error silently (no user-facing message about Tavily/auth)
  │
END → return AVAILABLE | UNAVAILABLE
```

### Fallback Contract (post-probe)

- If `AVAILABLE` → existing Step 3 runs unchanged (calls primary tool, fetches URLs).
- If `UNAVAILABLE` → call into the **fallback tier** (placeholder for US-16.1.2).
  - Until US-16.1.2 lands, the fallback path: log a single internal note in the run
    folder, return a graceful "Không tìm thấy kết quả tìm kiếm" message to the user.
  - No Tavily/auth/config terminology is exposed to the user.

### Why No Python Script?

The probe is a Copilot-level decision (pick which tool to call). Encoding it as a
script would require Copilot to call the script first, then call the search tool —
which doubles tool calls and adds zero value. A documented decision procedure that
Copilot follows is sufficient and consistent with how the rest of `search/SKILL.md`
operates (instructions, not orchestration code).

## Files to Change

| File | Change Type | Reason |
|------|-------------|--------|
| `.github/skills/search/SKILL.md` | EDIT | Insert Step 2.5 before Step 3; add probe summary to References list |
| `.github/skills/search/references/tool-availability-probe.md` | CREATE | Full probe algorithm, rationale, rollback notes |

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Probe falsely flags a working primary as unavailable | Low | Default: AVAILABLE unless explicit signal; cache only after positive failure |
| Silent fallback hides real configuration issues from devs | Medium | Internal note logged in run folder so devs can see what happened; user message stays friendly |
| Future US-16.1.2 hook signature differs from what's stubbed here | Low | Hook is described abstractly ("call fallback tier"); concrete signature deferred to US-16.1.2 |

## Self-Review Notes

- All 3 ACs covered: probe (AC1), branch on result (AC2), silent UX (AC3).
- Out-of-scope items not touched: no Playwright/HTTP fallback implementation, no other
  skills modified.
- Documentation-only change — no test scaffolding required, no dependency changes.
