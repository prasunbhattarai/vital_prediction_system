import os
import time
from datetime import datetime

import pandas as pd
import psutil
from django.core.management.base import BaseCommand

from vitals.models import Vitals

current_pid = os.getpid()

COLUMNS = [
    "date", "current_time", "cpu_usage", "cpu_freq", "cpu_switches",
    "memory_usage", "memory_swap", "disk_usage", "read_write", "net",
    "bytes_sent", "bytes_recv", "battery_percent", "power_plugged",
    "gpu_usage", "gpu_temp", "top5_processes_cpu_average",
    "top5_processes_cpu_std",
]

CSV_PATH = "metrics.csv"
gpu_available = False


def process_metrics():
    num_cores = psutil.cpu_count()
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    time.sleep(0.1)
    processes = []
    for proc in psutil.process_iter(['pid', 'cpu_percent']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            processes.append(proc.info['cpu_percent'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    processes.sort(reverse=True)
    top5 = processes[:5]
    top5_average = sum(top5) / len(top5) if top5 else 0
    top5_cpu_std = pd.Series(top5).std() if top5 else 0
    top5_average_percent = top5_average / num_cores
    top5_cpu_std_percent = top5_cpu_std / num_cores
    return top5_average_percent, float(top5_cpu_std_percent)


class Command(BaseCommand):
    help = "Collects system vitals (CPU, memory, disk, GPU, etc.) and saves to the database"

    def handle(self, *args, **options):
        global gpu_available

        try:
            import pynvml
            pynvml.nvmlInit()
            gpu_available = True
        except Exception:
            gpu_available = False

        try:
            df = pd.read_csv(CSV_PATH)
        except FileNotFoundError:
            df = pd.DataFrame(columns=COLUMNS)

        prev_disk = psutil.disk_io_counters()
        prev_net = psutil.net_io_counters()

        self.stdout.write(self.style.SUCCESS("Collector started. Press Ctrl+C to stop."))

        try:
            while True:
                now = datetime.now()
                date = now.date()
                current_time = now.strftime("%H:%M:%S")

                cpu_usage = psutil.cpu_percent(interval=1)
                cpu_freq = psutil.cpu_freq()
                cpu_switches = psutil.cpu_stats()

                memory_usage = psutil.virtual_memory().percent
                memory_swap = psutil.swap_memory()

                disk_usage = psutil.disk_usage('/').percent

                current_disk = psutil.disk_io_counters()
                current_net = psutil.net_io_counters()

                read_bytes = current_disk.read_bytes - prev_disk.read_bytes
                write_bytes = current_disk.write_bytes - prev_disk.write_bytes

                bytes_sent = current_net.bytes_sent - prev_net.bytes_sent
                bytes_recv = current_net.bytes_recv - prev_net.bytes_recv

                prev_disk = current_disk
                prev_net = current_net

                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else None
                power_plugged = battery.power_plugged if battery else None

                gpu_usage_val = None
                gpu_temp_val = None
                if gpu_available:
                    try:
                        import pynvml
                        gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        gpu_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
                        gpu_sensor = pynvml.NVML_TEMPERATURE_GPU
                        gpu_temp_val = pynvml.nvmlDeviceGetTemperature(gpu_handle, gpu_sensor)
                        gpu_usage_val = (gpu_info.used / gpu_info.total) * 100
                    except Exception:
                        pass

                top5_processes_cpu_average, top5_processes_cpu_std = process_metrics()

                Vitals.objects.create(
                    date=date,
                    current_time=current_time,
                    cpu_usage=cpu_usage,
                    cpu_freq=cpu_freq.current if cpu_freq else None,
                    cpu_switches=cpu_switches.ctx_switches,
                    memory_usage=memory_usage,
                    memory_swap=memory_swap.percent,
                    disk_usage=disk_usage,
                    read_write=read_bytes + write_bytes,
                    net=bytes_sent + bytes_recv,
                    bytes_sent=bytes_sent,
                    bytes_recv=bytes_recv,
                    battery_percent=battery_percent,
                    power_plugged=power_plugged,
                    gpu_usage=gpu_usage_val,
                    gpu_temp=gpu_temp_val,
                    top5_processes_cpu_average=top5_processes_cpu_average,
                    top5_processes_cpu_std=top5_processes_cpu_std,
                )

                row_data = [
                    date, current_time, cpu_usage,
                    cpu_freq.current if cpu_freq else None,
                    cpu_switches.ctx_switches, memory_usage,
                    memory_swap.percent, disk_usage,
                    read_bytes + write_bytes, bytes_sent + bytes_recv,
                    bytes_sent, bytes_recv, battery_percent, power_plugged,
                    gpu_usage_val, gpu_temp_val,
                    top5_processes_cpu_average, top5_processes_cpu_std,
                ]
                df.loc[len(df)] = row_data

                if len(df) % 10 == 0:
                    df.to_csv(CSV_PATH, index=False)
                    self.stdout.write(f"Saved {len(df)} records to metrics.csv")

                self.stdout.write(
                    f"CPU: {cpu_usage}% | Memory: {memory_usage}% | "
                    f"Disk: {disk_usage}% | GPU: {gpu_usage_val}%"
                )

                time.sleep(2)

        except KeyboardInterrupt:
            df.to_csv(CSV_PATH, index=False)
            self.stdout.write(self.style.SUCCESS(
                f"\nCollection stopped. {len(df)} records saved to metrics.csv"
            ))
