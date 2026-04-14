import numpy as np
import random
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

class Dashboard:
    """
    Live updating matplotlib dashboard.
    Shows 4 sensor charts + a status indicator in real time.
    """

    def __init__(self, sensor, twin):
        self.sensor = sensor
        self.twin   = twin

        # Create figure with 5 subplots
        self.fig = plt.figure(figsize=(12, 7))
        self.fig.patch.set_facecolor('#0d1117')  # dark background
        self.fig.suptitle('CNC Spindle Digital Twin — Live Monitor',
                          color='white', fontsize=14, fontweight='bold')

        # Define grid: 4 charts on left, 1 status panel on right
        gs = self.fig.add_gridspec(4, 2, width_ratios=[3, 1],
                                   hspace=0.5, wspace=0.3)

        # 4 sensor charts
        self.ax_rpm  = self.fig.add_subplot(gs[0, 0])
        self.ax_temp = self.fig.add_subplot(gs[1, 0])
        self.ax_vib  = self.fig.add_subplot(gs[2, 0])
        self.ax_load = self.fig.add_subplot(gs[3, 0])

        # Status panel (spans all 4 rows on the right)
        self.ax_status = self.fig.add_subplot(gs[:, 1])

        self._style_axes()

    def _style_axes(self):
        """Make all charts dark themed."""
        for ax in [self.ax_rpm, self.ax_temp,
                   self.ax_vib, self.ax_load, self.ax_status]:
            ax.set_facecolor('#161b22')
            ax.tick_params(colors='#8b949e', labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor('#30363d')

        self.ax_rpm.set_title('RPM',         color='#58a6ff', fontsize=9)
        self.ax_temp.set_title('Temperature (°C)', color='#ff7b72', fontsize=9)
        self.ax_vib.set_title('Vibration',   color='#ffa657', fontsize=9)
        self.ax_load.set_title('Load (%)',   color='#3fb950', fontsize=9)
        self.ax_status.set_title('Twin Status', color='white', fontsize=9)
        self.ax_status.axis('off')

    def _draw_status(self, state, health, anomaly_count):
        """Draws the status panel on the right."""
        self.ax_status.cla()
        self.ax_status.axis('off')
        self.ax_status.set_facecolor('#161b22')

        # Color based on state
        colors = {
            "NORMAL":   ('#3fb950', '#0d1117'),
            "WARNING":  ('#ffa657', '#0d1117'),
            "CRITICAL": ('#ff7b72', '#0d1117'),
        }
        bg, fg = colors.get(state, ('#8b949e', '#0d1117'))

        # Big state box
        self.ax_status.add_patch(plt.Rectangle(
            (0.05, 0.7), 0.9, 0.22,
            color=bg, transform=self.ax_status.transAxes))
        self.ax_status.text(0.5, 0.82, state,
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='black', transform=self.ax_status.transAxes)

        # Health + anomaly count
        self.ax_status.text(0.5, 0.58, f'Tool Health',
            ha='center', color='#8b949e', fontsize=8,
            transform=self.ax_status.transAxes)
        self.ax_status.text(0.5, 0.48, f'{health}%',
            ha='center', color='white', fontsize=20, fontweight='bold',
            transform=self.ax_status.transAxes)

        self.ax_status.text(0.5, 0.32, f'Anomalies',
            ha='center', color='#8b949e', fontsize=8,
            transform=self.ax_status.transAxes)
        self.ax_status.text(0.5, 0.22, str(anomaly_count),
            ha='center', color='#ff7b72', fontsize=20, fontweight='bold',
            transform=self.ax_status.transAxes)

        # Last anomaly message
        if self.twin.anomalies:
            last = self.twin.anomalies[-1]
            self.ax_status.text(0.5, 0.08, last[-30:],
                ha='center', color='#ffa657', fontsize=7,
                transform=self.ax_status.transAxes, wrap=True)

    def animate(self, frame):
        """Called every 500ms by matplotlib — gets new data and redraws."""
        reading = self.sensor.get_reading()
        state   = self.twin.update(reading)

        # Get last 60 readings for each sensor
        times = list(range(len(self.twin.history)))
        rpm   = self.twin.get_latest('rpm',  60)
        temp  = self.twin.get_latest('temperature', 60)
        vib   = self.twin.get_latest('vibration',   60)
        load  = self.twin.get_latest('load', 60)

        x = list(range(len(rpm)))

        # Clear and redraw each chart
        for ax in [self.ax_rpm, self.ax_temp, self.ax_vib, self.ax_load]:
            ax.cla()
        self._style_axes()

        self.ax_rpm.plot(x,  rpm,  color='#58a6ff', linewidth=1.2)
        self.ax_rpm.fill_between(x, rpm,  alpha=0.15, color='#58a6ff')

        self.ax_temp.plot(x, temp, color='#ff7b72', linewidth=1.2)
        self.ax_temp.fill_between(x, temp, alpha=0.15, color='#ff7b72')
        self.ax_temp.axhline(y=65, color='#ffa657', linewidth=0.8,
                             linestyle='--', label='warning')
        self.ax_temp.axhline(y=80, color='#ff7b72', linewidth=0.8,
                             linestyle='--', label='critical')

        self.ax_vib.plot(x,  vib,  color='#ffa657', linewidth=1.2)
        self.ax_vib.fill_between(x, vib,  alpha=0.15, color='#ffa657')
        self.ax_vib.axhline(y=2.0, color='#ffa657', linewidth=0.8,
                            linestyle='--')
        self.ax_vib.axhline(y=3.5, color='#ff7b72', linewidth=0.8,
                            linestyle='--')

        self.ax_load.plot(x, load, color='#3fb950', linewidth=1.2)
        self.ax_load.fill_between(x, load, alpha=0.15, color='#3fb950')

        # Redraw status panel
        self._draw_status(state, self.twin.tool_health(),
                          len(self.twin.anomalies))

    def run(self):
        """Starts the live animation loop."""
        ani = animation.FuncAnimation(
            self.fig, self.animate, interval=500, cache_frame_data=False)
        plt.show()

class SensorSimulator:
    def __init__(self):
        self.time_step = 0
        self.wear_level = 0.0

    def get_reading(self):
        self.time_step += 1
        self.wear_level += 0.001

        rpm         = 3500 + np.random.normal(0, 20)
        temperature = 45   + self.wear_level * 30 + np.random.normal(0, 1.5)
        vibration   = 0.5  + self.wear_level * 2.5 + np.random.normal(0, 0.1)
        load        = 40   + self.wear_level * 20 + np.random.normal(0, 2)

        if random.random() < 0.05:
            vibration   += random.uniform(2, 5)
            temperature += random.uniform(5, 15)

        return {
            "time":        self.time_step,
            "rpm":         round(rpm, 1),
            "temperature": round(temperature, 1),
            "vibration":   round(vibration, 3),
            "load":        round(load, 1),
            "wear":        round(self.wear_level * 100, 1)
        }


class DigitalTwin:
    """
    Live software model of the real spindle.
    Receives sensor data, tracks state, raises alerts.
    This is what Siemens MindSphere does at industrial scale.
    """

    LIMITS = {
        "temperature": {"warning": 65,  "critical": 80},
        "vibration":   {"warning": 2.0, "critical": 3.5},
        "load":        {"warning": 75,  "critical": 90},
        "wear":        {"warning": 60,  "critical": 85},
    }

    def __init__(self):
        self.state     = "NORMAL"
        self.anomalies = []
        self.history   = deque(maxlen=60)

    def update(self, reading):
        self.history.append(reading)
        self.state = "NORMAL"
        alerts = []

        for sensor, limits in self.LIMITS.items():
            value = reading[sensor]
            if value >= limits["critical"]:
                self.state = "CRITICAL"
                alerts.append(f"CRITICAL — {sensor} = {value}")
            elif value >= limits["warning"]:
                if self.state != "CRITICAL":
                    self.state = "WARNING"
                alerts.append(f"WARNING  — {sensor} = {value}")

        for alert in alerts:
            entry = f"[t={reading['time']:>4}s] {alert}"
            self.anomalies.append(entry)
            print(entry)

        return self.state

    def get_latest(self, sensor, n=30):
        return [r[sensor] for r in list(self.history)[-n:]]

    def tool_health(self):
        latest = list(self.history)[-1] if self.history else {}
        wear   = latest.get("wear", 0)
        return max(0, round(100 - wear, 1))

if __name__ == "__main__":
    sensor    = SensorSimulator()
    twin      = DigitalTwin()
    dashboard = Dashboard(sensor, twin)
    dashboard.run()