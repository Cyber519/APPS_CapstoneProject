# Technical Design Document (TDD)
## Automated Patch Prioritization System (APPS)

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Status:** In Development  
**Author:** Development Team

---

## 1. Executive Summary

The Automated Patch Prioritization System (APPS) is a web-based application designed to analyze security vulnerabilities across managed devices and intelligently prioritize patch deployment based on risk scoring algorithms. The system combines data from multiple security sources (Microsoft Defender, KACE), applies weighted scoring logic, and provides a cybersecurity dashboard for risk visualization and deployment management.

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (HTML/JS/CSS)              │
│  Dashboard | Vulnerabilities | Patches | Devices | Priorities│
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP/REST Calls
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend (main.py)                  │
│  Routes: /dashboard, /vulnerabilities, /api/v1/*            │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼──────┐        ┌───▼──────┐        ┌───▼──────┐
    │Defender  │        │KACE      │        │Priorities│
    │API       │        │API       │        │API       │
    │Router    │        │Router    │        │Router    │
    └───┬──────┘        └───┬──────┘        └───┬──────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │     Services Layer                      │
        │ ├─ Ingestion Service                    │
        │ ├─ Scoring Service                      │
        │ └─ Deployment Service                   │
        └────────────────────┬────────────────────┘
                             │
        ┌────────────────────▼────────────────────┐
        │     SQLite Database Layer               │
        │ ├─ Devices                              │
        │ ├─ Vulnerabilities                      │
        │ ├─ Patches                              │
        │ ├─ Device_Vulnerabilities               │
        │ ├─ Priority_Scores                      │
        │ └─ Deployment_Actions                   │
        └─────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | FastAPI | 0.104+ |
| **Server** | Uvicorn | 0.24+ |
| **Database** | SQLite 3 | Built-in |
| **Template Engine** | Jinja2 | 3.1+ |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Latest |
| **Python** | Python | 3.8+ |

---

## 3. Component Design

### 3.1 Database Schema

#### **Devices Table**
```sql
CREATE TABLE Devices (
    device_id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    os TEXT,
    criticality TEXT  -- Values: 'High', 'Medium', 'Low'
);
```
**Purpose:** Stores managed devices needing patch management  
**Key Fields:** device_id (unique identifier), criticality (assets importance rating)

#### **Vulnerabilities Table**
```sql
CREATE TABLE Vulnerabilities (
    vuln_id INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT,
    cve_id TEXT NOT NULL,
    severity TEXT,  -- Values: 'Critical', 'High', 'Medium', 'Low'
    cvss REAL,      -- Score 0-10
    description TEXT
);
```
**Purpose:** Tracks known vulnerabilities affecting managed devices  
**Key Fields:** cvss (critical for scoring), severity (security rating)

#### **Patches Table**
```sql
CREATE TABLE Patches (
    patch_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    severity TEXT,  -- Values: 'Critical', 'High', 'Medium', 'Low'
    reboot_required BOOLEAN,
    supersedes TEXT,
    cve_ids TEXT    -- JSON array of CVE IDs
);
```
**Purpose:** Available patches addressing vulnerabilities  
**Key Fields:** patch_id (unique), severity (patch criticality), cve_ids (vulnerability mapping)

#### **Device_Vulnerabilities Junction Table**
```sql
CREATE TABLE Device_Vulnerabilities (
    dv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    vuln_id INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES Devices(device_id),
    FOREIGN KEY (vuln_id) REFERENCES Vulnerabilities(vuln_id)
);
```
**Purpose:** Many-to-many relationship between devices and vulnerabilities  
**Usage:** Identifies which vulnerabilities affect which devices

#### **Priority_Scores Table**
```sql
CREATE TABLE Priority_Scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dv_id INTEGER NOT NULL,
    patch_id TEXT,
    score_value REAL,
    priority TEXT,  -- Values: 'Critical', 'High', 'Medium', 'Low'
    score_reason TEXT,
    FOREIGN KEY (dv_id) REFERENCES Device_Vulnerabilities(dv_id),
    FOREIGN KEY (patch_id) REFERENCES Patches(patch_id)
);
```
**Purpose:** Calculated priority scores for each device-vulnerability combination  
**Usage:** Drives prioritization logic; associates calculated score with deployment

#### **Deployment_Actions Table**
```sql
CREATE TABLE Deployment_Actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    score_id INTEGER NOT NULL,
    action_status TEXT,  -- Values: 'Pending', 'In Progress', 'Completed', 'Failed'
    deployment_date TIMESTAMP,
    FOREIGN KEY (score_id) REFERENCES Priority_Scores(score_id)
);
```
**Purpose:** Tracks deployment actions and their status  
**Usage:** Records patch installation attempts and outcomes

---

### 3.2 API Router Design

#### **3.2.1 Defender API Router** (`api/defender_api.py`)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/ingest/defender` | POST | Load mock defender vulnerability data | `{status: "success", count: int}` |
| `/ingest/defender/devices` | GET | Retrieve ingested defender devices | `{devices: Array}` |

**Data Flow:**
1. Load `defender_mock.json`
2. Parse vulnerability data
3. Insert into Vulnerabilities table
4. Create Device_Vulnerabilities associations

#### **3.2.2 KACE API Router** (`api/kace_api.py`)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/ingest/kace/devices` | POST | Load KACE managed device inventory | `{status: "success", count: int}` |
| `/ingest/kace/patches` | POST | Load available patches | `{status: "success", count: int}` |

**Data Flow:**
1. Load `kace_devices.json` and `kace_patches.json`
2. Parse device inventory and patch data
3. Insert into Devices and Patches tables

#### **3.2.3 Priorities API Router** (`api/priorities_api.py`)

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/ingest` | POST | Trigger complete data ingestion | `{status: "success"}` |
| `/scoring` | POST | Calculate priority scores | `{status: "success", scores_calculated: int}` |
| `/priorities` | GET | Retrieve scored prioritization results | `{priorities: Array}` |
| `/deploy/<score_id>` | POST | Record deployment action | `{status: "success"}` |

**Data Flow:**
1. `/ingest`: Calls defender and KACE ingest endpoints
2. `/scoring`: Calls scoring_service.calculate_priority_scores()
3. `/priorities`: Returns Priority_Scores table sorted by priority
4. `/deploy`: Updates Deployment_Actions status to 'Completed'

---

### 3.3 Services Layer

#### **3.3.1 Scoring Service** (`services/scoring_service.py`)

**Function:** `calculate_priority_scores()`

**Algorithm:**
```
For each Device-Vulnerability association:
    1. Retrieve CVSS score (0-10)
    2. Get device criticality weight
    3. Get patch severity weight
    4. Get exploit likelihood factor
    5. Apply weighted formula:
       score = (cvss × 4) + (criticality_weight × 3) + 
               (patch_weight × 2) + exploit + age_factor

    6. Classify priority by score range:
       - Critical: score >= 80
       - High: 60 <= score < 80
       - Medium: 40 <= score < 60
       - Low: score < 40

    7. Store in Priority_Scores table
```

**Weights Reference:**
```python
Device Criticality:   High=10, Medium=6, Low=2
Patch Severity:      Critical=10, High=8, Medium=5, Low=2
CVSS Weight:         4.0 (primary driver)
Criticality Weight:  3.0
Patch Severity Weight: 2.0
Exploit Likelihood:  Direct CVSS value
Age Factor:          5.0 (constant, represents patch age)
```

**Output:** Inserted Priority_Scores records with calculated score_value and priority level

#### **3.3.2 Ingestion Service** (`services/ingestion_service.py`)

**Function:** `ingest_data()`

**Steps:**
1. Load `defender_mock.json` → Insert Vulnerabilities
2. Load `kace_devices.json` → Insert Devices
3. Load `kace_patches.json` → Insert Patches
4. Create Device_Vulnerabilities associations
5. Return ingestion summary (count of each entity type)

#### **3.3.3 Deployment Service** (Planned)

**Functions:**
- `simulate_deployment()` - Simulates patch deployment
- `update_deployment_status()` - Updates Deployment_Actions status
- `get_deployment_history()` - Retrieves deployment records

---

### 3.4 Frontend Components

#### **3.4.1 Dashboard (`templates/dashboard.html`)**

**Key Sections:**
1. **Header:** Title and action buttons (Ingest Data, Run Scoring)
2. **Metric Cards:**
   - % Active Risk (red-themed)
   - Open Findings (count of active vulnerabilities)
   - Risk Analysis Progress (% of critical vulnerabilities analyzed)
   - Response Progress (% of vulnerabilities with deployment plans)

3. **Risk Rating Breakdown:**
   - Pie chart visualization (or count boxes) for Critical/High/Medium/Low
   - Aggregated from Priority_Scores table

4. **Response Progress Tracking:**
   - Remediated count (vulnerabilities with 'Completed' deployment status)
   - Completed Deployments (count of successful deployments)

5. **Navigation:** Buttons at bottom for Vulnerabilities, Devices, Patches pages

**Data Binding:** Templates receive context variables from `/dashboard` route

#### **3.4.2 Vulnerabilities Page (`templates/vulnerabilities.html`)**

**Layout:** Table showing:
- CVE ID
- Severity badge (color-coded)
- CVSS Score
- Description
- Affected Devices count
- Available Patch

**Data Source:** JOIN query from Vulnerabilities → Device_Vulnerabilities

#### **3.4.3 Devices Page (`templates/devices.html`)**

**Layout:** Table showing:
- Hostname
- Operating System
- Criticality level (badge)
- Vulnerability count (linked to this device)
- Last Patch date
- Status indicator

**Data Source:** Devices table with JOIN to Device_Vulnerabilities count

#### **3.4.4 Patches Page (`templates/patches.html`)**

**Layout:** Table showing:
- Patch ID / Title
- Severity
- Affected Vulnerabilities count
- Reboot Required indicator
- Deployment count (how many devices deployed)

**Data Source:** Patches table with JOIN statistics

#### **3.4.5 Priorities Page (`templates/priorities.html`)**

**Layout:** Results of scoring showing:
- Device + Vulnerability combination
- Priority level (badge with color)
- Score value
- Recommended Patch
- Deploy button (triggers simulation)

**Interactivity:**
- Score animation (0 → final value over 2 seconds)
- Deploy button shows progress bar (0-100%)
- Completion triggers toast notification
- Row highlighting on deployment completion

---

### 3.5 Static Assets

#### **Styling** (`static/styles.css`)

**Color Scheme (Cybersecurity Dashboard Aesthetic):**
- Background: Dark gray (#1a1a1a, #2d2d2d)
- Primary accent: Cyan (#00d9ff)
- Secondary accent: Blue (#0066ff)
- Critical risk: Red (#ff3333)
- High risk: Orange (#ff9900)
- Medium risk: Yellow (#ffcc00)
- Low risk: Green (#00cc66)

**Key Classes:**
- `.dashboard-page`: Main container
- `.metric-card`: Statistics card styling
- `.progress-track`: Progress bar container
- `.progress-track-fill`: Animated fill element
- `.priority-badge`: Priority level indicator
- `.toast-notification`: Notification styling

**Animations:**
- Score counter animation (number tween)
- Progress bar fill (0-100% over specified duration)
- Fade-in effects on card load
- Pulse effect on critical items

#### **Client Logic** (`static/app.js`)

**Functions:**

| Function | Trigger | Action |
|----------|---------|--------|
| `runIngest()` | "Ingest Data" button click | Calls `/api/v1/ingest`, shows spinner, displays success toast |
| `runScoring()` | "Run Scoring" button click | Calls `/api/v1/scoring`, animates score updates when complete |
| `simulateDeploy()` | Deploy button per row | Shows progress bar 0-100%, updates row status, shows toast |
| `animateScore()` | Called by runScoring() | Number animation from 0 to final value over 2 seconds |
| `showToast()` | Various operations | Displays temporary notification message (3-5 sec auto-dismiss) |
| `updateMetrics()` | Post-deployment | Refreshes dashboard metrics from server |

---

## 4. Data Flow Diagrams

### 4.1 Ingestion Flow

```
Start Ingestion
    ↓
POST /api/v1/ingest (Priorities Router)
    ├─ Load defender_mock.json
    │   ├─ Parse vulnerabilities
    │   └─ Insert → Vulnerabilities table
    │
    ├─ Load kace_devices.json  
    │   ├─ Parse devices
    │   └─ Insert → Devices table
    │
    └─ Load kace_patches.json
        ├─ Parse patches
        └─ Insert → Patches table

Create Device_Vulnerabilities associations
    ├─ Match devices to vulnerabilities
    └─ Insert cross-reference records

Return: {status: "success", ingested_count: X}
```

### 4.2 Scoring Flow

```
User clicks "Run Scoring"
    ↓
POST /api/v1/scoring (Priorities Router)
    ↓
Call calculate_priority_scores() (Scoring Service)
    ├─ Query all Device_Vulnerabilities
    ├─ For each combination:
    │   ├─ Calculate weighted score
    │   ├─ Classify priority
    │   └─ Insert → Priority_Scores table
    ├─ Return count of scores calculated
    │
Frontend receives response
    ├─ Show success toast
    ├─ GET /api/v1/priorities
    ├─ Animate scores 0 → final value
    └─ Refresh dashboard metrics
```

### 4.3 Deployment Simulation Flow

```
User clicks Deploy button on priority row
    ↓
JavaScript simulateDeploy(score_id)
    ├─ Show progress bar
    ├─ Animate 0-100% over 3 seconds
    └─ POST /api/v1/deploy/{score_id}
        ├─ Update Deployment_Actions status = 'Completed'
        └─ Return {status: "success"}

On completion:
    ├─ Show toast: "Deployment complete"
    ├─ Highlight row in green
    ├─ GET /dashboard to refresh metrics
    └─ Update vulnerability count
```

---

## 5. Integration Points

### 5.1 Frontend-Backend Communication

**Request Format:**
- Method: GET/POST
- Headers: `Content-Type: application/json`
- Base URL: `http://localhost:8000`

**Response Format:**
```json
{
    "status": "success" | "error",
    "data": {...} | null,
    "message": "Description"
}
```

### 5.2 Data Import Sources

**Mock Data Files Location:** `/data/`

| File | Source Table | Structure |
|------|--------------|-----------|
| `defender_mock.json` | Vulnerabilities | Array of {cve_id, severity, cvss, ...} |
| `kace_devices.json` | Devices | Array of {device_id, hostname, criticality, ...} |
| `kace_patches.json` | Patches | Array of {patch_id, severity, cve_ids[], ...} |

---

## 6. Error Handling Strategy

### 6.1 Backend Error Responses

| Scenario | HTTP Status | Response |
|----------|------------|----------|
| Route not found | 404 | `{"detail": "Not found"}` |
| Invalid data format | 400 | `{"detail": "Invalid request body"}` |
| Database query error | 500 | `{"detail": "Database error occurred"}` |
| Missing required field | 422 | `{"detail": "Field X is required"}` |

### 6.2 Frontend Error Handling

- Try-catch blocks around all fetch() calls
- User-friendly toast messages for errors
- Console logging for debugging
- Graceful degradation if data unavailable

---

## 7. Performance Considerations

### 7.1 Database Optimization

- **Indexes:** Create on foreign keys and frequently queried columns (severity, priority)
- **Query Optimization:** Use LIMIT for large result sets on dashboard
- **Batch Operations:** Insert operations batched for ingestion

### 7.2 Frontend Performance

- Lazy load data on page navigation
- Cache static assets via StaticFiles mount
- Minimize DOM reflow during animations
- Debounce rapid button clicks

---

## 8. Security Considerations

### 8.1 Current Implementation

- ✓ No authentication hardcoded (login template exists but not enforced)
- ✓ CORS not explicitly configured (same-origin only)
- ✓ No input validation on form fields

### 8.2 Recommended Improvements

- Implement JWT authentication for dashboard routes
- Add CORS middleware with specific allowed origins
- Validate/sanitize all user inputs
- Rate limit API endpoints
- Add SQL injection prevention via parameterized queries (already using ORM-style queries)

---

## 9. Deployment Architecture

### 9.1 Development Environment

```
Local Machine
├─ Python 3.8+ venv
├─ FastAPI server (localhost:8000)
├─ SQLite database (local file)
└─ Static assets served via Uvicorn
```

### 9.2 Production Deployment (Recommended)

```
Deployment Option A: Docker Container
├─ Dockerfile with Python base image
├─ Uvicorn running in container
├─ Volume mount for SQLite persistent storage
└─ Environment variables for config

Deployment Option B: Cloud VM (Azure recommended)
├─ App Service with Python runtime
├─ Azure SQL for production database
├─ Application Insights for monitoring
└─ Application Gateway for SSL/load balancing
```

---

## 10. Scaling Strategy

### 10.1 Database Scaling

- **Current:** SQLite (suitable for ≤ 100k records)
- **Phase 2:** Migrate to PostgreSQL for horizontal scaling
- **Sharding:** By device_id or prioritize by timestamp

### 10.2 Application Scaling

- Implement caching layer (Redis) for frequently accessed queries
- Move scoring calculations to async background job queue (Celery)
- Implement WebSocket for real-time dashboard updates

---

## 11. Testing Strategy

See FTD.md for comprehensive test cases and coverage

---

## 12. Known Limitations

1. Mock data only - no live API integration to actual Defender/KACE
2. No persistent session management
3. SQLite limits concurrent write operations
4. Score animation assumes synchronous calculation
5. No role-based access control

---

## 13. Future Enhancements

- [ ] Real API integration with Microsoft Defender
- [ ] KACE integration with actual API credentials
- [ ] Machine learning model for improved scoring
- [ ] Automated scheduled ingestion
- [ ] Multi-tenant support
- [ ] Mobile dashboard app
- [ ] Email alerts for critical patches
- [ ] Compliance reporting (CIS benchmarks)

---

## 14. Configuration Management

### 14.1 Environment Variables

```
DATABASE_URL=sqlite:///./apps.db
API_KEY=<defender-api-key>
KACE_URL=http://kace-server:8080
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### 14.2 Configuration File

`config.py` (recommended for Phase 2):
- Database connection settings
- API endpoints
- Scoring algorithm weights
- UI theme colors

---

## 15. Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | TBD | ___________ | _____ |
| Project Manager | TBD | ___________ | _____ |
| QA Lead | TBD | ___________ | _____ |

---

**End of Technical Design Document**
