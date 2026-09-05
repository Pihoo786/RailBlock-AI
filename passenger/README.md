# RailBlock Public Passenger Web Portal

Person 4 deliverable for the RailBlock AI project.

## Features

- Train-number status lookup
- Affected-trains view
- Scheduled / approved / active / completed / cancelled status badges
- Expected delay and affected section
- Stable public reason codes
- English / Hindi UI
- Responsive public-facing layout
- API/mock mode
- Privacy notice confirming that internal risk and optimization data are not published

## Run

```bash
npm install
npm run dev
```

Set `VITE_API_BASE_URL` and `VITE_USE_MOCK` using `.env` when connecting to FastAPI.
See `.env.example`.

The backend public endpoints are:
- `GET /api/passenger/trains/{train_number}`
- `GET /api/passenger/blocks`
