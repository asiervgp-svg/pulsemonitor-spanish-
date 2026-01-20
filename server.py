from http.server import BaseHTTPRequestHandler, HTTPServer
import psutil
from datetime import datetime
import json
import webbrowser
import threading
import time
import sys

class Handler(BaseHTTPRequestHandler): 
    def do_GET(self):
        if self.path == "/api/stats":
            self.send_stats_json()
        else:
            self.send_html()
    
    def send_stats_json(self):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent
        now = datetime.now().strftime("%H:%M:%S")
        
        data = {
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "now": now
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent
        now = datetime.now().strftime("%H:%M:%S")

        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>System Monitor</title>
<style>
body {{
    background: #0f172a;
    color: #e5e7eb;
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}}

.card {{
    background: #020617;
    padding: 30px 40px;
    border-radius: 12px;
    width: 360px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}}

h1 {{
    text-align: center;
    margin-bottom: 25px;
}}

.metric {{
    margin-bottom: 18px;
}}

.label {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}}

.bar {{
    background: #1e293b;
    border-radius: 6px;
    overflow: hidden;
    height: 16px;
}}

.fill {{
    height: 100%;
    transition: width 0.6s ease;
    background: linear-gradient(90deg, #22c55e, #4ade80);
}}


.footer {{
    text-align: center;
    font-size: 0.9em;
    margin-top: 20px;
    opacity: 0.8;
}}
</style>
</head>

<body>
<div class="card">
    <h1>🖥️ System Monitor</h1>
    <canvas id="chart" width="320" height="120" style="margin-bottom: 20px;"></canvas>
    <div class="metric">
        <div class="label">
            <span>CPU</span>
            <span id="cpu-value">{cpu}%</span>
        </div>
        <div class="bar">
            <div class="fill" id="cpu-bar" style="width:{cpu}%;"></div>
        </div>
    </div>

    <div class="metric">
        <div class="label">
            <span>RAM</span>
            <span id="ram-value">{ram}%</span>
        </div>
        <div class="bar">
            <div class="fill" id="ram-bar" style="width:{ram}%;"></div>
        </div>
    </div>

    <div class="metric">
        <div class="label">
            <span>DISK</span>
            <span id="disk-value">{disk}%</span>
        </div>
        <div class="bar">
            <div class="fill" id="disk-bar" style="width:{disk}%;"></div>
        </div>
    </div>

    <div class="footer">
        Última actualización: <span id="timestamp">{now}</span>
    </div>
</div>

<script>
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const history = [];
const MAX_POINTS = 60;

function drawChart() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (history.length < 2) return;

    ctx.beginPath();
    ctx.strokeStyle = "#22c55e";
    ctx.lineWidth = 2;

    history.forEach((value, index) => {{
        const x = (index / (MAX_POINTS - 1)) * canvas.width;
        const y = canvas.height - (value / 100) * canvas.height;

        if (index === 0) {{
            ctx.moveTo(x, y);
        }} else {{
            ctx.lineTo(x, y);
        }}
    }});

    ctx.stroke();
}}

async function updateStats() {{
    try {{
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Actualizar gráfico
        history.push(data.cpu);
        if (history.length > MAX_POINTS) {{
            history.shift();
        }}
        drawChart();
        
        document.getElementById('cpu-value').textContent = data.cpu.toFixed(1) + '%';
        document.getElementById('cpu-bar').style.width = data.cpu + '%';
        
        document.getElementById('ram-value').textContent = data.ram.toFixed(1) + '%';
        document.getElementById('ram-bar').style.width = data.ram + '%';
        
        document.getElementById('disk-value').textContent = data.disk.toFixed(1) + '%';
        document.getElementById('disk-bar').style.width = data.disk + '%';
        
        document.getElementById('timestamp').textContent = data.now;
    }} catch (error) {{
        console.error('Error actualizando stats:', error);
    }}
}}

// Actualizar cada 2 segundos
setInterval(updateStats, 2000);
// Actualizar inmediatamente al cargar
updateStats();
</script>
</body>
</html>
     """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:9000")

# Crear servidor con manejo de errores
try:
    server = HTTPServer(("0.0.0.0", 9000), Handler)
    print("Servidor creado correctamente")
except Exception as e:
    print("ERROR creando servidor:", e)
    input("Pulsa Enter para salir...")
    sys.exit(1)

# Arrancar servidor con manejo de errores
try:
    threading.Thread(target=open_browser, daemon=True).start()
    print("Servidor escuchando en puerto 9000...")
    server.serve_forever()
except Exception as e:
    print("ERROR ejecutando servidor:", e)
    input("Pulsa Enter para salir...")

