# RailBlock AI — Person 4 End-to-End Demo Script

## Goal

Demonstrate the complete pipeline:

**Request → Risk → Optimization → Control Approval → Passenger Update**

## Preconditions

1. Start the FastAPI backend.
2. Start the passenger Vite app.
3. Ensure the database has at least one asset, section and train schedule.
4. Set Postman variable `baseUrl` to `http://localhost:8000`.
5. Keep the passenger portal open at `http://localhost:5173`.

## Demo sequence

### 1. Submit maintenance request
`POST /api/maintenance-requests/`

Show:
- request accepted
- generated request ID
- status becomes `RECOMMENDED` when a block is produced

Explain: the backend builds ML features, obtains the risk result and runs the optimization engine.

### 2. Verify risk/optimization internally
Use the internal API or backend logs/dashboard.

Show:
- risk band/score
- recommended time window
- affected trains

**Important:** explain that these values are internal and are not sent to passengers.

### 3. Find the generated block
`GET /api/blocks/`

Capture the latest recommended block ID.

### 4. Control approval
`POST /api/blocks/{block_id}/approve`

Show status changing to `APPROVED`.

### 5. Passenger update
`GET /api/passenger/trains/{train_number}`

Show only:
- train number
- affected section
- maintenance window
- expected delay
- public reason
- public reason code
- public status

### 6. Security/QACheck
Open the raw passenger JSON in Postman and confirm it does **not** contain:
`risk_score`, `priority_score`, `priority_band`, `priority_reasons`,
`optimization_explanation`, `request_id`, `asset_id`, or internal audit data.

### 7. Browser demo
Open the passenger portal, enter the affected train number, and show the same sanitized information in the UI.

## Pass criteria

- All requests return expected HTTP status codes.
- Approved blocks appear in the passenger API.
- Internal-only fields are absent from every passenger response.
- Rejected/internal-only blocks never appear publicly.
- Public reason codes are stable and human-readable.
