#!/usr/bin/env python3
"""
Disk I/O Monitor - Real-time disk performance monitoring tool
"""

import sys
import time
import argparse
from datetime import datetime
from collections import deque

try:
    import psutil
except ImportError:
    print("Error: psutil library required. Install with: pip install psutil")
    sys.exit(1)


class DiskIOMonitor:
    def __init__(self, interval=1.0, history_size=10):
        self.interval = interval
        self.history_size = history_size
        self.prev_counters = {}
        self.history = deque(maxlen=history_size)
        self.running = False

    def get_disk_counters(self):
        """Get current disk I/O counters for all disks."""
        return psutil.disk_io_counters(perdisk=True)

    def calculate_metrics(self, current, previous):
        """Calculate I/O metrics between two counter snapshots."""
        metrics = {}
        
        for disk_name, curr_disk in current.items():
            if disk_name in previous:
                prev_disk = previous[disk_name]
                
                read_bytes = max(0, curr_disk.read_bytes - prev_disk.read_bytes)
                write_bytes = max(0, curr_disk.write_bytes - prev_disk.write_bytes)
                read_count = max(0, curr_disk.read_count - prev_disk.read_count)
                write_count = max(0, curr_disk.write_count - prev_disk.write_count)
                
                read_time = max(0, curr_disk.read_time - prev_disk.read_time)
                write_time = max(0, curr_disk.write_time - prev_disk.write_time)
                
                read_speed = read_bytes / self.interval
                write_speed = write_bytes / self.interval
                
                total_time = read_time + write_time
                busy_percentage = min(100.0, (total_time / 1000.0) / self.interval * 100) if self.interval > 0 else 0
                
                metrics[disk_name] = {
                    'read_speed': read_speed,
                    'write_speed': write_speed,
                    'read_iops': read_count / self.interval,
                    'write_iops': write_count / self.interval,
                    'read_bytes': read_bytes,
                    'write_bytes': write_bytes,
                    'busy_percentage': busy_percentage,
                    'timestamp': datetime.now()
                }
        
        return metrics

    def format_bytes(self, bytes_value):
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(bytes_value) < 1024.0:
                return f"{bytes_value:7.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:7.2f} PB"

    def display_metrics(self, metrics):
        """Display current metrics in a formatted table."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*70}")
        print(f"Disk I/O Monitor - {timestamp}")
        print(f"{'='*70}")
        
        header = f"{'Disk':<12} {'Read':<14} {'Write':<14} {'Read IOPS':<10} {'Write IOPS':<10} {'Busy %':<8}"
        print(header)
        print("-" * 70)
        
        for disk_name, data in sorted(metrics.items()):
            read_str = f"{self.format_bytes(data['read_speed'])}/s"
            write_str = f"{self.format_bytes(data['write_speed'])}/s"
            read_iops = f"{data['read_iops']:>8.1f}"
            write_iops = f"{data['write_iops']:>8.1f}"
            busy = f"{data['busy_percentage']:>6.1f}%"
            
            print(f"{disk_name:<12} {read_str:<14} {write_str:<14} {read_iops:<10} {write_iops:<10} {busy:<8}")
        
        print("-" * 70)
        
        total_read = sum(m['read_speed'] for m in metrics.values())
        total_write = sum(m['write_speed'] for m in metrics.values())
        print(f"{'TOTAL':<12} {self.format_bytes(total_read)}/s  {self.format_bytes(total_write)}/s")
        print(f"{'='*70}\n")

    def get_statistics(self):
        """Calculate statistics from history."""
        if not self.history:
            return None
        
        all_read_speeds = []
        all_write_speeds = []
        all_busy_percentages = []
        
        for snapshot in self.history:
            for disk_data in snapshot.values():
                all_read_speeds.append(disk_data['read_speed'])
                all_write_speeds.append(disk_data['write_speed'])
                all_busy_percentages.append(disk_data['busy_percentage'])
        
        if not all_read_speeds:
            return None
        
        return {
            'avg_read': sum(all_read_speeds) / len(all_read_speeds),
            'max_read': max(all_read_speeds),
            'avg_write': sum(all_write_speeds) / len(all_write_speeds),
            'max_write': max(all_write_speeds),
            'avg_busy': sum(all_busy_percentages) / len(all_busy_percentages),
            'max_busy': max(all_busy_percentages),
            'samples': len(self.history)
        }

    def display_statistics(self):
        """Display aggregated statistics."""
        stats = self.get_statistics()
        if not stats:
            return
        
        print(f"\n{'='*70}")
        print("STATISTICS SUMMARY")
        print(f"{'='*70}")
        print(f"Samples collected: {stats['samples']}")
        print(f"Avg Read Speed:    {self.format_bytes(stats['avg_read'])}/s")
        print(f"Max Read Speed:    {self.format_bytes(stats['max_read'])}/s")
        print(f"Avg Write Speed:   {self.format_bytes(stats['avg_write'])}/s")
        print(f"Max Write Speed:   {self.format_bytes(stats['max_write'])}/s")
        print(f"Avg Disk Busy:     {stats['avg_busy']:.1f}%")
        print(f"Max Disk Busy:     {stats['max_busy']:.1f}%")
        print(f"{'='*70}\n")

    def run(self, duration=None):
        """Run the monitoring loop."""
        self.running = True
        start_time = time.time()
        
        print("Starting Disk I/O Monitor...")
        print(f"Interval: {self.interval}s | History: {self.history_size} samples")
        print("Press Ctrl+C to stop\n")
        
        try:
            self.prev_counters = self.get_disk_counters()
            
            while self.running:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(self.interval)
                
                current = self.get_disk_counters()
                metrics = self.calculate_metrics(current, self.prev_counters)
                
                if metrics:
                    self.history.append(metrics)
                    self.display_metrics(metrics)
                
                self.prev_counters = current
                
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
        finally:
            self.running = False
            self.display_statistics()


def list_disks():
    """List available disks and their partitions."""
    print("\nAvailable Disks and Partitions")
    print("=" * 60)
    
    disks = psutil.disk_io_counters(perdisk=True)
    partitions = psutil.disk_partitions()
    
    for disk_name in sorted(disks.keys()):
        print(f"\n{disk_name}:")
        disk_info = disks[disk_name]
        print(f"  Read Bytes:   {disk_info.read_bytes:,}")
        print(f"  Write Bytes:  {disk_info.write_bytes:,}")
        print(f"  Read Count:   {disk_info.read_count:,}")
        print(f"  Write Count:  {disk_info.write_count:,}")
    
    print("\n\nMounted Partitions:")
    print("-" * 60)
    for partition in partitions:
        print(f"  {partition.device:<25} -> {partition.mountpoint} ({partition.fstype})")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Real-time disk I/O performance monitoring tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Monitor all disks with default settings
  %(prog)s -i 0.5             Monitor with 0.5 second interval
  %(prog)s -d 30              Monitor for 30 seconds then exit
  %(prog)s --list             List available disks and exit
  %(prog)s -n 5               Keep history of 5 samples
        """
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=1.0,
        help='Update interval in seconds (default: 1.0)'
    )
    parser.add_argument(
        '-d', '--duration',
        type=float,
        default=None,
        help='Total monitoring duration in seconds (default: infinite)'
    )
    parser.add_argument(
        '-n', '--history',
        type=int,
        default=10,
        help='Number of samples to keep in history (default: 10)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available disks and exit'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_disks()
        return 0
    
    if args.interval < 0.1:
        print("Error: Interval must be at least 0.1 seconds")
        return 1
    
    monitor = DiskIOMonitor(
        interval=args.interval,
        history_size=args.history
    )
    
    monitor.run(duration=args.duration)
    return 0


if __name__ == "__main__":
    sys.exit(main())
