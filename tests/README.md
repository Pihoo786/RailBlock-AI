# Person 4 — QACore Integration Test Suite

## What is covered

- Passenger response uses an explicit allow-list.
- Internal risk/priority/penalty/asset/request/audit fields cannot be serialized by the passenger sanitizer.
- Public reason codes are stable.
- Passenger train lookup returns a 404 for an unknown train.
- Passenger endpoints return only the public DTO shape.

## Run

From the repository root:

```bash
pip install -r backend/requirements.txt
pytest -q tests/test_passenger_boundary.py
```

For live API verification, import `docs/RailBlock-Person4.postman_collection.json`
into Postman and run the collection against the FastAPI server.
