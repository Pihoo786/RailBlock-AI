"""
ML/Risk Module for AI-Powered Railway Maintenance Block Planning
Person 2: Risk Scoring and Priority Assignment

This module provides risk assessment for railway assets to help
prioritize maintenance work.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Set up logging so your team can see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================
# PART 1: RISK SCORING CORE LOGIC
# ============================================

def calculate_risk_score(asset_data: Dict[str, Any]) -> float:
    """
    Calculate risk score for a railway asset.
    
    Args:
        asset_data: Dictionary with asset information
        
    Returns:
        float: Risk score between 0 and 1
        
    Example:
        >>> asset = {"condition_score": 4.0, "criticality_score": 5.0, 
        ...          "days_overdue": 60, "maintenance_history": 1, 
        ...          "safety_importance": 5.0}
        >>> calculate_risk_score(asset)
        0.84
    """
    try:
        # Extract values with default fallbacks
        condition = asset_data.get('condition_score', 3.0)
        criticality = asset_data.get('criticality_score', 3.0)
        overdue_days = asset_data.get('days_overdue', 0)
        history_count = asset_data.get('maintenance_history', 0)
        safety = asset_data.get('safety_importance', 3.0)
        
        # Normalize each factor to 0-1 scale
        condition_risk = min(condition / 5.0, 1.0)
        criticality_risk = min(criticality / 5.0, 1.0)
        safety_risk = min(safety / 5.0, 1.0)
        
        # Overdue: days overdue up to 100 days (max risk at 100+)
        overdue_risk = min(overdue_days / 100.0, 1.0)
        
        # History: more history = lower risk (max 10 previous maintenances)
        history_risk = 1.0 - min(history_count / 10.0, 1.0)
        
        # Apply weights from project specification
        risk_score = (0.35 * condition_risk) + \
                     (0.30 * criticality_risk) + \
                     (0.20 * overdue_risk) + \
                     (0.15 * history_risk)
        
        # Ensure score is between 0 and 1
        risk_score = max(0.0, min(risk_score, 1.0))
        
        logger.debug(f"Risk score calculated: {risk_score:.2f} for asset {asset_data.get('asset_id', 'unknown')}")
        return risk_score
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        return 0.5  # Default medium risk if something goes wrong


def get_priority(risk_score: float) -> str:
    """
    Convert risk score to priority level.
    
    Args:
        risk_score: Float between 0 and 1
        
    Returns:
        str: 'HIGH', 'MEDIUM', or 'LOW'
    """
    if risk_score >= 0.7:
        return "HIGH"
    elif risk_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


# ============================================
# PART 2: ADVANCED FEATURES
# ============================================

def get_urgency_level(asset_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate urgency based on multiple factors.
    
    Returns detailed breakdown for dashboard display.
    """
    risk_score = calculate_risk_score(asset_data)
    priority = get_priority(risk_score)
    
    # Determine if this is safety-critical (needs immediate attention)
    safety_critical = asset_data.get('safety_importance', 0) >= 4.0
    
    # Determine if this is overdue (immediate action needed)
    overdue_days = asset_data.get('days_overdue', 0)
    severely_overdue = overdue_days > 30
    
    return {
        "risk_score": risk_score,
        "priority": priority,
        "safety_critical": safety_critical,
        "severely_overdue": severely_overdue,
        "recommended_action": _get_recommended_action(risk_score, safety_critical, severely_overdue)
    }


def _get_recommended_action(risk_score: float, safety_critical: bool, severely_overdue: bool) -> str:
    """Helper function to recommend action based on risk factors."""
    if safety_critical and risk_score > 0.6:
        return "IMMEDIATE_MAINTENANCE_REQUIRED"
    elif risk_score >= 0.7:
        return "SCHEDULE_WITHIN_24_HOURS"
    elif risk_score >= 0.4:
        return "SCHEDULE_WITHIN_WEEK"
    else:
        return "ROUTINE_INSPECTION"


def predict_delay_impact(priority: str, base_delay: int = 10) -> int:
    """
    Estimate delay impact based on priority level.
    
    This is a simple rule-based estimation. For the prototype,
    it gives reasonable estimates for the dashboard.
    
    Args:
        priority: 'HIGH', 'MEDIUM', or 'LOW'
        base_delay: Base delay in minutes
        
    Returns:
        int: Estimated delay in minutes
    """
    if priority == "HIGH":
        return base_delay + 20  # High priority = more complex work = longer delay
    elif priority == "MEDIUM":
        return base_delay + 5
    else:
        return max(0, base_delay - 5)


# ============================================
# PART 3: MAIN FUNCTION FOR BACKEND INTEGRATION
# ============================================

