import json
from pathlib import Path
from database.db import get_connection

def ingest_all_data():
    conn = get_connection()
    cur = conn.cursor()

    # Clear existing data for repeatable runs
    cur.executescript("""
        DELETE FROM Deployment_Actions;
        DELETE FROM Priority_Scores;
        DELETE FROM Device_Vulnerabilities;
        DELETE FROM Patches;
        DELETE FROM Vulnerabilities;
        DELETE FROM Devices;
    """)

    # Vulnerabilities
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    with open(DATA_DIR / "defender_mock.json") as f:
        vulns = json.load(f)["vulnerabilities"]

    for v in vulns:
        cur.execute("""
            INSERT INTO Vulnerabilities (id, cve_id, severity, cvss, description)
            VALUES (?, ?, ?, ?, ?)
        """, (v["id"], v["cve"], v["severity"], v["cvss"], v["description"]))

    # Devices
    with open(DATA_DIR / "kace_devices.json") as f:
        devices = json.load(f)["devices"]

    for d in devices:
        cur.execute("""
            INSERT INTO Devices (device_id, hostname, os, criticality)
            VALUES (?, ?, ?, ?)
        """, (d["device_id"], d["hostname"], d["os"], d["criticality"]))

    # Patches
    with open(DATA_DIR / "kace_patches.json") as f:
        patches = json.load(f)["patches"]

    for p in patches:
        cur.execute("""
            INSERT INTO Patches (patch_id, title, severity, reboot_required, supersedes, cve_ids)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (p["patch_id"], p["title"], p["severity"], p["reboot_required"], json.dumps(p["supersedes"]), json.dumps(p["cve_ids"])))

    # Simple device-vuln mapping: match by OS presence in affected_products
    for v in vulns:
        cur.execute("SELECT vuln_id FROM Vulnerabilities WHERE cve_id = ?", (v["cve"],))
        row = cur.fetchone()
        if not row:
            continue
        vuln_id = row["vuln_id"]
        for d in devices:
            if d["os"] in v["affected_products"]:
                cur.execute("""
                    SELECT device_id FROM Devices WHERE hostname = ?
                """, (d["hostname"],))
                drow = cur.fetchone()
                if drow:
                    cur.execute("""
                        INSERT INTO Device_Vulnerabilities (device_id, vuln_id)
                        VALUES (?, ?)
                    """, (drow["device_id"], vuln_id))

    conn.commit()
    conn.close()