# Product Requirements Document: HA-Validator

## 1. Executive Summary
HA-Validator is a web-based tool designed to visualize and validate Home Assistant configurations. It ingests data from a live Home Assistant instance, maps the relationships between Entities and Automations, and identifies logic conflicts (loops, race conditions, fighting automations).

## 2. Technical Architecture
*   **Backend:** Python 3.11+ (FastAPI).
*   **Frontend:** React (Vite + TypeScript) using **React Flow** for visualization.
*   **Data Processing:** `NetworkX` for graph topology and analysis.
*   **Data Validation:** `Pydantic` for strict schema validation of HA API responses.
*   **Storage:** In-memory / JSON file snapshots (No complex DB for MVP).

## 3. Core Terminology
*   **Entity:** A device or state in HA (e.g., `light.bedroom`, `sensor.temperature`).
*   **Automation:** A logic block containing Triggers, Conditions, and Actions.
*   **Edge/Link:** A relationship.
    *   *Trigger Link:* Entity updates -> Triggers Automation.
    *   *Action Link:* Automation -> Changes State of Entity.

## 4. Phase Roadmap

### Phase 1: Ingestion (The Snapshot)
*   **Goal:** Connect to HA API and download current state and configuration.
*   **Output:** Normalized `snapshot.json` containing strongly-typed lists of Entities and Automations.
*   **Constraint:** Must parse `automation` config to extract triggers and actions structurally.

### Phase 2: Mapping (The Graph)
*   **Goal:** Build a Directed Graph (DiGraph).
*   **Logic:**
    *   Parse automation actions to find target entities (service calls).
    *   Parse automation triggers to find source entities.
*   **UI:** Visualize this graph using React Flow. Nodes are Entities/Automations; Edges are control flows.

### Phase 3: Analysis (The Validator)
*   **Goal:** algorithmic detection of issues.
*   **Detects:**
    *   **Cycles:** A triggers B which triggers A.
    *   **Fighting:** Automation A and B both control Entity X (potential conflict).
    *   **Races:** Automation A and B share the same Trigger AND the same Action Target.

## 5. Non-Functional Requirements
*   Code must be fully type-hinted (Python).
*   Frontend must use TypeScript.
*   Do not attempt to parse Jinja2 templates in the MVP (mark as "complex").