def get_asset_priority_and_risk(asset_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function called by Backend (Person 3).
    
    Args:
        asset_data: Dictionary with asset information
        
    Returns:
        Dictionary with risk assessment results
        
    Example Input:
        {
            "asset_id": "TRK_001",
            "condition_score": 4.2,
            "criticality_score": 4.5,
            "days_overdue": 45,
            "maintenance_history": 2,
            "safety_importance": 4.8
        }
        
    Example Output:
        {
            "asset_id": "TRK_001",
            "risk_score": 0.78,
            "priority": "HIGH",
            "urgency": {
                "safety_critical": true,
                "severely_overdue": true,
                "recommended_action": "IMMEDIATE_MAINTENANCE_REQUIRED"
            },
            "estimated_delay_minutes": 30,
            "timestamp": "2026-08-26T14:30:00"
        }
    """
    try:
        # Validate input
        if not asset_data or 'asset_id' not in asset_data:
            logger.error("Invalid asset data: missing asset_id")
            return {
                "error": "Invalid asset data",
                "asset_id": "unknown",
                "risk_score": 0.5,
                "priority": "MEDIUM"
            }
        
        # Calculate core metrics
        risk_score = calculate_risk_score(asset_data)
        priority = get_priority(risk_score)
        urgency = get_urgency_level(asset_data)
        estimated_delay = predict_delay_impact(priority)
        
        # Prepare result
        result = {
            "asset_id": asset_data['asset_id'],
            "risk_score": round(risk_score, 2),
            "priority": priority,
            "urgency": urgency,
            "estimated_delay_minutes": estimated_delay,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Risk assessment complete for {asset_data['asset_id']}: {priority}")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_asset_priority_and_risk: {e}")
        return {
            "error": str(e),
            "asset_id": asset_data.get('asset_id', 'unknown'),
            "risk_score": 0.5,
            "priority": "MEDIUM"
        }


# ============================================
# PART 4: BATCH PROCESSING (for multiple assets)
# ============================================

def process_multiple_assets(assets_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple assets at once.
    
    Useful for the dashboard to show all assets with their risks.
    
    Args:
        assets_list: List of asset data dictionaries
        
    Returns:
        List of risk assessment results
    """
    results = []
    for asset in assets_list:
        result = get_asset_priority_and_risk(asset)
        results.append(result)
    return results


# ============================================
# PART 5: MOCK DATA GENERATOR (for testing)
# ============================================

def generate_test_assets() -> List[Dict[str, Any]]:
    """
    Generate test data for development and demo.
    
    This creates realistic-looking asset data for testing the dashboard.
    """
    import random
    
    asset_types = ["Track", "Bridge", "Signal", "OHE", "Switch"]
    asset_ids = [f"{asset_type[:3].upper()}_{i:03d}" for asset_type in asset_types for i in range(1, 6)]
    
    assets = []
    for asset_id in asset_ids:
        asset = {
            "asset_id": asset_id,
            "condition_score": round(random.uniform(1.0, 5.0), 1),
            "criticality_score": round(random.uniform(1.0, 5.0), 1),
            "days_overdue": random.randint(0, 120),
            "maintenance_history": random.randint(0, 8),
            "safety_importance": round(random.uniform(1.0, 5.0), 1)
        }
        assets.append(asset)
    
    return assets


# ============================================
# PART 6: TEST SECTION
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("RAILBLOCK AI - RISK MODULE TEST")
    print("=" * 60)
    
    # Test 1: Single asset
    print("\n1. Testing Single Asset:")
    print("-" * 40)
    test_asset = {
        "asset_id": "TRK_001",
        "condition_score": 4.2,
        "criticality_score": 4.5,
        "days_overdue": 45,
        "maintenance_history": 2,
        "safety_importance": 4.8
    }
    
    result = get_asset_priority_and_risk(test_asset)
    print(json.dumps(result, indent=2))
    
    # Test 2: Multiple assets
    print("\n2. Testing Multiple Assets:")
    print("-" * 40)
    test_assets = generate_test_assets()[:5]  # Test 5 assets
    results = process_multiple_assets(test_assets)
    
    for r in results:
        print(f"{r['asset_id']}: Risk={r['risk_score']}, Priority={r['priority']}, Delay={r['estimated_delay_minutes']}min")
    
    # Test 3: Edge cases
    print("\n3. Testing Edge Cases:")
    print("-" * 40)
    
    # Perfect condition asset
    perfect = {
        "asset_id": "PERFECT_001",
        "condition_score": 1.0,
        "criticality_score": 1.0,
        "days_overdue": 0,
        "maintenance_history": 10,
        "safety_importance": 1.0
    }
    print(f"Perfect asset: {get_asset_priority_and_risk(perfect)['priority']}")
    
    # Terrible condition asset
    terrible = {
        "asset_id": "TERRIBLE_001",
        "condition_score": 5.0,
        "criticality_score": 5.0,
        "days_overdue": 200,
        "maintenance_history": 0,
        "safety_importance": 5.0
    }
    print(f"Terrible asset: {get_asset_priority_and_risk(terrible)['priority']}")
    
    print("\n" + "=" * 60)
    print("RISK MODULE TEST COMPLETE!")
    print("=" * 60)