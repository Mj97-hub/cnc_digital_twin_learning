# CNC Digital Twin — Learning Version

An earlier, simpler CNC process monitoring simulator built in Python.
This was my first digital twin project — focused on understanding
the core concepts before building the more advanced live version.

## What it does

- Simulates 120 seconds of CNC machining data
- Monitors temperature, vibration, and tool wear
- Detects and logs alerts when values exceed safe limits
- Saves sensor data to CSV
- Generates a static 3-chart process monitoring plot

## Tech stack

- Python 3.x
- NumPy — signal simulation with noise
- Pandas — data logging to CSV
- Matplotlib — static process chart

## How to run

pip install -r requirements.txt
python Simulator.py

## How this differs from v2

This is the foundation. The upgraded version (cnc-spindle-digital-twin)
adds a live updating dashboard, real-time anomaly detection, a DigitalTwin
class with state machine, and tool wear tracking — built after mastering
these basics.

## Author
Amalkrishna — Intelligent Manufacturing student
