import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# ── Settings ────────────────────────────────────────────
DURATION     = 120        # simulation length in seconds
TIME_STEP    = 1          # one reading per second
SPINDLE_RPM  = 3000       # normal spindle speed
FEED_RATE    = 150        # mm/min feed rate

# Normal operating ranges — outside these = alert
TEMP_MIN, TEMP_MAX         = 20, 75    # degrees Celsius
VIBRATION_MIN, VIBRATION_MAX = 0, 2.5  # mm/s
WEAR_MAX                   = 0.8       # mm tool wear limit

# ── Simulation ──────────────────────────────────────────
def simulate_process(duration, dt):
    time        = np.arange(0, duration, dt)
    n           = len(time)
    
    # Temperature rises gradually then stabilises, with noise
    temperature = 35 + 0.3 * time + np.random.normal(0, 1.5, n)
    
    # Vibration is mostly stable with occasional spikes
    vibration   = 1.2 + np.random.normal(0, 0.3, n)
    vibration[60:65] += 2.0   # simulate a disturbance at t=60s
    
    # Tool wear increases steadily over time
    wear        = 0.005 * time + np.random.normal(0, 0.01, n)
    wear        = np.clip(wear, 0, None)   # wear can't be negative
    
    return time, temperature, vibration, wear

# ── Alert detection ──────────────────────────────────────
def check_alerts(t, temp, vib, wear):
    alerts = []
    if temp > TEMP_MAX:
        alerts.append(f"  [t={t:.0f}s] TEMPERATURE ALERT: {temp:.1f}°C (limit: {TEMP_MAX}°C)")
    if vib > VIBRATION_MAX:
        alerts.append(f"  [t={t:.0f}s] VIBRATION ALERT: {vib:.2f} mm/s (limit: {VIBRATION_MAX} mm/s)")
    if wear > WEAR_MAX:
        alerts.append(f"  [t={t:.0f}s] TOOL WEAR ALERT: {wear:.3f} mm (limit: {WEAR_MAX} mm)")
    return alerts

# ── Main ─────────────────────────────────────────────────
def run():
    print("=" * 50)
    print("  CNC Digital Twin Simulator")
    print("=" * 50)
    print(f"  Duration:   {DURATION}s")
    print(f"  Spindle:    {SPINDLE_RPM} RPM")
    print(f"  Feed rate:  {FEED_RATE} mm/min")
    print("=" * 50)

    time, temperature, vibration, wear = simulate_process(DURATION, TIME_STEP)

    # ── Check alerts and print them ──
    print("\nRunning simulation...\n")
    all_alerts = []
    for i in range(len(time)):
        alerts = check_alerts(time[i], temperature[i], vibration[i], wear[i])
        all_alerts.extend(alerts)

    if all_alerts:
        print(f"  {len(all_alerts)} alert(s) detected:\n")
        for a in all_alerts:
            print(a)
    else:
        print("  No alerts. Process within normal limits.")

    # ── Save data to CSV ──
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame({
        "time_s":        time,
        "temperature_C": temperature,
        "vibration_mms": vibration,
        "tool_wear_mm":  wear
    })
    df.to_csv("data/sensor_log.csv", index=False)
    print(f"\n  Data saved to data/sensor_log.csv ({len(df)} rows)")

    # ── Plot ──
    os.makedirs("outputs", exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("CNC Digital Twin — Process Monitoring", fontsize=14)

    axes[0].plot(time, temperature, color="#1F618D", linewidth=1.5)
    axes[0].axhline(TEMP_MAX, color="red", linestyle="--", linewidth=1, label=f"Limit {TEMP_MAX}°C")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(time, vibration, color="#1D9E75", linewidth=1.5)
    axes[1].axhline(VIBRATION_MAX, color="red", linestyle="--", linewidth=1, label=f"Limit {VIBRATION_MAX} mm/s")
    axes[1].set_ylabel("Vibration (mm/s)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(time, wear, color="#BA7517", linewidth=1.5)
    axes[2].axhline(WEAR_MAX, color="red", linestyle="--", linewidth=1, label=f"Limit {WEAR_MAX} mm")
    axes[2].set_ylabel("Tool wear (mm)")
    axes[2].set_xlabel("Time (s)")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/process_chart.png", dpi=150)
    plt.show()
    print("  Chart saved to outputs/process_chart.png")
    print("\nSimulation complete.")

if __name__ == "__main__":
    run()