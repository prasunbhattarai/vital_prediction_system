from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from anomaly.predict import feature_engineering
from collections import deque
from collector.database import Database

buffer = deque(maxlen=10)


columns = [
    "date","current_time","cpu_usage","cpu_freq","cpu_switches",
    "memory_usage","memory_swap","disk_usage","read_write","net",
    "bytes_sent","bytes_recv","battery_percent","power_plugged",
    "gpu_usage","gpu_temp","top5_processes_cpu_average",
    "top5_processes_cpu_std","id"
]

@api_view(['GET'])
def predict_anomaly(request):
    try:
        database = Database()
        data = database.select_recent()

        if data is None:
            return Response({
                "status": "error",
                "message": "No data available"
            })
            
        buffer.append(data)
        print("BUFFER SIZE:", len(buffer))
        print("DATA:", data)
        if len(buffer) < 10:
            print("BUFFER SIZE:", len(buffer))
            print("DATA:", data)
            return Response({
            "status": "Warming",
            "message": "Wait",
            "length": len(buffer)
        })
        else:
            window = list(buffer)
            df = pd.DataFrame(window, columns=columns)

            df = feature_engineering(df)
            print("DATA:", data)
            row = df.iloc[-1]
            return Response({
                "status": "success",
                "cpu_usage": float(row["cpu_usage"]),
                "memory_usage": float(row["memory_usage"]),
                "anomaly": int(row["anomaly"]),
                "time": data[1]
            })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        })