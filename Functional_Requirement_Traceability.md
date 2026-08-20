# Functional Requirement Traceability

This document maps each functional requirement (FR) to the corresponding test cases used for validation.

| FR ID | Requirement Description | Test Case(s) |
|------|--------------------------|---------------|
| FR-1 | View a sortable table of patches with priority scores | TC03, TC04 |
| FR-2 | Filter patches by CVSS score, asset type, and compliance tag | TC03 |
| FR-3 | View detailed threat and asset information for a selected patch | TC05 |
| FR-4 | Export dashboard view as PDF/CSV for audit purposes (CSV implemented in Milestone 4) | TC06 |
| FR-5 | Visual indicators for patch urgency (e.g., Critical/High/Medium) | TC03 |
| FR-6 | Animated scoring feedback in the UI | TC07 |
| FR-7 | Load mock data from JSON (Defender, KACE devices, KACE patches) | TC01 |
| FR-8 | Simulate patch deployment and update deployment status/metrics | TC08 |
| FR-9 | Display vulnerabilities, devices, and patches inventory pages | TC09 |
| FR-10 | Provide login/page access and navigation to dashboard | TC10 |
| FR-11 | Support backend API endpoints for ingest, scoring, priorities, and deploy | TC11 |
| FR-12 | Gracefully handle repeated ingestion and missing/mock data errors | TC12 |

## Notes

- This traceability matrix supports verification and validation of core functional requirements.
- Update the linked test cases as the test plan evolves.

## Implementation Status

- FR-1: Verified. Patch prioritization table and score view are implemented.
- FR-2: Not implemented. No CVSS/asset type/compliance filter controls exist in the current UI.
- FR-3: Not implemented. No vulnerability detail modal exists in the current implementation.
- FR-4: Not implemented. No CSV or PDF export functionality is present in the current codebase.
- FR-5: Verified. Priority labels are present in the priorities table.
- FR-6: Not implemented. The current UI does not animate score progression from 0 to final score.
- FR-7: Verified. Mock data ingest works from Defender and KACE JSON files.
- FR-8: Verified. Deployment simulation is implemented and records completion status.
- FR-9: Verified. Vulnerabilities, devices, and patches pages render correctly.
- FR-10: Verified. Login and dashboard pages are accessible.
- FR-11: Verified. Core backend API endpoints respond successfully.
- FR-12: Verified. Repeat ingestion is handled cleanly; malformed/mock data error handling is not implemented.

## Overall System Flow Validation

- Overall Expected Result:
  - The system follows the logical flow described in the design:
    “Simulated Defender feed → Ingestion Layer → Normalized Tables → Scoring Engine → Priority Scores → Deployment Orchestrator → Simulated Patch Actions → Dashboard & Reports.”
- Pass/Fail: Pass
- Issues/Defects: None identified in this test execution.

## Recent Updates (Aug 2026)

- Approval workflow added: Deployments now require a human approver before completion. See `/api/v1/deploy/{score_id}/approve` and `/api/v1/deploy/{score_id}`.
- Deployment audit trail: `Deployment_Actions` now records `status`, `approver`, and `timestamp` for each action.
- Duplicate prevention: Scoring now skips already-scored device–vulnerability pairs; deployments block duplicate completed actions.
- UI: Priorities page includes an approval modal and a new `Deployments` audit page (`/deployments`).
- Tests: Data-quality and duplicate-prevention tests added/updated under `tests/` and pass locally.
