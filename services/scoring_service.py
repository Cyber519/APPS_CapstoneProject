from database.db import get_connection
import json

def calculate_priority_scores():
    conn = get_connection()
    cur = conn.cursor()

    # Clear old scores
    cur.execute("DELETE FROM Priority_Scores")

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
        criticality_weight = criticality_map.get(row["criticality"], 1)
        
        patch_info = patches.get(row["cve_id"])
        if patch_info:
            patch_id = patch_info["patch_id"]
            patch_severity = patch_info["severity"]
            patch_weight = severity_map.get(patch_severity, 1)
        else:
            patch_id = None
            patch_weight = 1
        
        exploit_likelihood = row["cvss"]  # 0-10
        age_factor = 5  # fake
        
        score = (row["cvss"] * 4) + (criticality_weight * 3) + (patch_weight * 2) + exploit_likelihood + age_factor
        
        if score >= 80:
            priority = "Critical"
        elif score >= 60:
            priority = "High"
        elif score >= 40:
            priority = "Medium"
        else:
            priority = "Low"
        
        reason = f"CVSS={row['cvss']}, Criticality={row['criticality']}, PatchSeverity={patch_severity if patch_info else 'N/A'}, Exploit={exploit_likelihood}, Age={age_factor}"

        cur.execute("""
            INSERT INTO Priority_Scores (dv_id, patch_id, score_value, priority, score_reason)
            VALUES (?, ?, ?, ?, ?)
        """, (row["dv_id"], patch_id, score, priority, reason))

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
               COALESCE(da.action_status, 'Pending') AS action_status
        FROM Priority_Scores ps
        JOIN Device_Vulnerabilities dv ON ps.dv_id = dv.dv_id
        JOIN Devices d ON dv.device_id = d.device_id
        JOIN Vulnerabilities v ON dv.vuln_id = v.vuln_id
        LEFT JOIN (
            SELECT score_id, action_status
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
    cur.execute("""
        INSERT INTO Deployment_Actions (score_id, action_status)
        VALUES (?, ?)
    """, (score_id, "Completed"))
    conn.commit()
    conn.close()