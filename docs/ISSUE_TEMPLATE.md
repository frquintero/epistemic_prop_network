<!-- ISSUE TEMPLATE: Agent Implementation Constraints
This template is used to create issues when an agent or contributor makes a temporary
workaround (fallback, duplicate request, or ad-hoc patch) that masks an underlying bug.
Use this template to ensure the workaround is documented, justified, and tracked for
follow-up remediation.
-->

# Agent Workaround / Temporary Patch Report

**Short Description:**

- Describe the bug or unexpected behavior and the temporary workaround applied.

**Files / Components Affected:**

- List changed files, scripts, and modules (e.g., `scripts/run_xai_batch.py`, `AGENTS.md`).

**Root-Cause Analysis (required):**

- Explain the underlying cause of the issue. If unknown, summarize the debugging steps taken and why the root cause remains unresolved.

**Why a Temporary Workaround Was Chosen:**

- Explain why a quick fix was preferred over a full remediation at the time of patching (time constraints, risk, test coverage, etc.).

**Workaround Details:**

- Provide the exact changes made (diff or list of edits). Mark the workaround with `TODO: remove` comments in code where appropriate.

**Tests & Validation Added:**

- List unit/integration tests added or modified to cover the bug and the planned fix. If none were added, explain why and add a follow-up TODO to add tests.

**Logging / Telemetry:**

- Describe what logs or telemetry were added to detect recurrence and gather evidence for the permanent fix.

**Planned Permanent Fix:**

- Describe the planned remediation (file/PR references, owner, and ETA). If not decided, add an explicit TODO with assignee and priority.

**Acceptance Criteria For Closing This Issue:**

- Root cause fixed and validated by tests.

- Temporary workaround removed and code annotated.

- CI green and a brief post-mortem added to the PR.

**References:**

- Link to `AGENTS.md` and any related docs.

**Additional Notes / Context:**

- Anything else reviewers should know.
