# Functional Test Documentation (FTD)
## Automated Patch Prioritization System (APPS)

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Status:** In Development  
**Test Environment:** Windows 10/11 + Python 3.8+ + SQLite  

---

## 1. Test Scope and Objectives

### 1.1 Scope

This document defines functional test cases for the APPS system including:
- ✓ Frontend UI functionality and interactions
- ✓ Backend API endpoints and responses
- ✓ Database operations and data integrity
- ✓ End-to-end workflow scenarios
- ✓ Error handling and edge cases
- ✓ Performance under expected load

### 1.2 Test Objectives

1. Verify all user workflows execute successfully
2. Validate data accuracy throughout the system
3. Ensure consistent user experience across browsers
4. Confirm error scenarios handled gracefully
5. Document and track bugs discovered during testing

### 1.3 Out of Scope

- Performance/load testing (see separate Performance Test Plan)
- Security penetration testing (see separate Security Audit)
- Accessibility compliance testing (WCAG 2.1)
- Mobile responsive testing (desktop only for MVP)
- Third-party API integration testing (using mock data only)

---

## 2. Test Environment Setup

### 2.1 Prerequisites

Before executing any test cases:

```
1. Clone/obtain APPS project repository
2. Create Python virtual environment: python -m venv .venv
3. Activate venv: .venv\Scripts\activate (Windows)
4. Install requirements: pip install -r requirements.txt
5. Verify project structure includes:
   - main.py
   - database/schema.sql
   - api/ (defender, kace, priorities routers)
   - services/ (ingestion, scoring)
   - templates/ (all HTML pages)
   - static/ (app.js, styles.css)
   - data/ (mock JSON files)
6. Initialize database: python -c "from database.db import init_db; init_db()"
7. Start server: uvicorn main:app --reload
8. Access UI: http://localhost:8000
```

### 2.2 Test System Specifications

| Component | Specification |
|-----------|---|
| OS | Windows 10/11 |
| Browser | Chrome 120+, Firefox 121+, Edge 120+ |
| Python | 3.8+ |
| FastAPI | 0.104+ |
| Database | SQLite 3 |
| RAM | 4GB minimum |
| Disk | 1GB free |

### 2.3 Test Data Reset

Between test runs, reset the database:

```python
# reset_db.py script
import os
from database.db import init_db

db_file = "apps.db"
if os.path.exists(db_file):
    os.remove(db_file)
init_db()
print("Database reset complete")
```

---

## 3. Test Case Categories

### 3.1 Category: Login/Authentication

#### TC-LOGIN-001: Access Login Page
- **Objective:** Verify login page displays correctly
- **Precondition:** Server running, no active session
- **Steps:**
  1. Navigate to `http://localhost:8000/login`
  2. Observe login form
- **Expected Result:** Login page renders with form fields visible
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-LOGIN-002: Redirect Unauthenticated Users
- **Objective:** Verify unauthenticated access to protected pages
- **Precondition:** No active session
- **Steps:**
  1. Attempt direct access to `http://localhost:8000/dashboard`
  2. Verify redirection behavior
- **Expected Result:** Either redirect to login or display dashboard without auth
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** Note: Current implementation lacks authentication enforcement

---

### 3.2 Category: Dashboard Functionality

#### TC-DASH-001: Dashboard Page Loads
- **Objective:** Verify dashboard renders correctly on page load
- **Precondition:** Server running, database initialized with mock data
- **Steps:**
  1. Navigate to `http://localhost:8000/dashboard`
  2. Wait for page to fully load (all assets loaded)
  3. Verify all sections visible
- **Expected Result:**
  - ✓ Page title: "Information Security Risk Dashboard"
  - ✓ Four metric cards displayed (% Risks, Open Findings, Progress, Response)
  - ✓ Risk breakdown section visible
  - ✓ Response tracking progress bars visible
  - ✓ Action buttons visible (Ingest Data, Run Scoring)
  - ✓ No console errors
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-002: Metric Card Display
- **Objective:** Verify metric values display correctly
- **Precondition:** Dashboard page loaded with mock data ingested
- **Steps:**
  1. Observe metric cards:
     - "% Active Risk" card
     - "Open Findings" card
     - "Risk Analysis Progress" card
     - "Response Progress" card
