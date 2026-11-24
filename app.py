"""Tablero en Solara para el proyecto Universal Bank: un KPI, un filtro y un gráfico.

Local:  solara run app.py --host localhost   ->  http://localhost:8765
"""
import pandas as pd
import solara
from matplotlib.figure import Figure

DATOS = "UniversalBank.csv"  # archivo limpio dentro de esta misma carpeta (sin ID ni ZIP Code)

clientes = pd.read_csv(DATOS)
mapa_educacion = {1: "Pregrado", 2: "Posgrado", 3: "Avanzado"}
clientes["nivel_educacion"] = clientes["Education"].map(mapa_educacion).fillna(clientes["Education"].astype(str))

# Una sola escala fija calculada sobre todos los segmentos para que no cambie con el filtro
TOPE = (clientes.groupby(["nivel_educacion", "Family"])["Personal Loan"].mean().max() * 100) * 1.15
educacion = solara.reactive("Todas")  # valor del filtro


def tasa_aceptacion(datos):
    # KPI: préstamos aceptados / total de clientes (sumar primero, dividir después, en %)
    if len(datos) == 0:
        return 0.0
    return (datos["Personal Loan"].sum() / len(datos)) * 100


@solara.component
def Page():
    datos = clientes if educacion.value == "Todas" else clientes[clientes["nivel_educacion"] == educacion.value]
    dif = (tasa_aceptacion(datos) / tasa_aceptacion(clientes) - 1) * 100  # frente a la línea base

    solara.Title("Aceptación de préstamo personal — Universal Bank")
    solara.Markdown("## Tasa de aceptación de préstamo personal por nivel educativo")
    solara.Select(
        label="Nivel educativo",
        value=educacion,
        values=["Todas"] + sorted(clientes["nivel_educacion"].unique()),
    )
    solara.Markdown(
        f"**Tasa de aceptación:** {tasa_aceptacion(datos):.2f} % ({dif:+.1f} % frente al total de clientes)"
    )

    serie = datos.groupby("Family")["Personal Loan"].mean() * 100  # tasa (%) según tamaño de familia
    ax = Figure(figsize=(7, 3)).subplots()
    ax.bar(serie.index.astype(str), serie.values, color="#2b6cb0")
    ax.set(
        ylim=(0, TOPE),
        xlabel="Tamaño de familia (integrantes)",
        ylabel="Aceptación de préstamo (%)",
        title="Tasa de aceptación por tamaño de familia",
    )
    solara.FigureMatplotlib(ax.figure)
    solara.Markdown(f"Datos: {DATOS}, {len(datos)} de {len(clientes)} filas. Fuente: Universal Bank.")
