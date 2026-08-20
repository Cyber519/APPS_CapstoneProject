import tempfile
import os
from pathlib import Path
import sqlite3
import pytest

import database.db as dbmod
from services import scoring_service


def setup_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    db_path = Path(tmp.name)
    dbmod.DB_PATH = db_path
    # initialize schema
    dbmod.init_db()
    return db_path


def teardown_temp_db(path: Path):
    try:
        os.unlink(path)
    except Exception:
        pass


def test_scoring_handles_missing_and_malformed_fields():
    db_path = setup_temp_db()
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Insert a device
        cur.execute("INSERT INTO Devices (device_id, hostname, os, criticality) VALUES ('dev1', 'host1', 'Windows', 'High')")
        # Insert vulnerability with missing cvss and severity
        cur.execute("INSERT INTO Vulnerabilities (id, cve_id, severity, cvss, description) VALUES (?,?,?,?,?)",
                    ( 'v1', 'CVE-0001', None, None, 'Missing cvss and severity' ))
        vuln_id = cur.lastrowid
        # Link device to vulnerability
        cur.execute("INSERT INTO Device_Vulnerabilities (device_id, vuln_id) VALUES (?,?)", ('dev1', vuln_id))
        dv_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Should not raise
        scoring_service.calculate_priority_scores()

        # After scoring, check that either a score exists or the system skipped gracefully
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Priority_Scores WHERE dv_id = ?", (dv_id,))
        count = cur.fetchone()[0]
        # count is 0 or 1 depending on mapping; ensure no crash and type safety
        assert count in (0, 1)
        conn.close()
    finally:
        teardown_temp_db(db_path)


def test_duplicate_scoring_is_prevented():
    db_path = setup_temp_db()
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO Devices (device_id, hostname, os, criticality) VALUES ('dev2', 'host2', 'Linux', 'Medium')")
        cur.execute("INSERT INTO Vulnerabilities (id, cve_id, severity, cvss, description) VALUES (?,?,?,?,?)",
                    ('v2','CVE-0002','High',7.5,'Test vuln'))
        vuln_id = cur.lastrowid
        cur.execute("INSERT INTO Device_Vulnerabilities (device_id, vuln_id) VALUES (?,?)", ('dev2', vuln_id))
        dv_id = cur.lastrowid
        # Manually insert an existing score for this dv
        cur.execute("INSERT INTO Priority_Scores (dv_id, patch_id, score_value, priority, score_reason) VALUES (?,?,?,?,?)",
                    (dv_id, None, 7.0, 'High', 'preinserted'))
        conn.commit()
        conn.close()

        # Now run scoring - it should skip the dv_id and not insert a duplicate
        scoring_service.calculate_priority_scores()

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Priority_Scores WHERE dv_id = ?", (dv_id,))
        count = cur.fetchone()[0]
        assert count == 1
        conn.close()
    finally:
        teardown_temp_db(db_path)


def test_duplicate_deployment_blocked():
    db_path = setup_temp_db()
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Insert minimal score record
        cur.execute("INSERT INTO Devices (device_id, hostname, os, criticality) VALUES ('dev3', 'host3', 'Linux', 'Low')")
        cur.execute("INSERT INTO Vulnerabilities (id, cve_id, severity, cvss, description) VALUES (?,?,?,?,?)",
                    ('v3','CVE-0003','Low',2.0,'vuln'))
        vuln_id = cur.lastrowid
        cur.execute("INSERT INTO Device_Vulnerabilities (device_id, vuln_id) VALUES (?,?)", ('dev3', vuln_id))
        dv_id = cur.lastrowid
        cur.execute("INSERT INTO Priority_Scores (dv_id, patch_id, score_value, priority, score_reason) VALUES (?,?,?,?,?)",
                    (dv_id, None, 2.0, 'Low', 'initial'))
        score_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Require approval before completing deployment
        scoring_service.approve_deployment(score_id, 'test-approver')

        # First completion should succeed
        scoring_service.simulate_deployment(score_id)

        # Second completion should raise ValueError due to duplicate completed deployment
        with pytest.raises(ValueError):
            scoring_service.simulate_deployment(score_id)

    finally:
        teardown_temp_db(db_path)
