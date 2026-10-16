"""Inicio de la aplicación. Ejecutar: python -m streamlit run app.py.

Aquí se define la interfaz. Los cálculos, archivos y gráficos se importan
desde modulos/, como solicita la rúbrica del entregable 2.
"""

from pathlib import Path

import streamlit as st

from modulos.calculos import analizar_obra
from modulos.datos import agregar_registro, dataframe_a_csv, leer_csv, validar_datos
from modulos.exportacion import generar_excel
from modulos.graficos import generar_graficos

BASE = Path(__file__).resolve().parent
RUTA_BASE = BASE / "datos" / "base_datos_avance_obra.csv"
RUTA_PLANTILLA = BASE / "datos" / "plantilla_carga.csv"
RUTA_INFOGRAFIA = BASE / "INFOGRAFIA" / "infografia_funcionamiento.png"
RUTA_LOGO = BASE / "recursos" / "logo_empresa.webp"
RUTA_ESTILOS = BASE / "recursos" / "estilos.css"
AUTOR = "Fabricio Jamir Samayani Cutipa"


def guardar_en_sesion(datos, fuente, *, reiniciar_filtros=False):
    """Guardar una copia validada y preparar la selección de la última semana."""
    st.session_state["datos"] = validar_datos(datos)
    st.session_state["fuente"] = fuente
    st.session_state["revision"] = st.session_state.get("revision", 0) + 1
    st.session_state["ajustar_corte"] = True
    if reiniciar_filtros:
        for clave in ["analisis_especialidades", "analisis_encargados", "analisis_partidas"]:
            st.session_state[clave] = []
        st.session_state["filtro_encargado"] = "Todos"


def mostrar_grafico(figura, clave):
    # El contenedor aporta un borde y espacio interior a cada gráfico.
    with st.container(border=True, key=f"marco_{clave}"):
        st.plotly_chart(figura, width="stretch", key=clave)


def mostrar_indicador(columna, clave, etiqueta, valor):
    """Mostrar el resultado nativo con su icono lateral y tamaño adaptable."""
    with columna:
        with st.container(key=f"indicador_{clave}"):
            st.metric(etiqueta, valor)


def seleccion_multiple(etiqueta, opciones, clave, **configuracion):
    """Retirar selecciones que ya no existen al cambiar datos o filtros previos."""
    anteriores = st.session_state.get(clave, [])
    vigentes = [valor for valor in anteriores if valor in opciones]
    if clave not in st.session_state or anteriores != vigentes:
        st.session_state[clave] = vigentes
    return st.multiselect(etiqueta, opciones, key=clave,
                          placeholder="Todas las opciones", **configuracion)


def limpiar_filtros():
    """Restaurar todos los registros y la última semana antes de redibujar widgets."""
    for clave in ["analisis_especialidades", "analisis_encargados", "analisis_partidas"]:
        st.session_state[clave] = []
    st.session_state["semana_corte"] = int(st.session_state["datos"]["semana"].max())