- **Expected Result:**
  - ✓ All metric cards contain numeric values
  - ✓ Values match database query results
  - ✓ Progress bars show correct percentage (0-100%)
  - ✓ Text color reflects risk level (red for high, green for low)
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-003: Risk Breakdown Visualization
- **Objective:** Verify risk breakdown by priority level
- **Precondition:** Scoring completed with priority scores in database
- **Steps:**
  1. Locate "Risk Rating Breakdown" section
  2. Verify counts for:
     - Critical (red)
     - High (orange)
     - Medium (yellow)
     - Low (green)
- **Expected Result:**
  - ✓ All priority counts displayed
  - ✓ Colors match severity level
  - ✓ Sum of counts ≤ total vulnerabilities
  - ✓ Percentages calculated correctly
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-004: Ingest Data Button
- **Objective:** Verify "Ingest Data" button functionality
- **Precondition:** Dashboard page loaded, database empty or stale data
- **Steps:**
  1. Click "Ingest Data" button
  2. Wait for operation to complete
  3. Observe response feedback
  4. Refresh page or check console
- **Expected Result:**
  - ✓ Button changes to disabled/loading state
  - ✓ API call completes (status 200)
  - ✓ Toast notification shows "Ingestion completed"
  - ✓ Dashboard metrics update with new data
  - ✓ Database tables populated:
    - Devices: 10+ records
    - Vulnerabilities: 20+ records
    - Patches: 5+ records
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-005: Run Scoring Button
- **Objective:** Verify "Run Scoring" button calculates priorities
- **Precondition:** Dashboard loaded with data ingested
- **Steps:**
  1. Click "Run Scoring" button
  2. Wait for calculation to complete (may show spinner)
  3. Observe response notification
  4. Check priority metrics updated
- **Expected Result:**
  - ✓ Button disabled during calculation
  - ✓ API call to `/api/v1/scoring` completes
  - ✓ Response shows scores_calculated > 0
  - ✓ Toast: "Scoring calculation complete"
  - ✓ Priority breakdown updates with new data
  - ✓ Priority_Scores table populated
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-006: Dashboard Metric Refresh
- **Objective:** Verify metrics update after operations
- **Precondition:** Dashboard displayed
- **Steps:**
  1. Record initial metric values
  2. Perform ingestion or scoring
  3. Observe metric changes
  4. Or press F5 to refresh, verify values persist
- **Expected Result:**
  - ✓ Metrics update automatically or on page refresh
  - ✓ No stale data displayed
  - ✓ Calculations accurate
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-007: Navigation Button - Vulnerabilities
- **Objective:** Verify button navigation to vulnerabilities page
- **Precondition:** Dashboard displayed with navigation buttons visible
- **Steps:**
  1. Click "View Vulnerabilities" button at bottom
  2. Observe page transition
  3. Verify new page loads
- **Expected Result:**
  - ✓ URL changes to `/vulnerabilities`
  - ✓ Vulnerabilities table page displays
  - ✓ Navigation maintains dashboard context
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-008: Navigation Button - Devices
- **Objective:** Verify button navigation to devices page
- **Precondition:** Dashboard displayed
- **Steps:**
  1. Click "View Devices" button
  2. Verify page navigation
- **Expected Result:**
  - ✓ URL changes to `/devices`
  - ✓ Devices table displayed
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-DASH-009: Navigation Button - Patches
- **Objective:** Verify button navigation to patches page
- **Precondition:** Dashboard displayed
- **Steps:**
  1. Click "View Patches" button
  2. Verify page navigation
- **Expected Result:**
  - ✓ URL changes to `/patches`
  - ✓ Patches table displayed
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.3 Category: Vulnerabilities Page

#### TC-VULN-001: Vulnerabilities Page Loads
- **Objective:** Verify vulnerabilities table displays
- **Precondition:** Data ingested, navigate to `/vulnerabilities`
- **Steps:**
  1. Access vulnerabilities page
  2. Wait for data load
  3. Observe table
