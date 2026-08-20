from database.db import get_connection
import json
import logging

logger = logging.getLogger(__name__)

# Workflow example (mocked, self-contained):
# 1) Ingest mock data (data/defender_mock.json) via `ingest_all_data()`
# 2) Run `calculate_priority_scores()` to compute scores (skips already-scored dv_id pairs)
# 3) Call `get_priority_list()` to view prioritized items in the UI
# 4) Simulate a deployment with `simulate_deployment(score_id)` which records status, timestamp, and approver
#
# This example demonstrates how a single vulnerability moves through the full workflow using
# only the repository's mock data. The functions below contain inline checks and logging
# to help future contributors understand where duplicates are skipped and where data issues
# are handled gracefully.

def calculate_priority_scores():
    conn = get_connection()
    cur = conn.cursor()

    # NOTE: Do not blindly clear scores. Instead, only insert scores for device-vuln pairs
    # that don't already exist in Priority_Scores to prevent duplicate scoring.

    # Load patches
    cur.execute("SELECT patch_id, severity, cve_ids FROM Patches")
    patches = {}
    for p in cur.fetchall():
        cve_ids = json.loads(p["cve_ids"])
        for cve in cve_ids:
            patches[cve] = {"patch_id": p["patch_id"], "severity": p["severity"]}

    cur.execute("""
        SELECT dv.dv_id, d.device_id, d.criticality, v.cve_id, v.cvss, v.severity as vuln_severity
        FROM Device_Vulnerabilities dv
        JOIN Devices d ON dv.device_id = d.device_id
        JOIN Vulnerabilities v ON dv.vuln_id = v.vuln_id
    """)

    rows = cur.fetchall()

    criticality_map = {"High": 10, "Medium": 6, "Low": 2}
    severity_map = {"Critical": 10, "High": 8, "Medium": 5, "Low": 2}

    for row in rows:
        try:
            # convert sqlite3.Row to plain dict for uniform access
            if hasattr(row, 'keys'):
                row = dict(row)
            # Defensive checks for malformed or missing fields
            dv_id = row.get("dv_id") if isinstance(row, dict) else row[0]
            if dv_id is None:
                logger.warning("Skipping row with missing dv_id: %s", dict(row))
                continue

            criticality_weight = criticality_map.get(row.get("criticality"), 1)
            severity_weight = severity_map.get(row.get("vuln_severity"), 1)

            # cvss may be None or non-numeric; coerce safely
            try:
                exploit_likelihood = float(row.get("cvss") or 0)
            except (TypeError, ValueError):
                logger.warning("Invalid cvss for dv_id %s: %s", dv_id, row.get("cvss"))
                exploit_likelihood = 0.0

            # Scoring formula
            score = (severity_weight * 0.5) + (exploit_likelihood * 0.3) + (criticality_weight * 0.2)

            if score >= 8:
                priority = "Critical"
            elif score >= 6:
                priority = "High"
            elif score >= 4:
                priority = "Medium"
            else:
                priority = "Low"

            patch_info = patches.get(row.get("cve_id"))
            patch_id = patch_info["patch_id"] if patch_info else None

            reason = f"Severity={severity_weight}, Exploitability={exploit_likelihood}, Criticality={criticality_weight}"

            # Duplicate prevention: skip if this device-vulnerability pair already has a score
            cur.execute("SELECT 1 FROM Priority_Scores WHERE dv_id = ?", (dv_id,))
            if cur.fetchone():
                logger.info("Skipping dv_id %s; score already exists", dv_id)
                continue

            cur.execute("""
                INSERT INTO Priority_Scores (dv_id, patch_id, score_value, priority, score_reason)
                VALUES (?, ?, ?, ?, ?)
            """, (dv_id, patch_id, score, priority, reason))
        except Exception as e:
            # Log and continue on errors to make scoring robust to malformed data
            logger.exception("Failed to score row %s: %s", dict(row), e)

    conn.commit()
    conn.close()

