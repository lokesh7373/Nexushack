# AMMS (AI Machine Monitoring System) — NexusHacks Embedded AI

**Category:** Embedded AI · NexusHacks (Phaser) · Jul 21–23, 2026

---

# Problem Statement

AMMS facilities require periodic inspection of electrical distribution panels to ensure safe operation of critical infrastructure. Operators currently perform these inspections manually by visiting each panel, recording electrical parameters such as Voltage, Current, Power, Power Factor, and Energy Consumption, and comparing them against safe operating limits.

This manual process is:

- Time-consuming
- Labor-intensive
- Error-prone
- Difficult to scale across large facilities
- Lacks centralized digital reporting

The objective is to develop an autonomous embedded AI system capable of navigating an industrial environment, inspecting electrical meters, extracting readings automatically, evaluating operational safety, and generating digital inspection reports.

---

# Solution Overview

**AMMS AI is an autonomous quadruped inspection system that explores an industrial electrical utility room, navigates to selected electrical panels, captures meter readings using onboard vision, extracts values through a Vision Language Model, evaluates them against predefined safety thresholds, and logs inspection reports to a centralized database via an intuitive Streamlit interface.**

---

# System Overview

Our system combines autonomous robotics, AI-powered visual understanding, and industrial automation into a complete inspection workflow.

Instead of manually inspecting electrical panels, an operator simply selects the desired inspection panel from a Streamlit dashboard.

The system automatically:

- Generates an inspection plan using LLM Tool Calling
- Sends navigation goals to the robot
- Navigates autonomously using ROS2 Nav2
- Captures images of electrical meters
- Extracts meter readings using a Vision Language Model
- Validates readings against configurable safety limits
- Stores inspection history inside a database
- Displays inspection results through the operator dashboard

---

# Architecture

```
                        Streamlit Dashboard
                                │
                                                ▼
                   LLM Tool Calling / Planner
                                │
                                                ▼
                 Navigation Goal Generation
                                │
                                                ▼
             Occupency map + Nav2 Navigation
                                │
                                                ▼
                    Spot Robot (Isaac Sim)
                                │
                                                ▼
                    RGB Camera Image Capture
                                │
                                                ▼
                   Vision Language Model (LLM)
                                │
                                                ▼
        Reading Extraction + Safety Verification
                                │
                                                ▼
                  Database + Inspection Report
                                │
                                                ▼
                    Streamlit Dashboard Update
```

See `docs/architecture.md` for a detailed architecture diagram.

---

# Workflow

### Step 1 — Environment Exploration

The Spot robot autonomously explores the unknown industrial utility room using ExploreLite and constructs an occupancy map of the environment.

---

### Step 2 — Operator Interaction

The operator launches the Streamlit dashboard and selects the electrical panel (meter) that requires inspection.

Example:

- Panel P-101
- Panel P-102
- UPS Meter
- Transformer Panel

---

### Step 3 — Intelligent Planning

The selected inspection request is processed using LLM Tool Calling, which generates the required inspection plan.

---

### Step 4 — Autonomous Navigation

The generated navigation goal is forwarded to ROS2 Nav2.

Using the previously generated occupancy map, Spot autonomously navigates to the inspection location.

---

### Step 5 — Visual Inspection

Upon reaching the inspection point, the onboard RGB camera captures a high-resolution image of the electrical meter.

---

### Step 6 — Meter Reading Extraction

The captured image is sent to a Vision Language Model (LLM), which extracts critical electrical parameters including:

- Voltage (V)
- Current (A)
- Power (W / kW)
- Power Factor (PF)
- Energy Consumption (kWh)

---

### Step 7 — Safety Verification

Extracted readings are automatically compared against predefined safety thresholds.

Example:

| Parameter | Reading | Safe Range | Status |
|-----------|---------|------------|--------|
| Voltage | 415 V | 400–440 V | ✅ Safe |
| Current | 82 A | ≤70 A | ⚠ Warning |
| Power Factor | 0.62 | ≥0.90 | ⚠ Warning |

---

### Step 8 — Inspection Report

The inspection result is stored in the database with:

- Timestamp
- Panel ID
- Meter Readings
- Safety Status
- Inspection Summary

The Streamlit dashboard displays the latest inspection report to the operator.

---

# Features

- Autonomous environment exploration
- Occupancy map generation
- ROS2 Nav2 autonomous navigation
- Streamlit-based operator interface
- LLM Tool Calling for inspection planning
- Vision-based electrical meter reading
- Automatic safety validation
- Digital inspection reporting
- Historical inspection database
- Fully simulation-based industrial proof-of-concept

---

# Tech Stack

### Simulation
- NVIDIA Isaac Sim 5.0

### Robotics Middleware
- ROS2 Humble
- Nav2

### AI / Perception
- Vision Language Model (LLM)
- LLM Tool Calling
- Python

### Robot
- Spot Quadruped Robot

### User Interface
- Streamlit

---

# How to Run

## Launch Isaac Sim

```bash
./python.sh .\scripts\app.py
```
---

## Launch Nav2

```bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true params_file:=./Nav2/nav2_params_map.yaml
```

---

## Launch Nav2 Maps

```bash
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=nex_hacks.yaml -p frame_id:=map && ros2 lifecycle set /map_server  && ros2 lifecycle set /map_server activate
```

---

##  Launch Streamlit Dashboard

```bash
source phaser_env/bin/activate 
cd phaser_hack
streamlit run app.py --server.address 0.0.0.0
```

---

## 8. Start Inspection

- Select the desired electrical panel.
- Click **Inspect**.
- Monitor the robot as it autonomously navigates to the selected panel.
- View extracted meter readings and safety status.
- Inspection history is automatically stored and displayed.

---

# Demo Video

[Output\Nexus.webm](https://github.com/lokesh7373/Nexushack/blob/main/NEXUS_HACK/Output/Nexus.webm)
---

