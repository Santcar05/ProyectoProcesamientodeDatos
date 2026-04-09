import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# 1. CONFIGURACIÓN
BASE_URL = "https://www.datos.gov.co/resource/gt2j-8ykr.json"
LIMIT    = 50_000
OFFSET   = 0
ALL_ROWS = []
COLS     = "id_de_caso,departamento_nom,ciudad_municipio_nom,edad,sexo,estado,fecha_reporte_web"

print("=" * 55)
print("  COVID-19 Colombia — Descarga API datos.gov.co")
print("=" * 55)

# 2. DESCARGA PAGINADA
print("\n[1/3] Descargando datos del INS...")

while True:
    params = {
        "$select": COLS,
        "$limit":  LIMIT,
        "$offset": OFFSET,
        "$order":  "id_de_caso ASC"
    }
    resp = requests.get(BASE_URL, params=params, timeout=60)
    resp.raise_for_status()

    batch = resp.json()
    if not batch:
        break

    ALL_ROWS.extend(batch)
    OFFSET += LIMIT
    print(f"   Filas descargadas: {len(ALL_ROWS):,}", end="\r")

    if len(ALL_ROWS) >= LIMIT:
        break

print(f"\n   Total filas obtenidas: {len(ALL_ROWS):,}")

# 3. LIMPIEZA Y TRANSFORMACIÓN
print("\n[2/3] Procesando datos...")

df = pd.DataFrame(ALL_ROWS)
df["edad"]              = pd.to_numeric(df["edad"], errors="coerce")
df["fecha_reporte_web"] = pd.to_datetime(df["fecha_reporte_web"], errors="coerce")

top_dptos = (df.groupby("departamento_nom")
               .size()
               .reset_index(name="casos")
               .sort_values("casos", ascending=False)
               .head(12))

# 4. Grafico
print("\n[3/3] Generando gráfico...")

COLORS = ["#1d3557", "#457b9d"]

fig, ax = plt.subplots(figsize=(10, 7))
fig.suptitle("COVID-19 en Colombia — Top 12 departamentos por casos\nFuente: INS / datos.gov.co",
             fontsize=13, fontweight="bold")

top_dptos_sorted = top_dptos.sort_values("casos")
bars = ax.barh(top_dptos_sorted["departamento_nom"],
               top_dptos_sorted["casos"],
               color=COLORS[1], edgecolor="white", linewidth=.6)

# Destacar top 3
for bar in bars[-3:]:
    bar.set_color(COLORS[0])

ax.set_xlabel("Casos confirmados")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x/1000:.0f}K" if x >= 1000 else str(int(x))))
ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("covid19_colombia.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n  Grafico guardado como covid19_colombia.png")
print("  Proceso completado.\n")