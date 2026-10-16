"""Seis funciones originales del Entregable 1 y coordinacion del analisis.

Las seis funciones se conservaron literalmente desde el codigo original.
No se importan lecturas, escrituras, animaciones ni ventanas del script ET1.
"""

import numpy as np
import pandas as pd

from .datos import validar_datos

def calcular_avance_semanal(datos):
    # Agrupar por semana y sumar los avances planificado y real
    resumen = datos.groupby("semana")[[
        "avance_plan_semanal",
        "avance_real_semanal"
    ]].sum().reset_index()

    # Redondear los resultados
    resumen[["avance_plan_semanal", "avance_real_semanal"]] = resumen[[
        "avance_plan_semanal",
        "avance_real_semanal"
    ]].round(2)

    # Devolver la tabla calculada
    return resumen


def calcular_avance_acumulado(datos_semanales):
    # Crear una copia para no modificar la tabla original
    resultado = datos_semanales.copy()

    # Calcular las sumas acumuladas
    resultado["avance_plan_acumulado"] = resultado["avance_plan_semanal"].cumsum()
    resultado["avance_real_acumulado"] = resultado["avance_real_semanal"].cumsum()

    # Redondear los valores
    resultado[["avance_plan_acumulado", "avance_real_acumulado"]] = resultado[[
        "avance_plan_acumulado",
        "avance_real_acumulado"
    ]].round(2)

    # Devolver la tabla
    return resultado


def calcular_diferencia_avance(datos_acumulados):
    # Crear una copia
    resultado = datos_acumulados.copy()

    # Calcular la diferencia: Real - Planificado
    resultado["diferencia"] = (
        resultado["avance_real_acumulado"] - resultado["avance_plan_acumulado"]
    ).round(2)

    # Evitar que aparezcan valores como -0.00
    resultado["diferencia"] = resultado["diferencia"].where(
        np.abs(resultado["diferencia"]) >= 0.005,
        0
    )

    # Clasificar el estado de la obra
    resultado["estado"] = np.where(
        resultado["diferencia"] > 0,
        "ADELANTADA",
        np.where(
            resultado["diferencia"] < 0,
            "RETRASADA",
            "SEGUN LO PREVISTO"
        )
    )

    # Devolver la tabla
    return resultado


def analizar_avance_especialidad(datos):
    # Agrupar por especialidad y sumar los avances
    resumen = datos.groupby("especialidad")[[
        "avance_plan_semanal",
        "avance_real_semanal"
    ]].sum()

    # Calcular la diferencia
    resumen["diferencia"] = (
        resumen["avance_real_semanal"] - resumen["avance_plan_semanal"]
    )

    # Redondear y convertir el índice en columna
    resumen = resumen.round(2).reset_index()

    # Evitar valores -0.00
    resumen["diferencia"] = resumen["diferencia"].where(
        np.abs(resumen["diferencia"]) >= 0.005,
        0
    )

    # Devolver la tabla
    return resumen


def contar_partidas_encargado(datos):
    # Conservar una sola fila por partida
    partidas_unicas = datos.drop_duplicates(subset="codigo_partida")

    # Agrupar por encargado y contar las partidas
    resumen = (
        partidas_unicas
        .groupby("encargado")["codigo_partida"]
        .count()
        .reset_index(name="cantidad_partidas")
    )

    # Devolver la tabla
    return resumen


def analizar_avance_encargado(datos):
    # Agrupar por encargado y sumar los avances
    resumen = datos.groupby("encargado")[[
        "avance_plan_semanal",
        "avance_real_semanal"
    ]].sum()

    # Calcular la diferencia
    resumen["diferencia"] = (
        resumen["avance_real_semanal"] - resumen["avance_plan_semanal"]
    )

    # Redondear y convertir el índice en columna
    resumen = resumen.round(2).reset_index()

    # Evitar valores -0.00
    resumen["diferencia"] = resumen["diferencia"].where(
        np.abs(resumen["diferencia"]) >= 0.005,
        0
    )

    # Devolver la tabla
    return resumen


def analizar_obra(datos, semana_corte=None, *, especialidades=None, encargados=None, partidas=None):
    """Aplicar filtros y coordinar las funciones originales del ET1.

    Los filtros vacíos incluyen todas las categorías. Los avances conservan
    sus aportes al total del proyecto; no se normalizan al filtrar partidas.
    """
    base = validar_datos(datos)
    peso_total = float(base.drop_duplicates("codigo_partida")["peso_partida"].sum())
    corte = int(semana_corte) if semana_corte is not None else int(base["semana"].max())
    filtros = {
        "especialidades": list(especialidades or []),
        "encargados": list(encargados or []),
        "partidas": list(partidas or []),
    }
    for nombre, columna in [
        ("especialidades", "especialidad"), ("encargados", "encargado"),
        ("partidas", "codigo_partida"),
    ]:
        if filtros[nombre]:
            base = base.loc[base[columna].isin(filtros[nombre])].copy()
    peso_seleccion = float(base.drop_duplicates("codigo_partida")["peso_partida"].sum())
    if semana_corte is not None:
        base = base.loc[base["semana"] <= corte].copy()
    if base.empty:
        raise ValueError("No hay registros para los filtros y la semana de corte elegidos. "
                         "Amplía la semana de corte o pulsa «Limpiar filtros».")
    semanal = calcular_diferencia_avance(
        calcular_avance_acumulado(calcular_avance_semanal(base))
    )
    ultima = semanal.iloc[-1]
    alertas = []
    if abs(peso_total - 100) > 0.1:
        alertas.append(
            f"Los pesos únicos de la base suman {peso_total:.2f} %. "
            "Para representar toda la obra deberían sumar 100 %. "
            "Los aportes se conservan tal como fueron ingresados."
        )
    return {
        "datos": base,
        "semanal": semanal,
        "especialidades": analizar_avance_especialidad(base),
        "encargados": analizar_avance_encargado(base),
        "partidas_encargado": contar_partidas_encargado(base),
        "indicadores": {
            "semana": corte,
            "ultima_semana_datos": int(ultima["semana"]),
            "plan": float(ultima["avance_plan_acumulado"]),
            "real": float(ultima["avance_real_acumulado"]),
            "diferencia": float(ultima["diferencia"]),
            "estado": str(ultima["estado"]),
            "partidas": int(base["codigo_partida"].nunique()),
            "semanas": int(base["semana"].nunique()),
        },
        "parametros": {
            **filtros,
            "semana_corte": corte,
            "peso_seleccion": peso_seleccion,
            "filtros_activos": any(filtros.values()),
        },
        "alertas": alertas,
    }
