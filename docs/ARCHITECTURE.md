# RailBlock AI - Project Architecture

## System Flow

Public Train Timetable
+
Synthetic Maintenance Requests
+
Asset Risk Score
↓
Conflict Detection
↓
Block Optimization
↓
FastAPI Backend
↓
Recommended Block
↓
Railway Dashboard + Passenger Interface

## Modules

### Data and Optimization
Processes train schedules and recommends maintenance blocks.

### Risk Module
Calculates asset risk and maintenance priority.

### Backend
Acts as the central communication layer.

### Railway Dashboard
Used by railway officials to review and approve recommendations.

### Passenger Interface
Shows affected passengers relevant maintenance and delay information.

### Integration
Tests the complete system and connects all modules.