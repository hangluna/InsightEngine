# Work Description — US-16.1.1

## 📋 Summary

| Aspect | Value |
|--------|-------|
| Work Type | FEATURE |
| Title | Tool availability probe before search execution |
| User Story | US-16.1.1 |
| Affected Roots | InsightEngine |
| Base Branch | main |
| Branch | feature/insight-engine-us-16.1.1 |

---

## Flow 1 Context

| Field | Value |
|-------|-------|
| User Story ID | US-16.1.1 |
| Product | insight-engine |
| Checklist Path | docs/product/insight-engine/checklist.md |
| Status | IN_PROGRESS |
| Phase | 16 — Agent-Centric Architecture & Tool-Agnostic Search |
| Epic | 16.1 — Tool-Agnostic Search Cascade |

---

## Problem Statement

The InsightEngine `search` skill currently calls `vscode-websearchforcopilot_webSearch` as
the primary search tool (per `search/SKILL.md` Step 3). This tool is provided by the
`vscode-websearchforcopilot` extension and silently triggers a **Tavily auth popup** the
first time it is invoked in a session if no API key is configured. For non-tech users,
this popup is a hard blocker: they don't know what Tavily is, can't get an API key, and
the pipeline appears to hang.

The skill's existing 3-tier cascade only covers **URL fetching** (after results are
obtained). There is no cascade for the **search call itself** — if the primary tool is
unavailable (popup, missing key, extension disabled), the skill has no fallback and
surfaces the error directly to the user.

---

## Expected Outcome

The `search` skill performs a **lightweight availability probe** before invoking
`vscode-websearchforcopilot_webSearch`. If the probe indicates the tool is unavailable
(no API key configured, extension absent, prior failure recorded), the skill silently
moves to the next tier (Playwright stealth — implemented in US-16.1.2) without
surfacing any popup, auth prompt, or config message to the user.

This story delivers **only the probe + decision logic**. Actual fallback tier
implementation belongs to US-16.1.2 / US-16.1.3.

---

## Acceptance Criteria

- **AC1:** Before any search call, the skill runs a lightweight availability check that
  determines whether `vscode-websearchforcopilot_webSearch` can be invoked without
  triggering an auth prompt or throwing a configuration error.
- **AC2:** If the check passes → primary tool is used. If the check fails → skill moves
  to next tier silently (placeholder for US-16.1.2; for now, fallback path documents
  "future tier" and uses an HTTP/Playwright stub or clearly-flagged degradation).
- **AC3:** No error, popup, or config message is shown to the user when the primary tool
  is unavailable. The user sees only that the search proceeded (or a graceful "no
  results" message with no technical details).

---

## In Scope

1. **Update `search/SKILL.md`** to insert a new "Step 2.5: Tool Availability Probe"
   before the existing "Step 3: Execute Search & Fetch".
2. **Document the probe logic** — what signals indicate availability (cached probe
   result, configuration check, prior-failure flag) and the decision tree.
3. **Define the silent-fallback contract** — exactly what happens when probe fails,
   including the placeholder behavior until US-16.1.2 lands.
4. **Update SKILL.md frontmatter notes** if needed (e.g., note that primary search is
   probed, not assumed available).
5. **Add a small reference doc** `references/tool-availability-probe.md` with full
   probe algorithm and rationale.

## Out of Scope

- Implementing the Playwright stealth fallback search tier (US-16.1.2).
- Implementing the HTTP zero-auth fallback search tier (US-16.1.3).
- Modifying any skill other than `search`.
- Changing the URL-fetching 3-tier cascade (separate concern, already working).
- Adding any new Python dependencies or scripts beyond documentation.

---

## Constraints (from tech stack & RULE.md)

- This is a **skill instruction change** (Markdown only) — no Python script changes
  required, no new dependencies, no schema changes.
- Must comply with `.github/RULE.md` (governance overrides skill instructions).
- All user-facing strings stay in Vietnamese.
- SKILL.md content (instructions to Copilot) stays in English.
- Probe must be **silent** — no terminal output to user when primary tool unavailable.

---

## Assumptions

- The probe itself can be a documented decision procedure (read by Copilot) rather than
  an executable check, because Copilot is the one selecting and invoking the tool. The
  probe is essentially: "if user has previously hit Tavily popup OR no api key visible
  in env, treat primary as unavailable."
- No persistent storage of probe state is required for this story — a simple
  per-session signal (or per-call check) is sufficient. Persistent caching can be added
  in a later story if needed.
- US-16.1.2 will plug into the "fallback tier" hook documented here.

---

## Test Strategy (Phase 4 preview)

- **Static checks:** SKILL.md is valid Markdown, frontmatter intact, references resolve.
- **Behavioral check:** A short scenario doc in the run folder describing how Copilot
  should behave when probe says "unavailable" — used as future regression reference.
- **No code-level unit tests** since this story is pure documentation. Coverage gate
  (≥70%) does not apply to documentation-only stories per project convention.

---

## Risks

- **R1 (low):** Probe heuristic is too aggressive and disables a working primary tool.
  Mitigation: probe defaults to "available" unless a clear unavailability signal exists.
- **R2 (low):** Without US-16.1.2 in place, the "silent fallback" today is degraded
  behavior. Mitigation: documented as expected; story chain is sequenced.
