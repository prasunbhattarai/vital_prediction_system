import os
import pynvml
import psutil
import time
from datetime import datetime
import pandas as pd
from backend.collector.database import Database
import requests

# URL = "http://127.0.0.1:8000/api/predict/"


current_pid = os.getpid()

database = Database()

columns = ["date","current_time","cpu_usage","cpu_freq","cpu_switches","memory_usage","memory_swap",
"disk_usage","read_write","net","bytes_sent","bytes_recv","battery_percent","power_plugged","gpu_usage","gpu_temp","top5_processes_cpu_average","top5_processes_cpu_std"]


def process_metrics():
    num_cores = psutil.cpu_count()
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    time.sleep(0.1)
    processes = []
    
    for proc in psutil.process_iter(['pid','cpu_percent']):
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




try: 
    df = pd.read_csv("metrics.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=columns)

try:
    pynvml.nvmlInit()
    gpu_available = True
except:
    gpu_available = False

try:
    prev_disk = psutil.disk_io_counters()
    prev_net = psutil.net_io_counters()
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

        if gpu_available:
            gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
            gpu_sensor = pynvml.NVML_TEMPERATURE_GPU
            gpu_temp = pynvml.nvmlDeviceGetTemperature(gpu_handle,gpu_sensor)
            # gpu_utilize = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle)
            gpu_usage = (gpu_info.used/gpu_info.total) * 100
        else :
            gpu_usage = None
            gpu_temp = None

        top5_processes_cpu_average, top5_processes_cpu_std = process_metrics()

        data ={}

        df.loc[len(df)] = [
            date,
            current_time,
            cpu_usage,
            cpu_freq.current if cpu_freq else None,
            cpu_switches.ctx_switches,
            memory_usage,
            memory_swap.percent,
            disk_usage,
            read_bytes + write_bytes,
            bytes_sent + bytes_recv,
            bytes_sent,
            bytes_recv,
            battery_percent,
            power_plugged,
            gpu_usage,
            gpu_temp,
            top5_processes_cpu_average,
            top5_processes_cpu_std
        ]
        time.sleep(2)

        data.update({
            "date": str(date),
            "current_time": current_time,
            "cpu_usage": cpu_usage,
            "cpu_freq": cpu_freq.current if cpu_freq else None,
            "cpu_switches": cpu_switches.ctx_switches,
            "memory_usage": memory_usage,
            "memory_swap": memory_swap.percent,
            "disk_usage": disk_usage,
            "read_write": read_bytes + write_bytes,
            "net": bytes_sent + bytes_recv,
            "bytes_sent": bytes_sent,
            "bytes_recv": bytes_recv,
            "battery_percent": battery_percent,
            "power_plugged": power_plugged,
            "gpu_usage": gpu_usage,
            "gpu_temp": gpu_temp,
            "top5_processes_cpu_average": top5_processes_cpu_average,
            "top5_processes_cpu_std": top5_processes_cpu_std
        })

        if len(df) % 10 == 0:
            df.to_csv("metrics.csv", index=False)
            print(f"Saved {len(df)} records to metrics.csv")


        database.insert_query(date, current_time, cpu_usage, cpu_freq.current if cpu_freq else None, cpu_switches.ctx_switches, memory_usage,
                 memory_swap.percent, disk_usage, read_bytes + write_bytes, bytes_sent + bytes_recv, bytes_sent, bytes_recv,
                 battery_percent, power_plugged, gpu_usage, gpu_temp, top5_processes_cpu_average, top5_processes_cpu_std)

        print(f"Date: {date}, Time: {current_time}")
        print(f"cpu_usage: {cpu_usage}%, memory_usage: {memory_usage}%, disk_usage: {disk_usage}%, gpu_gpu_usage: {gpu_usage}%")
        print(f"top5_processes_cpu_average: {top5_processes_cpu_average}%, top5_processes_cpu_std: {top5_processes_cpu_std}%")




except KeyboardInterrupt:
    df.to_csv("metrics.csv", index=False)
    print("Data collection stopped and saved to metrics.csv")