- **Expected Result:**
  - ✓ Page title: "Vulnerabilities" or similar
  - ✓ Table displays with columns: CVE ID, Severity, CVSS, Description
  - ✓ Rows populate with vulnerability data
  - ✓ No errors in console
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-VULN-002: Vulnerability Data Accuracy
- **Objective:** Verify displayed vulnerability data matches database
- **Precondition:** Vulnerabilities page loaded
- **Steps:**
  1. Select 3 random vulnerabilities from table
  2. Query database for same records
  3. Compare displayed vs. database values
- **Expected Result:**
  - ✓ All displayed data matches database records
  - ✓ CVSS scores display with precision (1 decimal)
  - ✓ Severity badges show correct color
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-VULN-003: Vulnerability Filtering (Optional)
- **Objective:** Verify severity filter functionality if implemented
- **Precondition:** Vulnerabilities page
- **Steps:**
  1. Filter by severity: Critical
  2. Observe table updates
- **Expected Result:**
  - ✓ Only Critical severity vulnerabilities displayed
  - ✓ Count accurate
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.4 Category: Devices Page

#### TC-DEV-001: Devices Page Loads
- **Objective:** Verify devices table displays
- **Precondition:** Data ingested, navigate to `/devices`
- **Steps:**
  1. Access devices page
  2. Observe table content
- **Expected Result:**
  - ✓ Table displays with columns: Hostname, OS, Criticality, Vuln Count
  - ✓ Device data populated from Devices table
  - ✓ No errors
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocks
- **Notes:** _____________

#### TC-DEV-002: Device Criticality Display
- **Objective:** Verify device criticality levels display correctly
- **Precondition:** Devices page loaded
- **Steps:**
  1. Observe criticality column
  2. Verify values are: High, Medium, or Low
  3. Check color-coding (if implemented)
- **Expected Result:**
  - ✓ Criticality values correct
  - ✓ Color badges displayed appropriately
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.5 Category: Patches Page

#### TC-PATCH-001: Patches Page Loads
- **Objective:** Verify patches table displays
- **Precondition:** Data ingested, navigate to `/patches`
- **Steps:**
  1. Access patches page
  2. Verify table
- **Expected Result:**
  - ✓ Table displays with patch data
  - ✓ Columns: Patch ID, Severity, Reboot Required
  - ✓ Data populated
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.6 Category: Priorities/Scoring Results

#### TC-PRIO-001: Priorities Page Loads After Scoring
- **Objective:** Verify scores display on priorities page
- **Precondition:** Ingestion and scoring completed
- **Steps:**
  1. Navigate to `/priorities`
  2. Observe results table
- **Expected Result:**
  - ✓ Table displays scored results
  - ✓ Columns: Device, Vulnerability, Priority, Score, Patch
  - ✓ Priority badges color-coded (Critical=red, High=orange, etc.)
  - ✓ Score values displayed (should be > 0, not all 0.0)
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-PRIO-002: Score Value Calculation
- **Objective:** Verify scores calculated using correct formula
- **Precondition:** Priorities page with scores
- **Steps:**
  1. Select specific device-vulnerability pair
  2. Verify score value matches formula:
     score = (cvss × 4) + (criticality × 3) + (patch_severity × 2) + exploit + age_factor
  3. Verify priority classification:
     - Critical: score >= 80
     - High: 60 <= score < 80
     - Medium: 40 <= score < 60
     - Low: score < 40
- **Expected Result:**
  - ✓ Score calculation accurate
  - ✓ Priority classification correct
  - ✓ No scores at 0.0 (if valid data associated)
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-PRIO-003: Score Animation on Page Load
- **Objective:** Verify score counter animation effect
- **Precondition:** Priorities page with scores
- **Steps:**
  1. Load priorities page
  2. Watch score values in table
  3. Observe animation from 0 → final value
