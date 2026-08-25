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