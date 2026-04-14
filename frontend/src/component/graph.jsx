import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import "chart.js/auto";

function Graph() {
  const [cpuData, setCpuData] = useState([]);
  const [memoryData, setMemoryData] = useState([]);
  const [labels, setLabels] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [cpuAnomaly, setCpuAnomaly] = useState([]);
  const [memoryAnomaly, setMemoryAnomaly] = useState([]);
  const fetchData = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/predict/");
      const data = res.data;

      if (data.status === "success") {
        setCpuData(prev => [...prev, data.cpu_usage].slice(-50));
        setMemoryData(prev => [...prev, data.memory_usage].slice(-50));
        setLabels(prev => [...prev, data.time].slice(-50));
        setAnomalyData(prev => [...prev,data.anomaly === -1 ? 1 : 0].slice(-50));
        setCpuAnomaly(prev => [
          ...prev,
          data.anomaly === -1 ? data.cpu_usage : null
        ].slice(-50));

        setMemoryAnomaly(prev => [
          ...prev,
          data.anomaly === -1 ? data.memory_usage : null
        ].slice(-50));
      } else {
        console.log("Warming up...");
        console.log(data.length)
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);
  const chartOptions = {
    responsive: true,
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10, // optional: controls tick intervals
        }
      }
    }
  };

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Anomaly (CPU)",
        data: cpuAnomaly,
        borderColor: "transparent",
        backgroundColor: "red",
        pointRadius: cpuAnomaly.map(v => v !== null ? 6 : 0),
        showLine: false
      },
      {
        label: "CPU Usage",
        data: cpuData,
        borderColor: "red",
        fill: false,
      },


    ]
  };
  const chartData2 = {
    labels: labels,
    datasets: [
      {
        label: "Anomaly (Memory)",
        data: memoryAnomaly,
        borderColor: "transparent",
        backgroundColor: "orange",
        pointRadius: memoryAnomaly.map(v => v !== null ? 6 : 0),
        showLine: false
      },
      {
        label: "Memory Usage",
        data: memoryData,
        borderColor: "blue",
        fill: false,
      }

    ]
  };

  return (
    <div>
      <h2>System Metrics (Live)</h2>
      <Line data={chartData} options={chartOptions} />
      <Line data={chartData2} options={chartOptions} />
    </div>
  );
}

export default Graph;