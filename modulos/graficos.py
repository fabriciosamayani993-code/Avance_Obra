"""Los cinco gráficos del ET1 convertidos en figuras interactivas."""

import plotly.graph_objects as go

AZUL = "#0645D8"
VERDE = "#008A63"


def _formato(figura, titulo, eje_x, eje_y):
    figura.update_layout(
        title=titulo, template="plotly_white", height=390,
        font=dict(family="Arial", color="#102F4C"),
        xaxis_title=eje_x, yaxis_title=eje_y,
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=30, r=25, t=100, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
    )
    figura.update_xaxes(gridcolor="#CCD8E5", color="#18344B")
    figura.update_yaxes(gridcolor="#CCD8E5", color="#18344B")
    return figura


def generar_curva_s(resumen):
    figura = go.Figure()
    for columna, nombre, color in [
        ("avance_plan_acumulado", "Planificado", AZUL),
        ("avance_real_acumulado", "Real", VERDE),
    ]:
        figura.add_trace(go.Scatter(
            x=resumen["semana"], y=resumen[columna], name=nombre,
            mode="lines+markers", line=dict(color=color, width=4),
            hovertemplate="Semana %{x}<br>%{y:.2f} %<extra>%{fullData.name}</extra>",
        ))
    figura.update_xaxes(dtick=1)
    return _formato(figura, "Curva S · avance acumulado", "Semana", "Avance acumulado (%)")


def _comparar(resumen, categoria, titulo, etiqueta):
    figura = go.Figure()
    for columna, nombre, color in [
        ("avance_plan_semanal", "Planificado", AZUL),
        ("avance_real_semanal", "Real", VERDE),
    ]:
        figura.add_trace(go.Bar(
            x=resumen[categoria], y=resumen[columna], name=nombre,
            marker_color=color,
            hovertemplate="%{x}<br>%{y:.2f} pp<extra>%{fullData.name}</extra>",
        ))
    figura.update_layout(barmode="group")
    return _formato(figura, titulo, etiqueta, "Aporte al proyecto (pp)")


def generar_produccion_semanal(resumen):
    figura = _comparar(resumen, "semana", "Producción semanal", "Semana")
    figura.update_xaxes(dtick=1)
    return figura


def generar_especialidades(resumen):
    return _comparar(resumen, "especialidad", "Avance por especialidad", "Especialidad")


def generar_encargados(resumen):
    return _comparar(resumen, "encargado", "Avance por encargado", "Encargado")


def generar_partidas_encargado(resumen):
    figura = go.Figure(go.Bar(
        x=resumen["encargado"], y=resumen["cantidad_partidas"],
        marker_color="#CF7400", text=resumen["cantidad_partidas"],
        textposition="outside", name="Partidas",
    ))
    figura.update_yaxes(dtick=1)
    return _formato(figura, "Partidas únicas por encargado", "Encargado", "Cantidad de partidas")


def generar_graficos(resultados):
    """Construir las figuras con las mismas tablas que se exportan a Excel."""
    return {
        "curva_s": generar_curva_s(resultados["semanal"]),
        "produccion_semanal": generar_produccion_semanal(resultados["semanal"]),
        "avance_especialidad": generar_especialidades(resultados["especialidades"]),
        "avance_encargado": generar_encargados(resultados["encargados"]),
        "partidas_encargado": generar_partidas_encargado(resultados["partidas_encargado"]),
    }