- **Expected Result:**
  - ✓ Scores animate from 0 to final value
  - ✓ Animation duration ~2 seconds
  - ✓ Animation smooth and readable
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-PRIO-004: Deploy Button Functionality
- **Objective:** Verify deploy button initiates deployment
- **Precondition:** Priorities page with results
- **Steps:**
  1. Click deploy button on first priority row
  2. Observe progress bar animation
  3. Wait for completion
  4. Observe result
- **Expected Result:**
  - ✓ Progress bar appears
  - ✓ Progress animates 0-100% over ~3 seconds
  - ✓ On completion: deployment_status updates to 'Completed'
  - ✓ Toast notification: "Deployment complete"
  - ✓ Row highlights in green
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-PRIO-005: Dashboard Update After Deployment
- **Objective:** Verify dashboard metrics reflect deployments
- **Precondition:** Deployment completed on priority row
- **Steps:**
  1. Navigate back to dashboard
  2. Observe metric updates
- **Expected Result:**
  - ✓ "Remediated" count increases
  - ✓ "Open Findings" count decreases
  - ✓ "Active Risk %" decreases
  - ✓ Deployment shows in "Completed Deployments"
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.7 Category: API Endpoint Testing

#### TC-API-001: GET /
- **Objective:** Test root endpoint
- **Test:** `curl http://localhost:8000/`
- **Expected Response:**
  ```json
  {"message": "APPS API running"}
  ```
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-API-002: POST /api/v1/ingest
- **Objective:** Test complete data ingestion
- **Test:** `curl -X POST http://localhost:8000/api/v1/ingest`
- **Expected Response:**
  ```json
  {"status": "success", "devices": X, "vulnerabilities": Y, "patches": Z}
  ```
- **Validation:**
  - ✓ Status 200 OK
  - ✓ Devices count > 0
  - ✓ Vulnerabilities count > 0
  - ✓ Patches count > 0
  - ✓ Database tables populated
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-API-003: POST /api/v1/scoring
- **Objective:** Test scoring calculation
- **Precondition:** Data ingested
- **Test:** `curl -X POST http://localhost:8000/api/v1/scoring`
- **Expected Response:**
  ```json
  {"status": "success", "scores_calculated": N}
  ```
- **Validation:**
  - ✓ Status 200 OK
  - ✓ scores_calculated > 0
  - ✓ Priority_Scores table populated
  - ✓ score_value field > 0 (not all 0.0)
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-API-004: GET /api/v1/priorities
- **Objective:** Test retrieve priorities list
- **Precondition:** Scoring completed
- **Test:** `curl http://localhost:8000/api/v1/priorities`
- **Expected Response:**
  ```json
  {"status": "success", "priorities": [...]}
  ```
- **Validation:**
  - ✓ Status 200 OK
  - ✓ Array of priority objects with: score_value, priority, patch_id
  - ✓ Array sorted by score descending
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-API-005: POST /api/v1/deploy/{score_id}
- **Objective:** Test deployment action recording
- **Precondition:** Valid score_id exists
- **Test:** `curl -X POST http://localhost:8000/api/v1/deploy/1`
- **Expected Response:**
  ```json
  {"status": "success"}
  ```
- **Validation:**
  - ✓ Status 200 OK
  - ✓ Deployment_Actions record created
  - ✓ action_status = 'Completed'
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-API-006: GET /dashboard (Template)
- **Objective:** Test dashboard template rendering
- **Test:** `curl http://localhost:8000/dashboard`
- **Expected Response:**
  - ✓ Status 200 OK
  - ✓ HTML content returned
  - ✓ Contains metric card elements
  - ✓ Context variables injected (devices, total_vulns, etc.)
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

---

### 3.8 Category: Error Scenarios

#### TC-ERR-001: Database Connection Failure
- **Objective:** Verify graceful handling of DB errors
- **Precondition:** Database file removed or inaccessible
- **Steps:**
  1. Remove database file
  2. Attempt to access endpoint
  3. Observe error handling
- **Expected Result:**
  - ✓ 500 error returned with descriptive message
  - ✓ No stack trace exposed to user
  - ✓ Server remains running (no crash)
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-ERR-002: Invalid Request Data
- **Objective:** Test malformed API request handling
- **Test:** 
  ```bash
  curl -X POST http://localhost:8000/api/v1/ingest \
    -H "Content-Type: application/json" \
    -d '{"invalid": "json"}'
  ```
