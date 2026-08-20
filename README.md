# APPS - Automated Patch Prioritization System

A full-stack web application for prioritizing patch deployments based on vulnerability severity, device criticality, and other factors.

This repository includes recent enhancements: a documented end-to-end demo, a color-coded UI mapping, an approval workflow for deployments, duplicate-prevention safeguards, an audit trail for deployment actions, and data-quality tests.

For full, up-to-date documentation including API reference, demo instructions, UI notes, and testing steps, see DOCUMENTATION.md in the repository root.

## Features

- **Mock Data Integration**: Uses simulated data from Defender and KACE APIs
- **Scoring Engine**: Calculates priority scores using CVSS, device criticality, patch severity, exploit likelihood, and vulnerability age
- **Web Dashboard**: HTML/JS frontend for viewing vulnerabilities, devices, patches, and prioritization results
- **SQLite Database**: Stores processed data locally
- **Animation**: UI animations for scoring and priority display

## Project Structure

```
APPS_Project/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── database/
│   ├── db.py              # Database connection utilities
│   └── schema.sql         # SQLite schema
├── services/
│   ├── ingestion_service.py  # Data ingestion from JSON
│   └── scoring_service.py    # Priority scoring logic
├── api/
│   ├── defender_api.py     # Vulnerability endpoints
│   ├── kace_api.py         # Device/patch endpoints
│   └── priorities_api.py   # Scoring and prioritization
├── data/
│   ├── defender_mock.json  # Mock vulnerability data
│   ├── kace_devices.json   # Mock device inventory
│   └── kace_patches.json   # Mock patch metadata
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS and JS files
└── README.md
```

## Setup Instructions

1. **Clone or download the project**:
   ```bash
   cd APPS_Project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Open in browser**:
   - Dashboard: http://localhost:8000/dashboard
   - API docs: http://localhost:8000/docs

## Usage

1. **Ingest Data**: Click "Ingest Data" to load mock data into the database
2. **Run Scoring**: Click "Run Scoring" to calculate priority scores (with loading animation)
3. **View Results**: Navigate to Priorities to see ranked patch priorities with animated scores
4. **Simulate Deployment**: Click "Simulate Deploy" on any priority item

## API Endpoints

- `GET /api/v1/vulnerabilities` - Get vulnerability data
- `GET /api/v1/devices-mock` - Get device inventory
- `GET /api/v1/patches-mock` - Get patch metadata
- `POST /api/v1/ingest` - Ingest data from JSON files
- `POST /api/v1/score` - Calculate priority scores
- `GET /api/v1/priorities` - Get prioritization results
- `POST /api/v1/deploy/{score_id}` - Simulate deployment

## Scoring Formula

Priority Score = (CVSS × 0.4) + (Device Criticality Weight × 0.3) + (Patch Severity Weight × 0.2) + (Exploit Likelihood × 0.1) + Age Factor

- **Device Criticality**: High=10, Medium=6, Low=2
- **Patch Severity**: Critical=10, High=8, Medium=5, Low=2
- **Exploit Likelihood**: Based on CVSS score
- **Age Factor**: Fixed value (5)

**Priority Levels**:
- Critical: 80-100
- High: 60-79
- Medium: 40-59
- Low: 0-39

## Extending Mock Data

Edit the JSON files in the `data/` directory to add more mock data:

- `defender_mock.json`: Add vulnerabilities with id, cve, severity, cvss, description, affected_products
- `kace_devices.json`: Add devices with device_id, hostname, criticality, os, installed_patches
- `kace_patches.json`: Add patches with patch_id, title, severity, reboot_required, supersedes, cve_ids

After editing, re-run the ingest process.

## Technologies Used

- **Backend**: FastAPI, SQLite, Python
- **Frontend**: HTML, CSS, JavaScript
- **Templates**: Jinja2
- **Data**: JSON mock files