def main():
    st.set_page_config(
        page_title="Avance físico de obra | Entregable 2",
        page_icon=str(RUTA_LOGO), layout="wide",
    )
    # Mantener el fondo azul de la página sin teñir las tablas y los campos.
    st.markdown(f"<style>{RUTA_ESTILOS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    if "datos" not in st.session_state:
        guardar_en_sesion(leer_csv(RUTA_BASE), "Base original del entregable 1", reiniciar_filtros=True)
    if "mensaje" in st.session_state:
        st.success(st.session_state.pop("mensaje"))

    with st.sidebar:
        with st.container(key="marca_lateral"):
            st.image(str(RUTA_LOGO), width=210)
            st.title("Avance de obra")
            st.caption("Entregable 2 · Python + IA")
        st.subheader("1. Fuente de datos")
        archivo = st.file_uploader("Selecciona un archivo CSV", type=["csv"], key="archivo_csv")
        if st.button("Usar archivo CSV", key="cargar_archivo", width="stretch"):
            if archivo is None:
                st.warning("Primero selecciona un archivo CSV.")
            else:
                try:
                    guardar_en_sesion(leer_csv(archivo.getvalue()), f"Archivo: {archivo.name}",
                                      reiniciar_filtros=True)
                    st.session_state["mensaje"] = "Archivo cargado y validado."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
        st.download_button(
            "Descargar plantilla CSV", RUTA_PLANTILLA.read_bytes(),
            "plantilla_carga.csv", "text/csv", width="stretch",
        )
        if st.button("Restaurar base del entregable 1", key="restaurar", width="stretch"):
            guardar_en_sesion(leer_csv(RUTA_BASE), "Base original del entregable 1", reiniciar_filtros=True)
            st.session_state["mensaje"] = "Se restauró la base original."
            st.rerun()
        st.caption(st.session_state["fuente"])
        cantidad_encargados = st.session_state["datos"]["encargado"].nunique()
        st.caption(f"{cantidad_encargados} encargados detectados en la base actual.")
        st.divider()
        semanas = sorted(st.session_state["datos"]["semana"].unique().tolist())
        if st.session_state.pop("ajustar_corte", False) or st.session_state.get("semana_corte") not in semanas:
            st.session_state["semana_corte"] = semanas[-1]
        with st.expander("2. Parámetros del análisis", expanded=True):
            corte = st.selectbox("Semana de corte", semanas, key="semana_corte")
            st.caption("Se acumulan los avances desde el inicio hasta la semana elegida.")
            disponibles = st.session_state["datos"]
            especialidades = seleccion_multiple(
                "Especialidades", sorted(disponibles["especialidad"].unique().tolist()),
                "analisis_especialidades", help="Sin selección se incluyen todas las especialidades.",
            )
            if especialidades:
                disponibles = disponibles.loc[disponibles["especialidad"].isin(especialidades)]
            encargados = seleccion_multiple(
                "Encargados", sorted(disponibles["encargado"].unique().tolist()),
                "analisis_encargados", help="Se muestran los encargados de las especialidades elegidas.",
            )
            if encargados:
                disponibles = disponibles.loc[disponibles["encargado"].isin(encargados)]
            nombres = disponibles.drop_duplicates("codigo_partida").set_index("codigo_partida")["partida"].to_dict()
            partidas = seleccion_multiple(
                "Partidas", sorted(nombres), "analisis_partidas",
                format_func=lambda codigo: f"{codigo} · {nombres[codigo]}",
                help="Se muestran las partidas compatibles con los filtros anteriores.",
            )
            st.caption("Puedes elegir varias opciones en cada lista. Una lista vacía incluye todas las opciones disponibles.")
            st.button("Limpiar filtros", key="limpiar_filtros", on_click=limpiar_filtros, width="stretch")

    try:
        resultados = analizar_obra(
            st.session_state["datos"], corte,
            especialidades=especialidades, encargados=encargados, partidas=partidas,
        )
    except ValueError as error:
        st.info(str(error))
        st.stop()
    figuras = generar_graficos(resultados)
    indicadores = resultados["indicadores"]
    parametros = resultados["parametros"]

    with st.container(key="cabecera"):
        logo, titulo = st.columns([1, 7])
        with logo:
            st.image(str(RUTA_LOGO), width=130)
        with titulo:
            st.markdown('<p class="subtitulo-proyecto">INGENIERÍA CIVIL · PYTHON + IA</p>', unsafe_allow_html=True)
            st.title("Control del avance físico de obra")
            st.markdown(f'<p class="autor-proyecto">Realizado por {AUTOR}</p>', unsafe_allow_html=True)
        st.write("Compara el avance planificado y real, identifica desviaciones y exporta tus resultados.")
    st.caption(f"Semana de corte: {corte} · {indicadores['partidas']} partidas · "
               f"{len(resultados['datos'])} registros analizados")
    if parametros["filtros_activos"]:
        st.info(f"Vista filtrada · Las partidas seleccionadas pesan {parametros['peso_seleccion']:.2f} % "
                "de la obra. Los avances mostrados son sus aportes al total del proyecto.")
    if indicadores["ultima_semana_datos"] < corte:
        st.caption(f"La última semana con registros de esta selección es la {indicadores['ultima_semana_datos']}.")
    columnas = st.columns(4)
    mostrar_indicador(columnas[0], "ap", "AP · Avance planificado", f"{indicadores['plan']:.2f} %")
    mostrar_indicador(columnas[1], "ar", "AR · Avance real", f"{indicadores['real']:.2f} %")
    mostrar_indicador(columnas[2], "desviacion", "Desviación real − plan", f"{indicadores['diferencia']:+.2f} pp")
    mostrar_indicador(columnas[3], "estado", "Estado", indicadores["estado"])
    for alerta in resultados["alertas"]:
        st.warning(alerta)

    resumen, detalle, datos, exportar, ayuda = st.tabs([
        "Resumen de la obra", "Especialidades y encargados", "Carga y edición de datos",
        "Exportar resultados", "Cómo funciona",
    ])
    with resumen:
        izquierda, derecha = st.columns(2)
        with izquierda:
            mostrar_grafico(figuras["curva_s"], "grafico_curva_s")
        with derecha:
            mostrar_grafico(figuras["produccion_semanal"], "grafico_produccion")
        st.markdown('<hr class="separador-resumen">', unsafe_allow_html=True)
        st.subheader("Resumen semanal")
        st.dataframe(resultados["semanal"], hide_index=True, width="stretch")
        st.caption("La desviación se expresa en puntos porcentuales (pp), no en semanas de atraso.")

    with detalle:
        izquierda, derecha = st.columns(2)
        with izquierda:
            mostrar_grafico(figuras["avance_especialidad"], "grafico_especialidades")
            st.dataframe(resultados["especialidades"], hide_index=True, width="stretch")
        with derecha:
            mostrar_grafico(figuras["avance_encargado"], "grafico_encargados")
            st.dataframe(resultados["encargados"], hide_index=True, width="stretch")
        mostrar_grafico(figuras["partidas_encargado"], "grafico_partidas")
        with st.expander("Consultar registros por encargado"):
            opciones = ["Todos"] + sorted(resultados["datos"]["encargado"].unique().tolist())
            if st.session_state.get("filtro_encargado") not in opciones:
                st.session_state["filtro_encargado"] = "Todos"
            encargado = st.selectbox("Encargado", opciones, key="filtro_encargado")
            tabla = resultados["datos"]
            if encargado != "Todos":
                tabla = tabla.loc[tabla["encargado"] == encargado]
            st.dataframe(tabla, hide_index=True, width="stretch")
        st.caption("Los avances por especialidad y encargado son aportes al total de la obra.")

    with datos:
        st.subheader("Ingresar un registro manualmente")
        st.info("Introduce aportes semanales ya ponderados. Si una partida pesa 4 % y ejecutas "
                "el 50 % de esa partida durante la semana, ingresa 2.00 pp como avance real.")
        st.caption("Para una partida existente, conserva su código, descripción, especialidad, "
                   "encargado y peso. Para corregir un registro existente, utiliza la tabla inferior.")
        with st.form("registro_manual"):
            c1, c2 = st.columns(2)
            with c1:
                semana = st.number_input("Semana", min_value=1, value=int(semanas[-1]), step=1,
                                         key="manual_semana")
                codigo = st.text_input("Código de partida", key="manual_codigo")
                partida = st.text_input("Descripción de partida", key="manual_partida")
                especialidad = st.text_input("Especialidad", key="manual_especialidad")
            with c2:
                encargado = st.text_input("Encargado", key="manual_encargado")
                peso = st.number_input("Peso de la partida (%)", min_value=0.01, max_value=100.0,
                                       value=4.0, step=0.01, format="%.4f", key="manual_peso")
                plan = st.number_input("Avance planificado semanal (pp)", min_value=0.0,
                                       max_value=100.0, step=0.01, format="%.4f", key="manual_plan")
                real = st.number_input("Avance real semanal (pp)", min_value=0.0,
                                       max_value=100.0, step=0.01, format="%.4f", key="manual_real")
            if st.form_submit_button("Agregar registro", type="primary"):
                try:
                    nuevos = agregar_registro(st.session_state["datos"], {
                        "semana": semana, "codigo_partida": codigo, "partida": partida,
                        "especialidad": especialidad, "encargado": encargado,
                        "peso_partida": peso, "avance_plan_semanal": plan,
                        "avance_real_semanal": real,
                    })
                    guardar_en_sesion(nuevos, "Base modificada manualmente")
                    st.session_state["mensaje"] = "Registro agregado. Los resultados se actualizaron."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

        st.subheader("Editar o eliminar registros")
        st.caption("Esta tabla muestra toda la base, independientemente de los filtros del análisis.")
        with st.form(f"edicion_{st.session_state['revision']}"):
            editados = st.data_editor(
                st.session_state["datos"], hide_index=True, num_rows="dynamic", width="stretch",
                key=f"editor_{st.session_state['revision']}",
            )
            if st.form_submit_button("Guardar cambios de la tabla"):
                try:
                    guardar_en_sesion(editados, "Base modificada desde la tabla")
                    st.session_state["mensaje"] = "Cambios guardados y resultados actualizados."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
        st.warning("Los cambios se conservan durante esta sesión. Descarga la base actualizada "
                   "para conservarlos al cerrar o recargar la página.")
        st.download_button(
            "Descargar base actualizada (.csv)", dataframe_a_csv(st.session_state["datos"]),
            "base_datos_avance_obra_actualizada.csv", "text/csv", width="stretch",
        )

    with exportar:
        st.subheader("Reporte de resultados en Excel")
        st.write(f"El reporte corresponde a la semana {corte}. Incluye el dashboard, cinco "
                 "tablas de datos y resultados, y cinco gráficos editables en Excel. "
                 "Respeta los filtros elegidos en la barra lateral.")
        st.download_button(
            "Descargar reporte Excel (.xlsx)", generar_excel(resultados),
            f"reporte_avance_obra_semana_{corte}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary", width="stretch",
        )
        st.download_button(
            "Descargar resumen semanal (.csv)", dataframe_a_csv(resultados["semanal"]),
            f"resumen_semanal_{corte}.csv", "text/csv", width="stretch",
        )
        st.caption("El reporte contiene resultados calculados por Python. Para recalcular con "
                   "nuevos datos, utiliza la aplicación y descarga un reporte actualizado.")

    with ayuda:
        st.subheader("Del registro de obra al reporte")
        st.write("CSV o ingreso manual → validación → cálculos del entregable 1 → "
                 "cinco gráficos y tablas → descarga en Excel.")
        st.write("La curva S suma progresivamente los aportes semanales. La desviación es "
                 "el avance real acumulado menos el planificado. Un valor negativo indica "
                 "avance inferior a lo programado.")
        st.write("En «Parámetros del análisis» puedes desplegar los filtros de especialidad, encargado "
                 "y partida. Los cambios se aplican a indicadores, tablas, gráficos y al reporte. "
                 "Los porcentajes conservan su referencia al total de la obra.")
        if RUTA_INFOGRAFIA.is_file():
            st.image(str(RUTA_INFOGRAFIA), caption="Infografía del funcionamiento y resultados "
                     "con la base original del entregable 1", width="stretch")
            st.download_button("Descargar infografía", RUTA_INFOGRAFIA.read_bytes(),
                               "infografia_funcionamiento.png", "image/png")
        st.caption(f"{AUTOR} · Especialización Python + IA aplicada a Ingeniería Civil")


if __name__ == "__main__":
    main()