- **Expected Result:**
  - ✓ 422 Unprocessable Entity returned
  - ✓ Clear error message
- **Status:** ☐ Pass ☐ Fail
- **Notes:** _____________

#### TC-ERR-003: Missing Mock Data Files
- **Objective:** Verify handling of missing data files
- **Precondition:** Rename defender_mock.json
- **Steps:**
  1. Attempt ingestion
  2. Observe error
- **Expected Result:**
  - ✓ Graceful error message
  - ✓ 500 status with explanation
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-ERR-004: Double Ingestion
- **Objective:** Verify behavior on repeat ingestion
- **Steps:**
  1. Click "Ingest Data" button
  2. Wait for completion
  3. Click "Ingest Data" again immediately
  4. Observe result
- **Expected Result:**
  - ✓ Second ingestion processes successfully
  - ✓ No duplicate key errors
  - ✓ Data integrity maintained
  - OR appropriate error message shown
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

### 3.9 Category: UI/UX

#### TC-UI-001: Responsive Button States
- **Objective:** Verify button visual feedback
- **Steps:**
  1. Hover over "Ingest Data" button
  2. Click button
  3. Observe states: normal, hover, active, disabled
- **Expected Result:**
  - ✓ Hover: color change/underline visible
  - ✓ Click: button disables (grayed out)
  - ✓ Animation feedbacker obvious
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-UI-002: Toast Notification Display
- **Objective:** Verify toast notifications appear and disappear
- **Steps:**
  1. Trigger action that shows toast (e.g., click Ingest)
  2. Observe toast appears
  3. Wait 5 seconds
  4. Observe toast disappears
- **Expected Result:**
  - ✓ Toast visible in lower right corner
  - ✓ Auto-dismisses after ~5 seconds
  - ✓ Message clear and readable
  - ✓ Multiple toasts stack vertically
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

#### TC-UI-003: Color Scheme Consistency
- **Objective:** Verify dashboard uses consistent cybersecurity theme
- **Steps:**
  1. Observe dashboard colors
  2. Check all severity badges
  3. Verify button colors
