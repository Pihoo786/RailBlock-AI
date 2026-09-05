# RailBlock AI - API Contract

## Trains

GET /api/trains

Returns available train data.

---

## Assets

GET /api/assets

Returns railway assets.

---

## Maintenance Jobs

GET /api/maintenance-jobs

POST /api/maintenance-jobs

---

## Risk

POST /api/risk/calculate

Calculates asset risk and priority.

---

## Block Optimization

POST /api/blocks/optimize

Generates the recommended maintenance block.

---

## Blocks

GET /api/blocks

GET /api/blocks/{block_id}

---

## Approval

POST /api/blocks/{block_id}/approve

POST /api/blocks/{block_id}/reject

---

## Passenger Status

GET /api/passenger/trains/{train_id}/status

# Passenger API Contract (Frozen)

## GET /api/passenger/trains/{train_number}

Response (200):
{
"train_number": "12627",
"blocks": [
{
"section": "Chennai - Katpadi",
"start_time": "2026-08-26T10:00:00",
"end_time": "2026-08-26T12:00:00",
"expected_delay_minutes": 25,
"reason": "Track maintenance",
"status": "SCHEDULED"
}
]
}

- Train exists, no disruption -> 200, blocks: []
- Train number doesn't exist -> 404

## GET /api/passenger/blocks

Returns flat array of all passenger-visible blocks (SCHEDULED, APPROVED, ACTIVE only):
[
{
"train_number": "12627",
"section": "Chennai - Katpadi",
"start_time": "2026-08-26T10:00:00",
"end_time": "2026-08-26T12:00:00",
"expected_delay_minutes": 25,
"reason": "Track maintenance",
"status": "SCHEDULED"
}
]

## Status values (passenger-visible only)

SCHEDULED | APPROVED | ACTIVE | COMPLETED | CANCELLED
(REJECTED is never exposed to passengers)

## Rules

- No auth required
- Server-side filtering of internal fields (risk_score, priority, etc.)
- CORS must allow http://localhost:5173 (dev)


## Person 4 / QACore — Public Data Boundary

The passenger endpoints are the **only public data surface** for passenger status.
They use an explicit server-side allow-list DTO. Do not expose ORM objects directly.

### GET /api/passenger/trains/{train_number}

Passenger response fields are frozen to:
`train_number`, `section`, `start_time`, `end_time`,
`expected_delay_minutes`, `reason`, `reason_code`, `status`.

### GET /api/passenger/blocks

Returns the same public fields as a flat list.

### Public reason codes

- `TRACK_MAINTENANCE`
- `OHE_INSPECTION`
- `SIGNAL_MAINTENANCE`
- `ELECTRICAL_WORK`
- `STRUCTURE_MAINTENANCE`
- `OTHER_MAINTENANCE`

### QACore checks

The Postman collection and pytest suite verify:
1. request accepted;
2. optimization produces a block;
3. control approval changes the block to `APPROVED`;
4. approved status reaches the passenger API;
5. internal scoring, penalty, asset and optimization fields are absent from public JSON.
