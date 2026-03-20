# disk-io-monitor

Real-time disk I/O performance monitoring tool. Because sometimes you need to know what's thrashing your disk at 3 AM.

## What it does

Monitors disk read/write speeds, IOPS, and busy percentages in real time. Shows you:

- Read/write throughput (KB/s, MB/s, etc.)
- I/O operations per second (IOPS)
- Disk busy percentage
- Aggregated statistics when you stop
- **Disk usage alerts** when partitions exceed configured thresholds

## Quick start

```bash
pip install -r requirements.txt
python disk_io_monitor.py
```

That's it. You'll see a live-updating table of disk activity.

## Usage

```bash
# Default monitoring (1 second intervals)
python disk_io_monitor.py

# Faster updates (0.5 second interval)
python disk_io_monitor.py -i 0.5

# Run for 30 seconds then exit
python disk_io_monitor.py -d 30

# List available disks
python disk_io_monitor.py --list

# Custom history size
python disk_io_monitor.py -n 20

# Enable disk usage alerts (default thresholds: 80% warning, 90% critical)
python disk_io_monitor.py --alert

# Custom alert thresholds
python disk_io_monitor.py --alert --alert-warning 85 --alert-critical 95

# One-time disk usage check
python disk_io_monitor.py --check-usage
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-i, --interval` | Update interval in seconds | 1.0 |
| `-d, --duration` | Total run duration in seconds | infinite |
| `-n, --history` | Number of samples in history | 10 |
| `--list` | Show available disks and exit | - |
| `--alert` | Enable disk usage alerting | disabled |
| `--alert-warning` | Warning threshold percentage | 80.0 |
| `--alert-critical` | Critical threshold percentage | 90.0 |
| `--check-usage` | One-time disk usage check | - |

## Output example

```
======================================================================
Disk I/O Monitor - 2026-03-20 14:32:15
======================================================================
Disk         Read           Write          Read IOPS  Write IOPS Busy %
----------------------------------------------------------------------
nvme0n1       1.25 MB/s       512.00 KB/s      45.2       23.1    12.5%
sda           0.00 B/s        0.00 B/s          0.0        0.0     0.0%
----------------------------------------------------------------------
TOTAL         1.25 MB/s     512.00 KB/s
======================================================================

[WARNING] ALERT: /dev/sda1 at 82.3% usage (threshold: 80.0%) at 2026-03-20 14:32:16
```

## Disk Usage Alerts

When `--alert` is enabled, the monitor checks disk usage on each interval and triggers alerts when any partition exceeds the configured thresholds:

- **WARNING**: Usage >= warning threshold (default 80%)
- **CRITICAL**: Usage >= critical threshold (default 90%)

Alerts are rate-limited to once per minute per disk to avoid spam. A summary of all alerts triggered during the session is shown when the monitor stops.

## Why I wrote this

Needed to debug some weird disk latency issues and `iotop` wasn't giving me the historical context I wanted. This tool keeps a rolling history and shows statistics when you stop, so you can see patterns over time.

## Requirements

- Python 3.6+
- psutil

Install deps:

```bash
pip install -r requirements.txt
```

## Notes

- Disk busy percentage is estimated from read/write time counters
- Requires appropriate permissions to read disk stats (usually works without root)
- On some systems, per-disk counters might not be available

## License

Do whatever you want with it.
