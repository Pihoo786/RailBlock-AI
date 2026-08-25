# RailBlock AI - Team Task Distribution

## Person 1 - Data and Optimization

Branch:
feature/data-optimizer

Folders:
data/
optimizer/

Responsibilities:
- Prepare train timetable data
- Filter data for the selected railway corridor
- Process train schedules
- Build train-block conflict detection
- Build maintenance block optimization
- Generate recommended maintenance windows

Main output:
Recommended block with timing, affected trains and estimated impact.

---

## Person 2 - Risk and Maintenance

Branch:
feature/risk-maintenance

Folders:
risk/
data/synthetic/

Responsibilities:
- Create synthetic asset data
- Create maintenance jobs
- Create risk scoring logic
- Calculate asset priority
- Provide risk output to the optimizer

Main output:
Risk score and priority for every maintenance request.

---

## Person 3 - Backend

Branch:
feature/backend

Folders:
backend/

Responsibilities:
- FastAPI backend
- SQLite database
- Database models
- API endpoints
- Connect optimizer and risk modules
- Swagger documentation

Main output:
Working backend API for the frontend and integration.

---

## Person 4 - Railway Dashboard

Branch:
feature/railway-dashboard

Folders:
dashboard/

Responsibilities:
- Railway control dashboard
- Maintenance request view
- Recommended block view
- Conflict visualization
- Affected trains
- Approve/reject actions

Main output:
Railway authority dashboard.

---

## Person 5 - Passenger Interface

Branch:
feature/passenger-ui

Folders:
passenger/

Responsibilities:
- Passenger-facing interface
- Train information
- Maintenance block information
- Expected delay/impact
- Block status

Main output:
Passenger transparency page.

---

## Person 6 - Integration and QA

Branch:
feature/integration-qa

Folders:
tests/
docs/

Responsibilities:
- Module integration
- API testing
- End-to-end testing
- Pull request review
- Merge feature branches into integration
- Bug tracking
- Final demo testing

Main output:
Fully integrated and tested prototype.