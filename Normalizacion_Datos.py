import pandas as pd
import numpy as np
import re
import json

def exportar_json_a_csv_limpio(data, archivo_salida="inmuebles_limpios.csv"):
    """
    Convierte una lista de JSONs o un DataFrame en un CSV con solo las columnas relevantes,
    todas en float o string. También convierte la antigüedad a años promedio.
    """

    
    if isinstance(data, pd.DataFrame):
        df = pd.json_normalize(data.to_dict(orient="records"), sep="_")
    else:
        df = pd.json_normalize(data, sep="_")

   
    columnas = [
        "precio_venta", "area", "habitaciones", "banos", "parqueaderos", "estrato",
        "barrio", "antiguedad", "localidad", "descripcion", "distancia_parque_m",
        "vigilancia", "jacuzzi", "chimenea", "permite_mascotas", "gimnasio",
        "ascensor", "conjunto_cerrado", "piscina", "salon_comunal", "terraza"
    ]
    columnas_presentes = [c for c in columnas if c in df.columns]
    df = df[columnas_presentes].copy()

    
    for col in df.columns:
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(
            r"^\s*\{['\"]?\$numberDouble['\"]?\s*:\s*['\"]?([^'\"}]*)['\"]?\}\s*$",
            r"\1", regex=True
        )
        df[col] = df[col].str.replace(r"[\$,]", "", regex=True)
        df[col] = df[col].replace(["None", "NaN", "nan", "null", "", " "], np.nan)

    
    mapa_antiguedad = {
        "NUEVO": 0,
        "ENTRE 0 Y 5 ANOS": 2.5,
        "ENTRE 5 Y 10 ANOS": 7.5,
        "ENTRE 10 Y 20 ANOS": 15,
        "MAS DE 20 ANOS": 25
    }

    def convertir_antiguedad(valor):
        if pd.isna(valor):
            return np.nan
        valor = str(valor).upper().strip()
        for clave, num in mapa_antiguedad.items():
            if clave in valor:
                return float(num)
        return np.nan

    if "antiguedad" in df.columns:
        df["antiguedad"] = df["antiguedad"].apply(convertir_antiguedad)

   
    cols_num = [
        "precio_venta", "area", "habitaciones", "banos", "parqueaderos", "estrato",
        "distancia_parque_m", "vigilancia", "jacuzzi", "chimenea", "permite_mascotas",
        "gimnasio", "ascensor", "conjunto_cerrado", "piscina", "salon_comunal",
        "terraza", "antiguedad"
    ]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    
    for col in ["barrio", "localidad", "descripcion"]:
        if col in df.columns:
            df[col] = df[col].astype(str).replace(["nan", "NaN", "None"], np.nan)

    
    df.to_csv(archivo_salida, index=False, encoding="utf-8")
    print(f"Archivo '{archivo_salida}' generado con éxito ({len(df)} filas, {len(df.columns)} columnas).")
    return df



data = pd.read_json("datos.json", orient='records')

d = data

df_limpio = exportar_json_a_csv_limpio(d, "inmuebles_limpios.csv")