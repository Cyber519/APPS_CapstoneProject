# Functional Test Cases

## TC01 – Mock Data Ingestion
- Objective: Verify that Defender and KACE mock JSON files are successfully ingested.
- Preconditions: Application running; JSON files present in `/data`.
- Steps:
  1. Start APPS backend.
  2. Navigate to Dashboard and click “Ingest Data”.
- Expected Result:
  - Defender, KACE devices, and KACE patches load successfully.
  - Summary metrics update (e.g., “Total Devices: 3”, “Total Vulnerabilities: 12”).
- Pass/Fail: Pass
- Notes: Ingestion endpoint returned 200 and data loaded successfully. Dashboard reflects ingested mock records.

## TC02 – Scoring Engine Calculation
- Objective: Validate the weighted scoring model.
- Preconditions: TC01 passed; data ingested.
- Steps:
  1. Click “Run Scoring” on the dashboard.
  2. Observe scores in the priorities view.
- Expected Result:
  - Scores reflect severity, exploitability, and device criticality using the formula:
    `(Severity * 0.5) + (Exploitability * 0.3) + (Criticality * 0.2)`.
- Pass/Fail: Fail
- Notes: Scoring endpoint returned 200, but the current implementation uses a different weighted formula: `(CVSS*4)+(criticality*3)+(patch_severity*2)+exploit+age`. The expected formula in the test case does not match the code.

## TC03 – Priority Queue Generation
- Objective: Ensure prioritized list is generated and sorted correctly.
- Preconditions: TC02 passed.
- Steps:
  1. Open “Patch Prioritization” view.
  2. Inspect the “Score” column ordering.
- Expected Result:
  - Patches are sorted in descending order of score; highest risk first.
  - Urgency indicators (Critical/High/Medium) align with severity.
- Pass/Fail: Pass
- Notes: Priorities endpoint returns sorted results and the UI includes priority label classes for urgency.

## TC04 – Dashboard Rendering
- Objective: Validate dashboard layout and metrics.
- Preconditions: TC01 passed.
- Steps:
  1. Navigate to `dashboard.html`.
  2. Confirm summary tiles and charts render.
- Expected Result:
  - Dashboard shows summary metrics and charts similar to Milestone 4 wireframes:
    “Summary Metrics: Total Devices, Total Vulnerabilities, Critical Findings, Pending Deployments”.
- Pass/Fail: Pass
- Notes: Dashboard page renders successfully with metrics and charts. Label text differs from the wireframe wording, but the dashboard content is present.

## TC05 – Vulnerability Detail Modal
- Objective: Verify detailed threat information is accessible.
- Preconditions: TC03 passed.
- Steps:
  1. In the priorities or vulnerabilities table, click a row.
  2. Observe the modal content.
- Expected Result:
  - Modal displays device, CVE ID, severity, exploitability, device criticality, and scoring breakdown (including final score and explanation).
- Pass/Fail: Fail
- Notes: No detail modal exists in the current implementation. Detail information is available only in the priorities table row.

## TC06 – Export Report (CSV)
- Objective: Validate export functionality.
- Preconditions: TC03 passed.
- Steps:
  1. In “Patch Prioritization” view, click “Export CSV”.
  2. Open the generated CSV file.
- Expected Result:
  - CSV contains prioritized patches with score, hostname, CVE ID, severity, and status, derived from mock data.
- Pass/Fail: Fail
- Notes: Export functionality is not implemented in the current codebase; no CSV/PDF generation was found.

## TC07 – Scoring Animation
- Objective: Confirm animated scoring feedback works.
- Preconditions: TC02 passed.
- Steps:
  1. Trigger scoring from the UI.
  2. Observe the scoring animation (e.g., modal or progress effect).
- Expected Result:
  - Animated score progression from 0 to final score, as described in Milestone 4: “Animated score progression (0 → final score).”.
- Pass/Fail: Fail
- Notes: The current UI does not animate score progression from 0 to final score; scoring runs and navigates to the priorities page.

## TC08 – Deployment Simulation
- Objective: Verify deployment simulation and status update functionality.
- Preconditions: TC03 passed; scoring completed.
- Steps:
  1. In the priorities view, click the deploy button for a patch.
  2. Observe progress and status update.
- Expected Result:
  - Deployment simulation completes successfully.
  - Deployment status updates and dashboard metrics reflect the deployment.
- Pass/Fail: Pass
- Notes: Deployment endpoint returned 200 and the app records deployment status successfully. UI button animation exists in code.

## TC09 – Inventory Pages Rendering
- Objective: Validate vulnerabilities, devices, and patches pages render correctly.
- Preconditions: TC01 passed; data ingested.
- Steps:
  1. Open `/vulnerabilities`, `/devices`, and `/patches` pages.
  2. Confirm table data appears for each page.
- Expected Result:
  - Each inventory page displays the corresponding data tables.
  - Rows and key columns are visible for vulnerabilities, devices, and patches.
- Pass/Fail: Pass
- Notes: All inventory pages returned 200 and page content is present.

## TC10 – Login and Navigation
- Objective: Verify login page access and navigation to dashboard.
- Preconditions: Application running.
- Steps:
  1. Navigate to `/login`.
  2. Navigate to `/dashboard`.
- Expected Result:
  - Login page loads successfully.
  - Dashboard page is reachable and renders without errors.
- Pass/Fail: Pass
- Notes: Both `/login` and `/dashboard` returned 200.

## TC11 – API Endpoint Validation
- Objective: Validate backend API endpoints for ingestion, scoring, priorities, and deployment.
- Preconditions: Application running.
- Steps:
  1. Call `/api/v1/ingest`.
  2. Call `/api/v1/scoring`.
  3. Call `/api/v1/priorities`.
  4. Call `/api/v1/deploy/{score_id}` with a valid score ID.
- Expected Result:
  - API endpoints respond successfully with expected payloads.
  - Priorities endpoint returns sorted results and deploy endpoint updates deployment status.
- Pass/Fail: Pass
- Notes: All API endpoints returned 200 and the priorities list is sorted descending by score.

## TC12 – Repeat Ingestion/Error Handling
- Objective: Verify behavior on repeated ingestion and missing/mock data errors.
- Preconditions: Application running; data ingested at least once.
- Steps:
  1. Click “Ingest Data” again after initial ingestion.
  2. Observe system response.
- Expected Result:
  - System handles repeated ingestion gracefully.
  - Any missing or malformed mock data is reported appropriately.
- Pass/Fail: Pass
- Notes: Repeated ingestion returns 200 and data is reloaded cleanly. Explicit malformed/mock-data error handling is not present in the current implementation.

## Overall System Flow Validation
- Overall Expected Result:
  - The system follows the logical flow described in the design:
    “Simulated Defender feed → Ingestion Layer → Normalized Tables → Scoring Engine → Priority Scores → Deployment Orchestrator → Simulated Patch Actions → Dashboard & Reports.”
- Pass/Fail: Partially Pass
- Issues/Defects:
  - The scoring formula implemented in code differs from the test case expected formula.
  - Vulnerability detail modal and export CSV/PDF are not implemented.
  - Animated score progression from 0 to final score is not present in the current UI.
