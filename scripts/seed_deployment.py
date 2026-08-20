#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure project root is on sys.path so local modules can be imported when running the script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.scoring_service import approve_deployment, simulate_deployment, get_deployment_actions

def main():
    score_id = 1
    approver = "Demo Approver"
    try:
        approve_deployment(score_id, approver)
        print(f"Approved score_id {score_id} by {approver}")
    except Exception as e:
        print(f"Approval step: {e}")
    try:
        simulate_deployment(score_id)
        print(f"Deployment completed for score_id {score_id}")
    except Exception as e:
        print(f"Deployment step: {e}")

    actions = get_deployment_actions()
    print(f"Deployment actions count: {len(actions)}")
    for a in actions:
        print(a)

if __name__ == '__main__':
    main()
