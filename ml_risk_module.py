 # ml_risk_module.py

def calculate_risk_score(asset_data):
    condition = asset_data['condition_score']
    criticality = asset_data['criticality_score']
    overdue_days = asset_data['days_overdue']
    history_count = asset_data['maintenance_history']
    safety = asset_data['safety_importance']

    condition_risk = condition / 5.0
    criticality_risk = criticality / 5.0
    safety_risk = safety / 5.0
    overdue_risk = min(overdue_days / 100.0, 1.0)
    history_risk = 1.0 - min(history_count / 10.0, 1.0)

    total_risk_score = (0.35 * condition_risk) + \
                       (0.30 * criticality_risk) + \
                       (0.20 * overdue_risk) + \
                       (0.15 * history_risk)
    return total_risk_score

def get_priority(risk_score):
    if risk_score >= 0.7:
        return "HIGH"
    elif risk_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"

def get_asset_priority_and_risk(asset_data):
    risk_score = calculate_risk_score(asset_data)
    priority = get_priority(risk_score)
    
    result = {
        "asset_id": asset_data['asset_id'],
        "risk_score": round(risk_score, 2),
        "priority": priority
    }
    return result

# Test section
if __name__ == "__main__":
    fake_asset = {
        "asset_id": "TRACK_101",
        "condition_score": 4.0,
        "criticality_score": 5.0,
        "days_overdue": 60,
        "maintenance_history": 1,
        "safety_importance": 5.0
    }
    output = get_asset_priority_and_risk(fake_asset)
    print("My Output:")
    print(output)