def get_priority_list():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT ps.score_id,
               ps.score_value,
               ps.priority,
               ps.patch_id,
               d.device_id,
               v.id as vulnerability_id,
               d.hostname,
               v.cve_id,
               v.severity,
               COALESCE(da.status, da.action_status, 'Pending') AS action_status,
               da.approver,
               da.timestamp
        FROM Priority_Scores ps
        JOIN Device_Vulnerabilities dv ON ps.dv_id = dv.dv_id
        JOIN Devices d ON dv.device_id = d.device_id
        JOIN Vulnerabilities v ON dv.vuln_id = v.vuln_id
        LEFT JOIN (
            SELECT score_id, action_status, status, approver, timestamp
            FROM Deployment_Actions
            WHERE action_id IN (
                SELECT MAX(action_id) FROM Deployment_Actions GROUP BY score_id
            )
        ) da ON ps.score_id = da.score_id
        ORDER BY ps.score_value DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def simulate_deployment(score_id: int):
    conn = get_connection()
    cur = conn.cursor()
    # Prevent duplicate *completed* deployments for the same score_id
    cur.execute("SELECT 1 FROM Deployment_Actions WHERE score_id = ? AND LOWER(COALESCE(status, action_status)) = 'completed'", (score_id,))
    if cur.fetchone():
        conn.close()
        logger.warning("Duplicate completed deployment blocked for score_id %s", score_id)
        raise ValueError(f"Deployment already completed for score_id {score_id}")

    # Ensure an approval record exists for this score_id before completing
    cur.execute("SELECT approver FROM Deployment_Actions WHERE score_id = ? AND LOWER(status) = 'approved' ORDER BY action_id DESC LIMIT 1", (score_id,))
    aprow = cur.fetchone()
    if not aprow:
        conn.close()
        logger.warning("Attempted to complete deployment without approval for score_id %s", score_id)
        raise ValueError(f"Deployment for score_id {score_id} must be approved before completion")

    approver = aprow[0]

    # Record the deployment — mark as completed and carry approver from the approval action
    cur.execute("""
        INSERT INTO Deployment_Actions (score_id, action_status, status, approver)
        VALUES (?, ?, ?, ?)
    """, (score_id, "Completed", "completed", approver))
    conn.commit()
    conn.close()


def approve_deployment(score_id: int, approver: str):
    """Record a human approver for a pending deployment.

    Inserts an action with status='approved' and the approver name. Does not mark
    the deployment as completed; a separate call to `simulate_deployment` is required.
    """
    if not approver or not approver.strip():
        raise ValueError("Approver name is required")

    conn = get_connection()
    cur = conn.cursor()
    # Prevent duplicate approval if already approved by same approver
    cur.execute("SELECT 1 FROM Deployment_Actions WHERE score_id = ? AND LOWER(status) = 'approved'", (score_id,))
    if cur.fetchone():
        conn.close()
        raise ValueError(f"Score_id {score_id} already has an approval recorded")

    cur.execute("""
        INSERT INTO Deployment_Actions (score_id, action_status, status, approver)
        VALUES (?, ?, ?, ?)
    """, (score_id, "Approved", "approved", approver))
    conn.commit()
    conn.close()

def get_score_detail(score_id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ps.score_id,
               ps.score_value,
               ps.priority,
               ps.patch_id,
               ps.score_reason,
               d.device_id,
               d.hostname,
               d.criticality,
               v.cve_id,
               v.severity,
               v.cvss,
               v.description,
               COALESCE(da.status, da.action_status, 'Pending') AS action_status,
               da.approver,
               da.timestamp
        FROM Priority_Scores ps
        JOIN Device_Vulnerabilities dv ON ps.dv_id = dv.dv_id
        JOIN Devices d ON dv.device_id = d.device_id
        JOIN Vulnerabilities v ON dv.vuln_id = v.vuln_id
        LEFT JOIN (
            SELECT score_id, action_status, status, approver, timestamp
            FROM Deployment_Actions
            WHERE action_id IN (
                SELECT MAX(action_id) FROM Deployment_Actions GROUP BY score_id
            )
        ) da ON ps.score_id = da.score_id
        WHERE ps.score_id = ?
    """, (score_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        return {"error": "Score not found"}

def export_priorities_csv():
    import io
    import csv
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
         SELECT ps.score_value,
             ps.priority,
             d.hostname,
             v.cve_id,
             p.patch_id,
             COALESCE(da.status, da.action_status, 'Pending') AS action_status
        FROM Priority_Scores ps
        JOIN Device_Vulnerabilities dv ON ps.dv_id = dv.dv_id
        JOIN Devices d ON dv.device_id = d.device_id
        JOIN Vulnerabilities v ON dv.vuln_id = v.vuln_id
        LEFT JOIN Patches p ON ps.patch_id = p.patch_id
        LEFT JOIN (
            SELECT score_id, action_status, status, approver, timestamp
            FROM Deployment_Actions
            WHERE action_id IN (
                SELECT MAX(action_id) FROM Deployment_Actions GROUP BY score_id
            )
        ) da ON ps.score_id = da.score_id
        ORDER BY ps.score_value DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Score', 'Priority', 'Hostname', 'CVE ID', 'Patch ID', 'Status'])
    
    # Write data rows
    for row in rows:
        writer.writerow([
            round(row['score_value'], 1),
            row['priority'],
            row['hostname'],
            row['cve_id'],
            row['patch_id'] or 'N/A',
            row['action_status']
        ])
    
    return output.getvalue()


def get_deployment_actions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT action_id, score_id, COALESCE(status, action_status) as status, action_status, approver, timestamp
        FROM Deployment_Actions
        ORDER BY timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]