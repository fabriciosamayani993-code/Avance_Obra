# Entregable 2 Python · Control del avance físico de obra

**Realizado por Fabricio Jamir Samayani Cutipa.**

Aplicación de Streamlit para comparar el avance planificado y real de una obra,
consultar indicadores y gráficos, ingresar datos y descargar resultados.

## Ejecutar en este equipo

Abre la terminal de PowerShell en Visual Studio Code y copia estas dos líneas:

```powershell
cd "C:\Users\Usuario\Documents\ESPECIALIZACION PYTHON\ENTREGABLE 2 PYTHON"
& "..\.venv\Scripts\python.exe" -B -m streamlit run app.py
```

Este comando utiliza el entorno de Python que ya existe en la carpeta principal
`ESPECIALIZACION PYTHON`. La opción `-B` evita generar archivos de caché de Python.

Si aparece un error indicando que falta una librería, ejecuta desde la carpeta
del proyecto y después vuelve a iniciar la aplicación:

```powershell
& "..\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Abre la dirección que muestra la terminal, normalmente **http://localhost:8501**.
Mantén la terminal abierta mientras utilizas la página. Para detenerla,
presiona **Ctrl+C**.

## Ejecutar en otro equipo

Con Python y pip disponibles, abre la terminal dentro de `ENTREGABLE 2 PYTHON`:

```powershell
python -m pip install -r requirements.txt
python -B -m streamlit run app.py
```

El archivo que se ejecuta es `app.py`. Conserva las carpetas del proyecto junto
a ese archivo para que encuentre sus módulos, datos e imágenes.

## Cómo utilizar la aplicación

1. Al iniciar se carga la base original del entregable 1: 20 partidas y 12 semanas.
2. Para probar otro escenario, selecciona un CSV de `datos/` en la barra lateral
   y pulsa **Usar archivo CSV**.
3. Despliega **Parámetros del análisis** para elegir la semana de corte y filtrar
   especialidades, encargados y partidas. Una lista vacía incluye todas las opciones.
4. Consulta los indicadores, las tablas y los cinco gráficos en las pestañas de resultados.
5. En **Carga y edición de datos**, ingresa los ocho campos del formulario o
   modifica la tabla y guarda los cambios.
6. En **Exportar resultados**, descarga el reporte Excel o el resumen CSV.

Al cargar otro CSV se reinician los filtros y se detectan los encargados de ese
archivo. Las cinco bases adicionales representan adelanto, atraso, recuperación,
pausa y avance variable; tienen 16, 20 o 24 semanas y equipos de encargados distintos.
El archivo `01_obra_adelantada_20_semanas.csv` tiene **10 encargados** para probar
los filtros, los gráficos y la exportación con un equipo más grande.

Los avances semanales son aportes ya ponderados al total de la obra, en puntos
porcentuales. Por ejemplo, si una partida pesa 4 % y ejecutas el 50 % durante
una semana, ingresa **2.00 pp** de avance real.

**Descarga la base actualizada antes de cerrar o recargar la página**, porque
los cambios manuales se conservan únicamente durante la sesión.

## Organización del proyecto

| Archivo o carpeta | Función |
|---|---|
| `app.py` | Interfaz y punto de inicio de la aplicación |
| `requirements.txt` | Librerías necesarias |
| `modulos/calculos.py` | Funciones del entregable 1 y análisis de resultados |
| `modulos/datos.py` | Lectura CSV, validación e ingreso de registros |
| `modulos/graficos.py` | Preparación de los cinco gráficos |
| `modulos/exportacion.py` | Generación del reporte Excel |
| `modulos/__init__.py` | Identificación del paquete de funciones |
| `datos/` | Base original, plantilla y cinco CSV adicionales de prueba |
| `recursos/` | Logo y estilos de la página |
| `.streamlit/config.toml` | Configuración de colores |
| `INFOGRAFIA/` | Imagen del funcionamiento del código, generada con IA |
| `referencias/entregable_1/` | Copia del script original utilizado como referencia |
| `pruebas/` | Comprobaciones de cálculos, archivos e interfaz |

Las seis funciones de análisis proceden del entregable 1 y se importan desde
`modulos/calculos.py`. Con la base original, el avance planificado es **99.99 %**,
el real **98.83 %**, la desviación **−1.16 pp** y el estado **RETRASADA**.

La infografía muestra ese ejemplo fijo de la semana 12. Los resultados de otros
archivos o filtros se consultan en la página y en el reporte descargado.

## Comprobar el funcionamiento

Desde `ENTREGABLE 2 PYTHON`, en este equipo:

```powershell
& "..\.venv\Scripts\python.exe" -B -m unittest discover -s pruebas -v
```

Para entregar el trabajo, comprime la carpeta del proyecto incluyendo
`.streamlit/config.toml`. Excluye entornos `.venv`, carpetas `__pycache__`
y archivos temporales.
