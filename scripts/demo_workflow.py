"""Demo script: run end-to-end workflow using mock data.

Steps executed:
- init_db() to (re)create schema
- ingest_all_data() to load mock JSONs
- calculate_priority_scores()
- print top priorities via get_priority_list()
- pick first score, show detail via get_score_detail()
- simulate_deployment(score_id)
- show detail again to display approver/timestamp

Run with the workspace Python:
c:/Users/zakiy/Documents/APPS_Project/.venv/Scripts/python.exe scripts/demo_workflow.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so local modules can be imported when running the script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db, get_connection
from services.ingestion_service import ingest_all_data
from services.scoring_service import calculate_priority_scores, get_priority_list, get_score_detail, simulate_deployment
import json

def print_div():
    print('\n' + '-'*60 + '\n')

if __name__ == '__main__':
    print('Initializing database schema...')
    # Remove existing DB so schema changes (new columns) are applied cleanly for the demo
    db_file = PROJECT_ROOT / 'apps.db'
    if db_file.exists():
        try:
            db_file.unlink()
            print('Removed existing apps.db to ensure fresh schema')
        except Exception as e:
            print('Warning: could not remove apps.db:', e)

    init_db()

    print('Ingesting mock data...')
    ingest_all_data()

    print('Calculating priority scores...')
    calculate_priority_scores()

    print_div()
    print('Top priority list (first 5):')
    priorities = get_priority_list()
    for p in priorities[:5]:
        print(json.dumps(p, default=str, indent=2))

    if not priorities:
        print('No priorities available; aborting demo.')
        exit(0)

    first = priorities[0]
    score_id = first['score_id']

    print_div()
    print(f'Detail before deployment for score_id={score_id}:')
    detail_before = get_score_detail(score_id)
    print(json.dumps(detail_before, default=str, indent=2))

    print_div()
    print(f'Simulating deployment for score_id={score_id}...')
    try:
        simulate_deployment(score_id)
        print('Deployment simulated successfully.')
    except Exception as e:
        print('Deployment failed or prevented:', str(e))

    print_div()
    print(f'Detail after deployment for score_id={score_id}:')
    detail_after = get_score_detail(score_id)
    print(json.dumps(detail_after, default=str, indent=2))

    print_div()
    print('Demo complete.')
