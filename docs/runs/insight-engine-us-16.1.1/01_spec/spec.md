# Phase 1 — Specification

## Functional Requirements

### FR1 — Probe Procedure
Search skill MUST run a tool-availability probe before any call to
`vscode-websearchforcopilot_webSearch`. The probe is a decision procedure documented
in `references/tool-availability-probe.md` that returns one of:
- `AVAILABLE` → primary tool may be invoked
- `UNAVAILABLE` → primary tool MUST be skipped, fallback tier invoked

### FR2 — Session Caching
Once the probe yields `UNAVAILABLE` in a session, that result MUST be cached
(session-scoped flag) and reused for all subsequent search calls in the same session
without re-probing. Once it yields `AVAILABLE`, that result MAY be cached.

### FR3 — Silent Failure Mode
When the probe yields `UNAVAILABLE`, no Tavily/auth/configuration terminology, error
trace, popup notice, or technical detail MUST be shown to the user. The user-facing
message MUST be in Vietnamese and limited to a friendly status (e.g., "Không tìm
thấy kết quả tìm kiếm" until the fallback tier in US-16.1.2 ships).

### FR4 — Internal Diagnostics
When the probe yields `UNAVAILABLE`, an internal note MUST be appendable to the
current run folder (developer-visible), describing the unavailability signal observed.

## Non-Functional Requirements

### NFR1 — No New Dependencies
This story MUST NOT add Python packages, Node modules, or system tools.

### NFR2 — Documentation-Only
All changes MUST be Markdown (SKILL.md edit + new reference doc). No code files
created or modified.

### NFR3 — Backward Compatibility
Existing search behavior when primary tool is fully configured MUST remain identical
(probe returns AVAILABLE → Step 3 runs unchanged).

### NFR4 — RULE.md Compliance
All behavior MUST defer to `.github/RULE.md` if any conflict arises.

## Interfaces

### Step 2.5 (new, in SKILL.md)
- **Input:** Query list from Step 2.
- **Output:** A probe verdict (AVAILABLE | UNAVAILABLE) consumed by Step 3.
- **Side effects:** May set session-scoped `primary_unavailable` flag; may write
  internal diagnostic note to run folder.

### Fallback Tier Hook (placeholder)
- **Trigger:** Probe verdict = UNAVAILABLE.
- **Behavior in this story:** Log internal note + emit friendly Vietnamese "no
  results" message.
- **Future:** US-16.1.2 will replace the placeholder with Playwright stealth search.

## Acceptance Criteria Mapping

| AC | Spec Item |
|----|-----------|
| AC1 (probe runs before search) | FR1 |
| AC2 (branch on probe result) | FR1, FR2 |
| AC3 (silent UX) | FR3, FR4 |

## Self-Review Notes

- Spec items map 1:1 with ACs and the design from Phase 0.
- No undefined behavior — UNAVAILABLE path is explicitly bounded by US-16.1.2.
- Constraints reflect tech-stack and RULE.md governance.
