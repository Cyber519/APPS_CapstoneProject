from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database.db import init_db, get_connection
from api.defender_api import router as defender_router
from api.kace_api import router as kace_router
from api.priorities_api import router as priorities_router

app = FastAPI(title="APPS")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(defender_router, prefix="/api/v1")
app.include_router(kace_router, prefix="/api/v1")
app.include_router(priorities_router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "APPS API running"}

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard(request: Request):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM Devices")
    devices = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM Vulnerabilities")
    total_vulns = cur.fetchone()["c"]
    cur.execute("""
        SELECT COUNT(*) AS c FROM Vulnerabilities WHERE severity = 'Critical'
    """)
    critical = cur.fetchone()["c"]
    cur.execute("""
        SELECT COUNT(*) AS c
        FROM Deployment_Actions
        WHERE action_status = 'Completed'
    """)
    deployed = cur.fetchone()["c"]
    cur.execute("""
        SELECT COUNT(*) AS c
        FROM Priority_Scores ps
        JOIN Deployment_Actions da ON ps.score_id = da.score_id
        WHERE da.action_status = 'Completed'
    """)
    remediated = cur.fetchone()["c"]
    cur.execute("""
        SELECT COUNT(*) AS c
        FROM Device_Vulnerabilities dv
        WHERE dv.dv_id NOT IN (
            SELECT ps.dv_id
            FROM Priority_Scores ps
            JOIN Deployment_Actions da ON ps.score_id = da.score_id
            WHERE da.action_status = 'Completed'
        )
    """)
    active_vulns = cur.fetchone()["c"]
    cur.execute("""
        SELECT priority, COUNT(*) AS c
        FROM Priority_Scores
        GROUP BY priority
    """)
    priority_counts = {row["priority"]: row["c"] for row in cur.fetchall()}
    conn.close()

    active_risk_percent = round((active_vulns / total_vulns) * 100, 1) if total_vulns else 0
    remediation_percent = round((remediated / total_vulns) * 100, 1) if total_vulns else 0
    response_percent = round((deployed / total_vulns) * 100, 1) if total_vulns else 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "devices": devices,
        "total_vulns": total_vulns,
        "active_vulns": active_vulns,
        "remediated": remediated,
        "critical": critical,
        "deployed": deployed,
        "active_risk_percent": active_risk_percent,
        "remediation_percent": remediation_percent,
        "response_percent": response_percent,
        "priority_critical": priority_counts.get('Critical', 0),
        "priority_high": priority_counts.get('High', 0),
        "priority_medium": priority_counts.get('Medium', 0),
        "priority_low": priority_counts.get('Low', 0)
    })

@app.get("/vulnerabilities")
def vulnerabilities(request: Request):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT v.*, COUNT(dv.device_id) as device_count
        FROM Vulnerabilities v
        LEFT JOIN Device_Vulnerabilities dv ON v.vuln_id = dv.vuln_id
        GROUP BY v.vuln_id
    """)
    vulnerabilities = [dict(r) for r in cur.fetchall()]
    conn.close()
    return templates.TemplateResponse("vulnerabilities.html", {"request": request, "vulnerabilities": vulnerabilities})

@app.get("/devices")
def devices(request: Request):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Devices")
    devices = [dict(r) for r in cur.fetchall()]
    conn.close()
    return templates.TemplateResponse("devices.html", {"request": request, "devices": devices})

@app.get("/patches")
def patches(request: Request):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT patch_id, title, severity, reboot_required FROM Patches")
    patches = [dict(r) for r in cur.fetchall()]
    conn.close()
    return templates.TemplateResponse("patches.html", {"request": request, "patches": patches})

@app.get("/priorities")
def priorities(request: Request):
    from services.scoring_service import get_priority_list
    priorities = get_priority_list()
    return templates.TemplateResponse("priorities.html", {"request": request, "priorities": priorities})