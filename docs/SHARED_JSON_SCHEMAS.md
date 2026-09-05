# RailBlock AI — Day 1 Shared JSON Schemas

These schemas are the integration boundary for all five team members.

## 1. Maintenance request

`POST /api/maintenance-requests/`

```json
{
  "asset_id": "TRK-001",
  "department": "TRACK",
  "section_id": "SEC-CHN-KPD",
  "category": "Track",
  "severity": "HIGH",
  "raw_text": "Track maintenance required",
  "reported_at": "2026-09-05T09:00:00",
  "required_duration_minutes": 120,
  "maintenance_type": "Preventive",
  "urgency_remarks": "Planned work"
}
```

## 2. Risk result (internal)

```json
{
  "asset_id": 1,
  "asset_code": "TRK-001",
  "risk_score": 0.82,
  "priority": "HIGH"
}
```

**Internal only. Never return this object from `/api/passenger/*`.**

## 3. Optimizer request/result (internal)

```json
{
  "job_id": "MR-1234",
  "section": "Chennai - Katpadi",
  "duration_minutes": 120,
  "department": "TRACK",
  "priority": "HIGH",
  "risk_score": 0.82,
  "trains": []
}
```

**Internal only.** Priority, penalties, risk score and optimizer explanations must not cross the passenger boundary.

## 4. Approval result

`POST /api/blocks/{block_id}/approve`

```json
{
  "message": "Block approved successfully",
  "block_id": 17,
  "status": "APPROVED"
}
```

## 5. Passenger response (public/frozen)

`GET /api/passenger/trains/{train_number}`

```json
{
  "train_number": "12627",
  "blocks": [
    {
      "train_number": "12627",
      "section": "Chennai - Katpadi",
      "start_time": "2026-09-05T10:00:00",
      "end_time": "2026-09-05T12:00:00",
      "expected_delay_minutes": 25,
      "reason": "Track maintenance",
      "reason_code": "TRACK_MAINTENANCE",
      "status": "APPROVED"
    }
  ]
}
```

### Passenger allow-list

Allowed:
- `train_number`
- `section`
- `start_time`
- `end_time`
- `expected_delay_minutes`
- passenger-safe `reason`
- stable `reason_code`
- public `status`

Never allowed:
- `risk_score`
- `priority_score`
- `priority_band`
- `priority_reasons`
- `optimization_explanation`
- `request_id`
- `asset_id` / `asset_code`
- internal department data
- model/version details
- audit data

Public status values: `SCHEDULED`, `APPROVED`, `ACTIVE`, `COMPLETED`, `CANCELLED`.

Rejected/internal-only states are filtered server-side.
