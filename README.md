# Tyler's Train Detector
Components for a system used to identify and detect trains on the Union Pacific Austin Subdivision line.

This is my first attempt at a CV project... so don't judge :)

Included in this repo:
- All train detection logic
- API to expose train data stored in SQL
- Simple HTML dashboard for viewing train stats

## (Ideal) Process Diagram
```mermaid
flowchart TD
    A[Camera Process<br/><br/>• Capture frames<br/>• Crop ROI<br/>• Timestamp]
    -->|frames| B[Motion Detection Process<br/><br/>• Background subtract<br/>• Motion scoring<br/>• Debounce noise]

    B -->|motion frames| C[Train Presence Gate Process<br/><br/>• Confirm persistence<br/>• Start/stop events<br/>• Drop false hits]

    C -->|event frames| D[Classification Process<br/><br/>• ML inference<br/>• Freight vs Amtrak<br/>• Confidence score]

    D -->|predictions| E[Event Aggregator Process<br/><br/>• Majority vote<br/>• Direction<br/>• Speed estimate]

    E -->|finalized event| F[Persistence & Alerts<br/><br/>• SQL write<br/>• iOS Push Notification]

```