# APPS Documentation

This document summarizes the recent enhancements and provides quick usage instructions for running and testing the APPS (Automated Patch Prioritization System) project.

## Summary of recent enhancements

- Workflow demo script: `scripts/demo_workflow.py` runs ingest → scoring → priorities → approve → deploy end-to-end using mock data.
- Approval workflow: deployments require a human approver before completion. Approval is recorded in `Deployment_Actions`.
- Deployment audit trail: `Deployment_Actions` now records `status`, `action_status`, `approver`, and `timestamp`.
- UI changes: color-coded priority labels and an approval modal (instead of `prompt()`), plus a `Deployments` audit page.
- Duplicate prevention: scoring prevents duplicate device-vulnerability scoring; deployment prevents duplicate completed deployments.
- Data quality tests: pytest tests simulate missing/malformed data and validate duplicate safeguards.
- Additional mock data: 5 new vulnerabilities added to `data/defender_mock.json` for richer demos.

## API Reference (new / updated)

- `POST /api/v1/ingest` — ingest mock data from `data/` files into SQLite DB.
- `POST /api/v1/score` — calculate priority scores and populate `Priority_Scores`.
- `GET /api/v1/priorities` — returns priority list (used by UI route `/priorities`).
- `GET /api/v1/priorities/{score_id}` — return detail for a score.
- `POST /api/v1/deploy/{score_id}/approve` — record an approval. Body: `{"approver": "name"}`.
- `POST /api/v1/deploy/{score_id}` — completes a deployment (requires prior approval).
- `GET /deployments` — UI page showing the audit report (reads from `Deployment_Actions`).

Notes:
- Approvals are recorded as actions with `status='approved'` and `approver` set.
- A subsequent `POST /api/v1/deploy/{score_id}` records a `completed` action and copies the approver into the completed action.

## UI Behavior

- Priorities page: `http://127.0.0.1:8000/priorities` shows the color-coded score and a "Simulate Deploy" button.
- Approval modal: clicking the deploy button opens a modal requiring a non-empty approver name. The modal validates input before calling the approve API and then the deploy API.
- Audit page: `http://127.0.0.1:8000/deployments` lists all deployment actions (id, score_id, status, approver, timestamp).

### Color mapping

- Critical (red): score ≥ 8
- High (orange): 6 ≤ score < 8
- Medium (yellow): 4 ≤ score < 6
- Low (green): score < 4

The server assigns the `priority` label and the UI applies corresponding CSS classes (`priority critical|high|medium|low`).

## Demo: run full workflow locally

1. Ensure virtualenv is activated and deps installed.
2. Start the dev server (if not already running):

```powershell
c:/Users/zakiy/Documents/APPS_Project/.venv/Scripts/python.exe -m uvicorn main:app --reload
```

3. Open the priorities page in your browser: `http://127.0.0.1:8000/priorities`.
4. Click "Simulate Deploy" on a priority row — an approval modal will appear.
5. Enter an approver name and click "Approve"; the UI will record approval then run deploy and refresh.
6. Inspect `http://127.0.0.1:8000/deployments` to see the recorded actions.

Alternatively, run the scripted demo to see printed output (demo deletes and recreates `apps.db`):

```powershell
c:/Users/zakiy/Documents/APPS_Project/.venv/Scripts/python.exe scripts/demo_workflow.py
```

## Testing

Run pytest to execute the data-quality and duplicate-protection tests:

```powershell
c:/Users/zakiy/Documents/APPS_Project/.venv/Scripts/python.exe -m pytest -q
```

Files of interest:

- `services/scoring_service.py` — scoring, deployment, approval, and audit helpers.
- `api/priorities_api.py` — approve and deploy endpoints.
- `templates/priorities.html` — UI with approval modal.
- `templates/deployments.html` — audit report.
- `static/app.js` — approval/deploy client logic and modal handling.
- `data/defender_mock.json` — mock vulnerability data (additional records added).
- `scripts/demo_workflow.py` — runnable demo script (prints before/after details).
- `tests/test_data_quality.py` — tests for malformed data handling and duplicate controls.

## Notes for contributors

- Schema changes: `database/schema.sql` now includes `status` and `approver` columns on `Deployment_Actions`. If you have an existing `apps.db`, delete it and re-run the server or `init_db()` to recreate schema for local testing.
- The approver identity is currently free-text; recommend integrating with an authentication layer (e.g., login) before using in production.
- The approval flow simulates human approval and records `approver` in the audit trail; the design keeps `action_status` for backwards compatibility.

If you'd like, I can:
- Add a nicer approval modal UX (inline validation, saving approver across session),
- Add filtering/sorting/search to the deployments audit page,
- Generate a CHANGELOG or release notes file.

*** End of documentation ***
