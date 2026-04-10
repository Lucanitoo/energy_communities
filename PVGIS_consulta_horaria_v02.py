import requests
import json
import os

# --- Leer parámetros desde JSON ---
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "parametros_pvgis.json")

with open(json_path, "r", encoding="utf-8") as f:
    params = json.load(f)

lat = params["lat"]
lon = params["lon"]
startyear = params["startyear"]
endyear = params["endyear"]
peakpower = params["peakpower"]
angle = params["angle"]
azimuth = params["azimuth"]
loss = params["loss"]

# --- Construir URL PVGIS ---
url = (
    "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"
    f"?lat={lat}&lon={lon}"
    f"&startyear={startyear}&endyear={endyear}"
    "&radiation=2.5"
    "&pvcalculation=1"
    f"&peakpower={peakpower}"
    f"&angle={angle}"
    f"&aspect={azimuth}"
    f"&loss={loss}"
    "&outputformat=json"
    "&browser=0"
)

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Carpeta donde está el script .py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    txt_path = os.path.join(script_dir, "pvgis_hourly_production.txt")

    # Extraer datos horarios
    hourly = data["outputs"]["hourly"]

    # Crear TXT con índice secuencial y P
    with open(txt_path, "w", encoding="utf-8") as f:
        for i, row in enumerate(hourly, start=1):
            index = f"{i:04d}"   # convierte 1 → 0001, 12 → 0012, 8760 → 8760
            P = row["P"]
            f.write(f"{index};{P}\n")

    print(f"TXT generado en: {txt_path}")

else:
    print("Error:", response.status_code, response.text)