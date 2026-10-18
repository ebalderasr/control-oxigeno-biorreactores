"""Exploración visual del archivo Sartorius Biostat B (antes de ajustar FOPDT).

Genera en ./figuras:
  00_resumen_hojas.png     pO2 y agitación de las 3 hojas
  01_principal_pO2_RPM.png   figura principal: pO2 y agitación de la hoja .2
  02_escalones_alineados.png los dos escalones 200->500 RPM alineados en t0
  03_accesorias_TEMP_pH.png  temperatura y pH de la hoja .2
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fopdt_sartorius import cargar, detectar_escalones

ARCHIVO = Path(__file__).with_name("fermentador B1 levadura.xlsx")
FIGS = Path(__file__).with_name("figuras")

# Paleta (dataviz, modo claro)
C_PO2 = "#2a78d6"
C_STIR = "#eb6834"
C_TEMP = "#1baf7a"
C_PH = "#6250d6"
C_TXT2 = "#52514e"
C_ESCALON = "#2a78d6"

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#b9b8b2",
    "axes.labelcolor": C_TXT2,
    "xtick.color": C_TXT2,
    "ytick.color": C_TXT2,
    "axes.grid": True,
    "grid.color": "#e6e5e0",
    "grid.linewidth": 0.6,
    "lines.linewidth": 1.4,
    "figure.dpi": 130,
})


def ventanas_escalon(df, t0s, u1=500, antes=60):
    """(inicio, fin) de cada escalón: 60 s antes de t0 hasta que STIR deja u1."""
    ventanas = []
    for t0 in t0s:
        post = df[df["t"] >= t0]
        sale = post.index[post["STIR"] != u1]
        t_fin = df.loc[sale[0], "t"] if len(sale) else df["t"].iloc[-1]
        ventanas.append((t0 - antes, t_fin))
    return ventanas


def marcar_escalones(a, t0s, ventanas):
    for (ini, fin) in ventanas:
        a.axvspan(ini, fin, color=C_ESCALON, alpha=0.08, lw=0)
    for t0 in t0s:
        a.axvline(t0, color=C_ESCALON, lw=1, ls="--")


def fig_resumen(hojas):
    fig, ax = plt.subplots(2, len(hojas), figsize=(12, 5), sharex="col")
    for j, (nombre, df) in enumerate(hojas.items()):
        dt = np.median(np.diff(df["t"]))
        ax[0, j].plot(df["t"], df["pO2"], color=C_PO2)
        ax[0, j].set_title(f"{nombre}\nΔt ≈ {dt:.2f} s · T {df['TEMP'].min():.1f}–{df['TEMP'].max():.1f} °C",
                           fontsize=9, loc="left")
        ax[1, j].step(df["t"], df["STIR"], where="post", color=C_STIR)
        ax[1, j].set_xlabel("t [s]")
    ax[0, 0].set_ylabel("pO₂ [%sat]")
    ax[1, 0].set_ylabel("STIR [rpm]")
    fig.suptitle("Las tres hojas del archivo", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "00_resumen_hojas.png")
    plt.close(fig)


def fig_principal(df, t0s, ventanas, estados):
    """Figura principal: solo pO2 y RPM contra el tiempo."""
    fig, ax = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True,
                           gridspec_kw={"height_ratios": [2, 1]})
    ax[0].plot(df["t"], df["pO2"], color=C_PO2)
    ax[0].set_ylabel("pO₂ [%sat]")
    ax[1].step(df["t"], df["STIR"], where="post", color=C_STIR)
    ax[1].set_ylabel("Agitación [rpm]")
    ax[1].set_yticks([0, 200, 300, 400, 500])
    ax[1].set_xlabel("t [s]")
    for a in ax:
        marcar_escalones(a, t0s, ventanas)
    # y0 y y∞ de cada escalón como segmentos horizontales
    for k, (t0, (ini, fin), (y0, yinf)) in enumerate(zip(t0s, ventanas, estados)):
        ax[0].hlines(y0, ini, t0, color=C_TXT2, lw=1.2)
        ax[0].hlines(yinf, fin - 120, fin, color=C_TXT2, lw=1.2)
        ax[0].annotate(f"y₀ = {y0:.1f}", xy=(t0, y0), xytext=(6, -2), textcoords="offset points",
                       va="top", fontsize=8, color=C_TXT2)
        ax[0].annotate(f"y∞ = {yinf:.1f}", xy=(fin - 120, yinf), xytext=(0, -6), textcoords="offset points",
                       ha="right", va="top", fontsize=8, color=C_TXT2)
        ax[0].annotate(f"Escalón {k + 1}: 200→500 rpm\nt₀ = {t0:.0f} s · Δy = {yinf - y0:.1f} %",
                       xy=(t0, 97.5), xytext=(6, 0), textcoords="offset points",
                       va="top", fontsize=8.5, color=C_TXT2)
    ax[0].set_ylim(top=98)
    fig.suptitle("Hoja B1.20261014.2: respuesta de pO₂ a los escalones de agitación",
                 x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "01_principal_pO2_RPM.png")
    plt.close(fig)


def fig_accesoria(df, t0s, ventanas):
    """Temperatura y pH de la misma hoja (contexto)."""
    fig, ax = plt.subplots(2, 1, figsize=(12, 4.5), sharex=True)
    ax[0].plot(df["t"], df["TEMP"], color=C_TEMP)
    ax[0].set_ylabel("TEMP [°C]")
    ax[1].plot(df["t"], df["pH"], color=C_PH)
    ax[1].set_ylabel("pH")
    ax[1].set_xlabel("t [s]")
    for a in ax:
        marcar_escalones(a, t0s, ventanas)
    fig.suptitle("Hoja B1.20261014.2: variables accesorias (sombreado = ventanas de los escalones)",
                 x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "03_accesorias_TEMP_pH.png")
    plt.close(fig)


def fig_escalones(df, t0s, antes=150, despues=600):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    colores = ["#2a78d6", "#eb6834"]
    for k, t0 in enumerate(t0s):
        m = (df["t"] >= t0 - antes) & (df["t"] <= t0 + despues)
        tt = df.loc[m, "t"] - t0
        ax[0].plot(tt, df.loc[m, "pO2"], color=colores[k], marker="o", ms=2.5,
                   label=f"Escalón {k + 1} (t₀ = {t0:.0f} s)")
        ax[1].plot(tt, df.loc[m, "TEMP"], color=colores[k], label=f"Escalón {k + 1}")
    for a in ax:
        a.axvline(0, color=C_TXT2, lw=0.8, ls="--")
        a.set_xlabel("t − t₀ [s]")
        a.legend(frameon=False, loc="lower right")
    ax[0].set_ylabel("pO₂ [%sat]")
    ax[0].set_title("Respuesta de pO₂ (puntos = muestras de 5 s)", loc="left", fontsize=9)
    ax[1].set_ylabel("TEMP [°C]")
    ax[1].set_title("Temperatura durante cada escalón", loc="left", fontsize=9)
    fig.suptitle("Los dos escalones 200→500 rpm alineados en t₀", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "02_escalones_alineados.png")
    plt.close(fig)


def main():
    FIGS.mkdir(exist_ok=True)
    nombres = pd.ExcelFile(ARCHIVO).sheet_names
    hojas = {n: cargar(ARCHIVO, n) for n in nombres}
    fig_resumen(hojas)

    df = hojas["B1.20261014.2"]
    t0s = detectar_escalones(df)
    ventanas = ventanas_escalon(df, t0s)

    # Estados estacionarios y resumen numérico de cada escalón
    estados = []
    for k, (t0, (_, t_fin)) in enumerate(zip(t0s, ventanas)):
        pre = df[(df["t"] >= t0 - 60) & (df["t"] < t0)]
        meseta = df[(df["t"] >= t_fin - 120) & (df["t"] < t_fin)]
        y0, yinf = pre["pO2"].mean(), meseta["pO2"].mean()
        estados.append((y0, yinf))
        pendiente = np.polyfit(pre["t"], pre["pO2"], 1)[0] * 60
        print(f"Escalón {k + 1}: t0={t0:.1f} s, y0(60 s)={y0:.2f}, pendiente previa={pendiente:+.2f} %/min, "
              f"meseta hasta {t_fin:.0f} s: y∞={yinf:.2f} (σ={meseta['pO2'].std():.2f}), Δy={yinf - y0:.2f}")

    fig_principal(df, t0s, ventanas, estados)
    fig_escalones(df, t0s)
    fig_accesoria(df, t0s, ventanas)


if __name__ == "__main__":
    main()
