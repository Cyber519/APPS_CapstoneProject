PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Devices (
    device_id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    os TEXT,
    criticality TEXT
);

CREATE TABLE IF NOT EXISTS Vulnerabilities (
    vuln_id INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT,
    cve_id TEXT NOT NULL,
    severity TEXT,
    cvss REAL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Patches (
    patch_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    severity TEXT,
    reboot_required BOOLEAN,
    supersedes TEXT,
    cve_ids TEXT
);

CREATE TABLE IF NOT EXISTS Device_Vulnerabilities (
    dv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    vuln_id INTEGER NOT NULL,
    FOREIGN KEY (device_id) REFERENCES Devices(device_id),
    FOREIGN KEY (vuln_id) REFERENCES Vulnerabilities(vuln_id)
);

CREATE TABLE IF NOT EXISTS Priority_Scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dv_id INTEGER NOT NULL,
    patch_id TEXT,
    score_value REAL,
    priority TEXT,
    score_reason TEXT,
    FOREIGN KEY (dv_id) REFERENCES Device_Vulnerabilities(dv_id),
    FOREIGN KEY (patch_id) REFERENCES Patches(patch_id)
);

CREATE TABLE IF NOT EXISTS Deployment_Actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    score_id INTEGER NOT NULL,
    -- New schema: support explicit `status` values and record who approved
    -- `status` values: pending, approved, completed, failed
    action_status TEXT,
    status TEXT,
    approver TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (score_id) REFERENCES Priority_Scores(score_id)
);