# train-detector
Components for a system used to identify and detect trains on the Union Pacific Austin Subdivision line.

This is my first attempt at a CV project... so don't judge :)

## (Ideal) Process Diagram
┌──────────────────────┐
│   Camera Process     │
│                      │
│ • Capture frames     │
│ • Crop ROI           │
│ • Timestamp          │
│                      │
└─────────┬────────────┘
          │  frames
          ▼
┌──────────────────────┐
│ Motion Detection     │
│      Process         │
│                      │
│ • Background subtract│
│ • Motion scoring     │
│ • Debounce noise     │
│                      │
└─────────┬────────────┘
          │ motion frames
          ▼
┌──────────────────────┐
│ Train Presence       │
│    Gate Process      │
│                      │
│ • Confirm persistence│
│ • Start/stop events  │
│ • Drop false hits    │
│                      │
└─────────┬────────────┘
          │ event frames
          ▼
┌──────────────────────┐
│ Classification       │
│     Process          │
│                      │
│ • ML inference       │
│ • Freight vs Amtrak  │
│ • Confidence score   │
│                      │
└─────────┬────────────┘
          │ predictions
          ▼
┌──────────────────────┐
│ Event Aggregator     │
│     Process          │
│                      │
│ • Majority vote      │
│ • Direction          │
│ • Speed estimate     │
│                      │
└─────────┬────────────┘
          │ finalized event
          ▼
┌──────────────────────┐
│ Persistence & Alerts │
│                      │
│ • SQLite write       │
│ • Slack / UI update  │
│                      │
└──────────────────────┘
