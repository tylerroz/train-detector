# TrainVision ATX

TrainVision ATX is a computer vision system for detecting and tracking trains along the Union Pacific Austin Subdivision line in Downtown Austin, Texas.
The project is entirely self-hosted on a Rasperry Pi in my apartment, giving insight on live and historical train activity data.

Live demo: http://trains.tylerroz.com

## Overview

This project is deployed on a Raspberry Pi 4 and operates as a self-contained system responsible for:

- Capturing a live camera feed (netcam pointed at the tracks)
- Detecting train motion using computer vision
- Persisting train events to a database
- Serving a REST API and web dashboard over the public internet

The system is designed to run continuously in a real-world environment with no reliance on cloud services.

## Key Features

- Real-time train detection using Python and OpenCV
- REST API for querying recent and historical train activity
- MySQL-backed storage layer
- HTML+JS dashboard for monitoring train events and system status
- Edge deployment on Raspberry Pi hardware

## Tech Stack

- Python
- OpenCV (CV2)
- Apache (host the dashboard)
- Flask (API endpoints)
- MySQL
- HTML, CSS, JavaScript
- Raspberry Pi 4 running Debian-ish

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