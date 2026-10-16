"""Lectura y validación de registros, sin depender de Streamlit."""

import csv
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNAS = [
    "semana", "codigo_partida", "partida", "especialidad", "encargado",
    "peso_partida", "avance_plan_semanal", "avance_real_semanal",
]
NUMERICAS = ["peso_partida", "avance_plan_semanal", "avance_real_semanal"]
TEXTOS = ["codigo_partida", "partida", "especialidad", "encargado"]


def validar_datos(datos):
    """Devolver una copia validada o explicar el problema mediante ValueError.

    Los avances son aportes ya ponderados al proyecto, como en el ET1.
    Se admite una diferencia de 0.05 pp por partida por redondeos del origen.
    """
    faltantes = [columna for columna in COLUMNAS if columna not in datos.columns]
    if faltantes:
        raise ValueError("Faltan columnas: " + ", ".join(faltantes))
    if datos.empty:
        raise ValueError("La base debe contener al menos un registro.")
    df = datos.loc[:, COLUMNAS].copy()
    for columna in ["semana"] + NUMERICAS:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")
        if not np.isfinite(df[columna].to_numpy(dtype=float)).all():
            raise ValueError(f"'{columna}' contiene valores vacíos o no numéricos.")
    if ((df["semana"] < 1) | (df["semana"] % 1 != 0)).any():
        raise ValueError("La semana debe ser un número entero positivo.")
    # Evitar desbordamientos al convertir semanas procedentes de un CSV.
    if (df["semana"] > np.iinfo(np.int32).max).any():
        raise ValueError("El número de semana es demasiado grande.")
    df["semana"] = df["semana"].astype(int)
    for columna in NUMERICAS:
        if (df[columna] < 0).any():
            raise ValueError(f"'{columna}' no puede tener valores negativos.")
    if ((df["peso_partida"] <= 0) | (df["peso_partida"] > 100)).any():
        raise ValueError("El peso de cada partida debe ser mayor que 0 y como máximo 100 %.")
    for columna in TEXTOS:
        if df[columna].isna().any():
            raise ValueError(f"'{columna}' contiene textos vacíos.")
        df[columna] = df[columna].astype(str).str.strip()
        if df[columna].eq("").any():
            raise ValueError(f"'{columna}' contiene textos vacíos.")
    if df.duplicated(["semana", "codigo_partida"]).any():
        raise ValueError("Hay registros duplicados para una misma semana y código de partida.")
    grupos = df.groupby("codigo_partida")
    for columna in TEXTOS[1:] + ["peso_partida"]:
        if (grupos[columna].nunique() > 1).any():
            raise ValueError(f"'{columna}' debe ser constante para un mismo código de partida.")
    partidas = grupos.agg(
        peso=("peso_partida", "first"),
        plan=("avance_plan_semanal", "sum"),
        real=("avance_real_semanal", "sum"),
    )
    exceso = (partidas["plan"] > partidas["peso"] + 0.05) | (
        partidas["real"] > partidas["peso"] + 0.05
    )
    if exceso.any():
        codigos = ", ".join(partidas.index[exceso].astype(str))
        raise ValueError("El avance acumulado supera el peso de estas partidas: " + codigos)
    return df.sort_values(["semana", "codigo_partida"]).reset_index(drop=True)


def leer_csv(origen: bytes | str | Path):
    """Leer un CSV UTF-8 desde una ruta o desde un archivo subido a la web."""
    if isinstance(origen, bytes):
        origen = BytesIO(origen)
    try:
        # Reconocer tanto la coma como el punto y coma como separadores.
        datos = pd.read_csv(origen, encoding="utf-8-sig", sep=None, engine="python")
    except (UnicodeError, csv.Error, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        raise ValueError("No se pudo leer el archivo. Usa la plantilla CSV guardada en UTF-8.") from error
    return validar_datos(datos)


def agregar_registro(datos, registro):
    """Agregar una fila solo cuando toda la base resultante sea válida."""
    combinado = pd.concat([datos, pd.DataFrame([registro])], ignore_index=True)
    return validar_datos(combinado)


def dataframe_a_csv(datos):
    """Crear bytes de un CSV compatible con los acentos en Excel."""
    return datos.to_csv(index=False).encode("utf-8-sig")
