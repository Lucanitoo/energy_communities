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

    # Extraer datos horarios
    hourly = data["outputs"]["hourly"]

    # Extraer solo la columna P en una lista
    P_utc = [row["P"] for row in hourly]  # longitud 8760

    # Crear lista vacía para P ajustado a España
    P_spain = [0.0] * 8760

    # --- Ajuste horario 2023 ---
    # Tramo 1: 0001–2018 → UTC+1 → desplazar 1 hacia abajo
    for i in range(0, 2018):
        if i - 1 >= 0:
            P_spain[i] = P_utc[i - 1]
        else:
            P_spain[i] = 0.0  # primera hora del año

    # Tramo 2: 2019–7225 → UTC+2 → desplazar 2 hacia abajo
    for i in range(2018, 7225):
        if i - 2 >= 0:
            P_spain[i] = P_utc[i - 2]
        else:
            P_spain[i] = 0.0

    # Tramo 3: 7226–8760 → UTC+1 → desplazar 1 hacia abajo
    for i in range(7225, 8760):
        if i - 1 >= 0:
            P_spain[i] = P_utc[i - 1]
        else:
            P_spain[i] = 0.0

    # --- Guardar TXT final ---
    txt_path = os.path.join(script_dir, "pvgis_indextime_spain.txt")

    with open(txt_path, "w", encoding="utf-8") as f:
        for i, P in enumerate(P_spain, start=1):
            index = f"{i:04d}"
            f.write(f"{index};{P}\n")

    print(f"TXT generado en: {txt_path}")

else:
    print("Error:", response.status_code, response.text)