- **Expected Result:**
  - ✓ Dark gray background (#1a1a1a or similar)
  - ✓ Critical items: RED (#ff3333 or similar)
  - ✓ High items: ORANGE (#ff9900)
  - ✓ Medium items: YELLOW (#ffcc00)
  - ✓ Low items: GREEN (#00cc66)
  - ✓ Accents: Cyan/Blue (#00d9ff, #0066ff)
- **Actual Result:** _____________
- **Status:** ☐ Pass ☐ Fail ☐ Blocked
- **Notes:** _____________

---

## 4. End-to-End Test Scenarios

### Scenario 1: Complete Workflow - Fresh System
**Objective:** Test complete workflow from fresh database

**Steps:**
1. Reset database (TC-SETUP):
   ```python
   import os
   os.remove("apps.db") if os.path.exists("apps.db") else None
   ```

2. Start server:
   ```bash
   uvicorn main:app --reload
   ```

3. Execute test sequence:
   - TC-DASH-001: Access dashboard (empty state)
   - TC-DASH-004: Click "Ingest Data"
   - TC-DASH-002: Verify metrics updated (except priority counts should be 0)
   - TC-VULN-001: Navigate to vulnerabilities page
   - TC-DEV-001: Navigate to devices page
   - TC-DASH-005: Navigate back, click "Run Scoring"
   - TC-PRIO-001: Navigate to priorities page, verify scores
   - TC-PRIO-004: Click deploy on first result
   - TC-PRIO-005: Navigate back to dashboard, verify remediation updated

**Expected Outcome:**
- ✓ All steps complete without errors
- ✓ Data flows correctly through system
- ✓ Metrics increase at each stage
- ✓ UI remains responsive

**Status:** ☐ Pass ☐ Fail ☐ Partially Complete

**Issues Found:**
1. _____________
2. _____________
3. _____________

---

### Scenario 2: Data Verification
**Objective:** Verify data integrity throughout workflow

**Steps:**
1. Complete Scenario 1
2. Query database for each table:
   ```sql
   SELECT COUNT(*) FROM Devices;           -- Should be ~10
   SELECT COUNT(*) FROM Vulnerabilities;   -- Should be ~20
   SELECT COUNT(*) FROM Patches;           -- Should be ~5
   SELECT COUNT(*) FROM Device_Vulnerabilities;  -- Should be ~50+
   SELECT COUNT(*) FROM Priority_Scores;   -- Should equal DV count
   SELECT COUNT(*) FROM Deployment_Actions WHERE action_status='Completed';  -- Should be ≥1
   ```
3. Verify FOREIGN KEY relationships:
   ```sql
   -- No orphaned records (all FKs resolve)
   SELECT * FROM Priority_Scores WHERE dv_id NOT IN (SELECT dv_id FROM Device_Vulnerabilities);
   ```

**Expected Outcome:**
- ✓ All count queries return expected ranges
- ✓ No orphaned FK records
- ✓ Data consistency maintained

**Status:** ☐ Pass ☐ Fail

---

### Scenario 3: Multiple Deployments
**Objective:** Test multiple deployments update metrics correctly

**Steps:**
1. Complete scoring (Scenario 1 up to step 7)
2. Record initial metrics
3. Deploy 5 patches in sequence:
   - Click deploy, wait completion, verify toast
   - Repeat for 5 different score_ids
4. Navigate to dashboard
5. Verify metrics:
   - Remediated count should be 5
   - Active Risk % should decrease
   - Completed Deployments should be 5

**Expected Outcome:**
- ✓ Each deployment isolated and success
- ✓ Metrics update correctly after each deployment
- ✓ Dashboard reflects cumulative deployments

**Status:** ☐ Pass ☐ Fail

---

## 5. Test Execution Log

### Test Run #1
**Date:** ____________  
**Tester:** ____________  
**Environment:** Windows, Python 3.x, Chrome  
**Duration:** ____________  

| Test Case | Status | Issues | Notes |
|-----------|--------|--------|-------|
| TC-DASH-001 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-DASH-002 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-DASH-004 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-DASH-005 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-PRIO-001 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-PRIO-002 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-API-002 | ☐ Pass ☐ Fail ☐ Blocked | | |
| TC-API-003 | ☐ Pass ☐ Fail ☐ Blocked | | |

**Summary:** ____________ tests passed, ____________ failed, ____________ blocked

**Critical Issues:** 
1. _____________
2. _____________

**Recommendations:** _____________

---

## 6. Known Issues / Bugs Discovered

### Issue #1
- **Test Case:** TC-DASH-005
- **Severity:** HIGH
- **Description:** Run Scoring button not functional - click does not trigger API call
- **Steps to Reproduce:** Click "Run Scoring" on dashboard
- **Expected:** POST to /api/v1/scoring
- **Actual:** No API call made
- **Root Cause:** Button onclick handler missing or broken in app.js
- **Status:** ☐ Open ☐ In Progress ☐ Resolved
- **Resolution:** _____________

### Issue #2
- **Test Case:** TC-DASH-001
- **Severity:** MEDIUM
- **Description:** CSS syntax errors on dashboard.html lines 81 & 93
- **Error Message:** "property value expected" / "at-rule or selector expected"
- **Impact:** Page may not render correctly in some browsers
- **Root Cause:** Inline style attribute with unterminated template variable
- **Status:** ☐ Open ☐ In Progress ☐ Resolved
- **Resolution:** _____________

### Issue #3
- **Test Case:** TC-PRIO-002
- **Severity:** HIGH
- **Description:** Score calculation returns 0.0 for all values
- **Expected:** Scores > 0 calculated using weighted formula
- **Actual:** All scores are 0.0 despite valid input data
- **Root Cause:** Scoring formula not applied correctly in calculate_priority_scores()
- **Impact:** Prevents proper prioritization of patches
- **Status:** ☐ Open ☐ In Progress ☐ Resolved
- **Resolution:** _____________

### Issue #4
- **Test Case:** TC-DASH-007, TC-DASH-008, TC-DASH-009
- **Severity:** MEDIUM
- **Description:** Navigation buttons missing from dashboard bottom
- **Expected:** Three buttons: "View Vulnerabilities", "View Devices", "View Patches"
- **Actual:** Buttons not present on page
- **Impact:** Users cannot navigate to detail pages from dashboard
- **Status:** ☐ Open ☐ In Progress ☐ Resolved
- **Resolution:** Add bottom navigation section to dashboard.html template

---

## 7. Test Metrics

### Test Coverage Summary

| Module | Test Cases | Passed | Failed | Blocked | Coverage |
|--------|-----------|--------|--------|---------|----------|
| Dashboard | 9 | ___ | ___ | ___ | __% |
| Vulnerabilities | 3 | ___ | ___ | ___ | __% |
| Devices | 2 | ___ | ___ | ___ | __% |
| Patches | 1 | ___ | ___ | ___ | __% |
| Priorities | 5 | ___ | ___ | ___ | __% |
| API Endpoints | 6 | ___ | ___ | ___ | __% |
| Error Handling | 4 | ___ | ___ | ___ | __% |
| UI/UX | 3 | ___ | ___ | ___ | __% |
| **TOTAL** | **33** | **___** | **___** | **___** | **__%** |

### Defect Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | ___ | Open/In Progress/Resolved |
| High | ___ | Open/In Progress/Resolved |
| Medium | ___ | Open/In Progress/Resolved |
| Low | ___ | Open/In Progress/Resolved |

---

## 8. Browser Compatibility Testing

| Browser | Version | Result | Notes |
|---------|---------|--------|-------|
| Chrome | 120+ | ☐ Pass ☐ Fail | |
| Firefox | 121+ | ☐ Pass ☐ Fail | |
| Edge | 120+ | ☐ Pass ☐ Fail | |
| Safari | 17+ | ☐ Pass ☐ Fail | (Optional for MVP) |

---

## 9. Performance Testing (Optional)

### Page Load Times

| Page | Target | Actual | Status |
|------|--------|--------|--------|
| Dashboard | < 2s | ___ | ☐ Pass ☐ Fail |
| Vulnerabilities | < 1s | ___ | ☐ Pass ☐ Fail |
| Priorities | < 1s | ___ | ☐ Pass ☐ Fail |

### API Response Times

| Endpoint | Target | Actual | Status |
|----------|--------|--------|--------|
| /api/v1/ingest | < 2s | ___ | ☐ Pass ☐ Fail |
| /api/v1/scoring | < 3s | ___ | ☐ Pass ☐ Fail |
| /api/v1/priorities | < 1s | ___ | ☐ Pass ☐ Fail |

---

## 10. Acceptance Criteria

For system to be considered **Ready for Production:**

- ✓ All 33 test cases pass
- ✓ 0 critical/high severity bugs remaining
- ✓ Dashboard metrics calculate correctly
- ✓ Score values > 0 (not all 0.0)
- ✓ Navigation functional
- ✓ Deployment simulation completes successfully
- ✓ Toast notifications display correctly
- ✓ No console errors during test scenarios
- ✓ Database integrity maintained through workflow
- ✓ CSS renders correctly (no style errors)

---

## 11. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Test Lead | _____________ | __________ | _____ |
| QA Manager | _____________ | __________ | _____ |
| Product Owner | _____________ | __________ | _____ |

---

**End of Functional Test Documentation**

## Recent Changes (Aug 2026)

- Approval-first deployment flow: Deployments require an approval step via `POST /api/v1/deploy/{score_id}/approve` before completion.
- Deployment audit page: `/deployments` lists `Deployment_Actions` including `status`, `approver`, and `timestamp`.
- Duplicate safeguards: Scoring prevents duplicate `dv_id` re-scoring; deployments prevent duplicate completed actions.
- Demo helper: `scripts/demo_workflow.py` available to run a local ingest→score→approve→deploy demo.
