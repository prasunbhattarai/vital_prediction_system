from collections import deque

import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response

from vitals.models import Vitals
from .engine import feature_engineering
from .models import AnomalyResult

buffer = deque(maxlen=10)

COLUMNS = [
    "date", "current_time", "cpu_usage", "cpu_freq", "cpu_switches",
    "memory_usage", "memory_swap", "disk_usage", "read_write", "net",
    "bytes_sent", "bytes_recv", "battery_percent", "power_plugged",
    "gpu_usage", "gpu_temp", "top5_processes_cpu_average",
    "top5_processes_cpu_std", "id",
]


@api_view(['GET'])
def predict_anomaly(request):
    try:
        latest = Vitals.objects.order_by('-id').first()
        if latest is None:
            return Response({"status": "error", "message": "No data available"})

        row = [
            latest.date, latest.current_time, latest.cpu_usage, latest.cpu_freq,
            latest.cpu_switches, latest.memory_usage, latest.memory_swap,
            latest.disk_usage, latest.read_write, latest.net, latest.bytes_sent,
            latest.bytes_recv, latest.battery_percent, latest.power_plugged,
            latest.gpu_usage, latest.gpu_temp, latest.top5_processes_cpu_average,
            latest.top5_processes_cpu_std, latest.id,
        ]
        buffer.append(row)

        if len(buffer) < 10:
            return Response({
                "status": "Warming",
                "message": "Wait",
                "length": len(buffer),
            })

        window = list(buffer)
        df = pd.DataFrame(window, columns=COLUMNS)
        df = feature_engineering(df)
        row = df.iloc[-1]

        AnomalyResult.objects.create(
            cpu_usage=float(row["cpu_usage"]),
            memory_usage=float(row["memory_usage"]),
            anomaly=int(row["anomaly"]),
        )

        return Response({
            "status": "success",
            "cpu_usage": float(row["cpu_usage"]),
            "memory_usage": float(row["memory_usage"]),
            "anomaly": int(row["anomaly"]),
            "time": latest.current_time.strftime("%H:%M:%S") if latest.current_time else "",
        })
    except Exception as e:
        return Response({"status": "error", "message": str(e)})


@api_view(['GET'])
def anomaly_history(request):
    queryset = AnomalyResult.objects.all()[:50]
    data = [
        {
            "cpu_usage": r.cpu_usage,
            "memory_usage": r.memory_usage,
            "anomaly": r.anomaly,
            "detected_at": r.detected_at,
        }
        for r in queryset
    ]
    return Response(data)
