# RailBlock AI - Shared Data Schema

## Train

- train_id
- train_name
- section
- entry_time
- exit_time
- train_type

## Asset

- asset_id
- asset_type
- section
- condition
- criticality
- overdue_days

## Maintenance Job

- job_id
- asset_id
- department
- section
- duration_minutes
- priority
- status

## Risk Output

- asset_id
- risk_score
- priority

## Recommended Block

- block_id
- section
- start_time
- end_time
- departments
- affected_trains
- estimated_impact_minutes
- impact_level
- status

## Standard Rules

Time format:
HH:MM

Section format:
MAS-AJJ

Risk score:
0.00 to 1.00

Priority:
LOW
MEDIUM
HIGH

Status:
PENDING
RECOMMENDED
APPROVED
REJECTED
COMPLETED