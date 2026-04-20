# Phase 4 — Test Notes

This is a documentation-only story. Per project convention, the ≥70% code-coverage gate
does not apply (no executable code added or changed).

## Static Verification Performed

| Check | Result |
|-------|--------|
| `get_errors` on `search/SKILL.md` | ✅ No errors |
| `get_errors` on `references/tool-availability-probe.md` | ✅ No errors |
| Frontmatter intact, version bumped to 1.1 | ✅ |
| New reference link present in References list | ✅ (line 29) |
| Step 2.5 inserted before Step 3 | ✅ (lines 83 / 121) |
| Step 3 has skip-on-UNAVAILABLE notice | ✅ (line 123) |
| All cross-links target existing files | ✅ |

## Behavioral Acceptance Walkthrough

### AC1 — Probe runs before search execution
The new `Step 2.5: Tool Availability Probe (Hard Gate Before Step 3)` mandates the
probe procedure documented in `references/tool-availability-probe.md` is executed
before any call to the primary tool. ✅

### AC2 — Branch on probe result
- `AVAILABLE` → Step 3 runs unchanged (existing flow preserved).
- `UNAVAILABLE` → Step 3 explicitly skipped via `*(Skip this step if Step 2.5 returned UNAVAILABLE.)*`; fallback tier invoked. ✅

### AC3 — Silent UX
The probe contract in both SKILL.md (Step 2.5 "Fallback tier") and the reference doc
(`Silent Failure Contract` section) prohibits surfacing Tavily/auth/configuration
text. Only a friendly Vietnamese "no results" message is allowed during the
placeholder period. ✅

## Regression Risk

- **Low.** Default verdict is `AVAILABLE` unless an explicit failure signal is
  observed, so existing fully-configured installations behave identically.
- US-16.1.2 will replace the placeholder fallback path with real Playwright search.
