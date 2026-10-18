"""Identificación FOPDT de pO2 ante un escalón de agitación y sintonía PI para Sartorius Biostat B.

Uso:
    .venv/bin/python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 2

Salidas:
    datos_limpios/<hoja>_escalon<k>.csv   t, t_rel, pO2, pO2_filtrada, STIR, TEMP, pH
    resultados/<hoja>_escalon<k>.json     y0, y∞, Δy, Kp, Kp_norm, τ, θ, Xp y TI por método
    figuras/10_<hoja>_escalon<k>_filtro.png  cruda vs filtrada + estados estacionarios
    figuras/11_<hoja>_escalon<k>_ajuste.png  Smith y mínimos cuadrados sobre los datos
    figuras/12_<hoja>_escalon<k>_criterios.png  cómo lee la curva cada método (tangente, SIMC, Smith)

Span = N_max − N_min configurado en la cascada de pO2 (por defecto 200–1200 rpm → 1000 rpm).
"""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

BASE = Path(__file__).parent
SPAN = 1000.0         # rpm: 200 a 1200 en la cascada del Biostat B
U0, U1 = 200.0, 500.0

C_DATOS = "#9a9890"
C_PO2 = "#2a78d6"
C_SMITH = "#eb6834"
C_LSQ = "#1baf7a"
C_TAN = "#6250d6"
C_STIR = "#eb6834"
C_TXT2 = "#52514e"

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


# ---------------------------------------------------------------- carga

def cargar(archivo, hoja=0) -> pd.DataFrame:
    """Lee una exportación Sartorius (xlsx con filas 'Value' y unidades bajo el encabezado).

    Devuelve columnas estándar: t [s], pO2, STIR, TEMP, pH.
    """
    df = pd.read_excel(archivo, sheet_name=hoja, header=0, skiprows=[1, 2])
    df = df.rename(columns={"pO2_1": "pO2", "STIRR_1": "STIR", "TEMP_1": "TEMP", "pH_1": "pH"})
    # Algunas celdas vienen guardadas como texto en el xlsx
    for col in ["ProcessTime", "pH", "pO2", "STIR", "TEMP", "tiempo"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["PDatTime", "pO2", "STIR"]).reset_index(drop=True)
    # Tiempo real desde PDatTime; 'tiempo' asume 5 s exactos y deriva (~0.8 %)
    if pd.api.types.is_datetime64_any_dtype(df["PDatTime"]):
        df["t"] = (df["PDatTime"] - df["PDatTime"].iloc[0]).dt.total_seconds()
    else:  # número serial de Excel en días
        pdat = pd.to_numeric(df["PDatTime"], errors="coerce")
        df["t"] = (pdat - pdat.iloc[0]) * 86400.0
    return df


def detectar_escalones(df, u0=U0, u1=U1, max_muestras=3):
    """Instantes donde STIR pasa de u0 a u1 en <= max_muestras muestras."""
    s = df["STIR"].to_numpy()
    t0s = []
    for i in range(1, len(s)):
        if s[i] == u1 and s[i - 1] != u1:
            if np.any(s[max(0, i - max_muestras):i] == u0):
                t0s.append(df["t"].iloc[i])
    return t0s


def fin_escalon(df, t0, u1=U1):
    """Último instante con STIR = u1 tras el escalón."""
    post = df[df["t"] >= t0]
    sale = post.index[post["STIR"] != u1]
    return df.loc[sale[0], "t"] if len(sale) else df["t"].iloc[-1]


# ---------------------------------------------------------------- identificación

def filtrar(y, ventana=5, orden=2):
    """Savitzky-Golay centrado (sin desfase). Con Δt = 5 s, 5 puntos = 25 s."""
    return savgol_filter(y, ventana, orden)


def cruce(t, y, nivel):
    """Primer instante (interpolado) en que y alcanza 'nivel' subiendo."""
    i = np.argmax(y >= nivel)
    if i == 0:
        return t[0]
    return t[i - 1] + (nivel - y[i - 1]) * (t[i] - t[i - 1]) / (y[i] - y[i - 1])


def smith(t, y, t0, y0, yinf):
    """Método de dos puntos (Smith): τ = 1.5 (t63 − t28), θ = (t63 − t0) − τ."""
    dy = yinf - y0
    t28 = cruce(t, y, y0 + 0.283 * dy)
    t63 = cruce(t, y, y0 + 0.632 * dy)
    tau = 1.5 * (t63 - t28)
    theta = (t63 - t0) - tau
    return {"t28": t28, "t63": t63, "tau": tau, "theta": theta}


def tangente(t, y, t0, y0, yinf):
    """Ziegler-Nichols: recta tangente en el punto de máxima pendiente.

    θ = cruce de la tangente con y0 (menos t0); τ = tiempo entre los cruces con y0 y con y∞.
    """
    pend = np.diff(y) / np.diff(t)
    i = int(np.argmax(pend))
    s = pend[i]
    tm, ym = (t[i] + t[i + 1]) / 2, (y[i] + y[i + 1]) / 2
    ta = tm - (ym - y0) / s
    tb = tm + (yinf - ym) / s
    return {"pendiente": s, "t_pend": tm, "y_pend": ym, "ta": ta, "tb": tb,
            "theta": ta - t0, "tau": tb - ta}


def skogestad(t, y, t0, y0, yinf, umbral=0.5):
    """SIMC: θ = cuando la salida empieza a moverse (> y0 + umbral %pO2);
    τ = tiempo adicional hasta el 63.2 % del cambio."""
    dy = yinf - y0
    post = t >= t0
    t_mov = cruce(t[post], y[post], y0 + umbral)
    t63 = cruce(t, y, y0 + 0.632 * dy)
    return {"t_mov": t_mov, "t63": t63, "theta": t_mov - t0, "tau": t63 - t_mov}


def fopdt(t, y0, kp, du, t0, theta, tau):
    """Respuesta FOPDT a un escalón du aplicado en t0."""
    x = np.clip(t - t0 - theta, 0, None)
    return y0 + kp * du * (1 - np.exp(-x / tau))


def ajuste_lsq(t, y, t0, y0, du, p0):
    """Mínimos cuadrados no lineales para Kp, θ, τ (y0, du, t0 fijos)."""
    f = lambda tt, kp, theta, tau: fopdt(tt, y0, kp, du, t0, theta, tau)
    popt, pcov = curve_fit(f, t, y, p0=p0, bounds=([0, 0, 1], [np.inf, 300, 3000]))
    err = np.sqrt(np.diag(pcov))
    return {"Kp": popt[0], "theta": popt[1], "tau": popt[2],
            "sd": {"Kp": err[0], "theta": err[1], "tau": err[2]}}


# ---------------------------------------------------------------- sintonía Sartorius

REGLAS = {
    "Ziegler-Nichols": lambda k, tau, th: (0.9 / k * tau / th, 3.33 * th),
    "SIMC": lambda k, tau, th: (tau / (2 * th) / k, min(tau, 8 * th)),
    "ITAE carga": lambda k, tau, th: (0.859 / k * (th / tau) ** -0.977, tau / 0.674 * (th / tau) ** 0.680),
}


def regla(metodo, kp_norm, tau, theta):
    """Xp [%] y TI [s] para el PI del Biostat B (Xp = 100 / Kc,norm; TD = 0)."""
    kc, ti = REGLAS[metodo](kp_norm, tau, theta)
    return {"Kc_norm": kc, "Xp_%": 100 / kc, "TI_s": ti}


def sintonia(kp_norm, tau, theta):
    """Los tres métodos con un mismo conjunto de parámetros."""
    return {m: regla(m, kp_norm, tau, theta) for m in REGLAS}


# ---------------------------------------------------------------- figuras

def fig_filtro(seg, t0, y0, yinf, t_fin, ruta):
    fig, ax = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax[0].plot(seg["t_rel"], seg["pO2"], color=C_DATOS, marker="o", ms=3, lw=0.8, label="cruda")
    ax[0].plot(seg["t_rel"], seg["pO2_filtrada"], color=C_PO2, label="Savitzky-Golay (5 pts, orden 2)")
    ax[0].hlines(y0, -60, 0, color=C_TXT2, lw=1.2)
    ax[0].hlines(yinf, t_fin - t0 - 120, t_fin - t0, color=C_TXT2, lw=1.2)
    ax[0].annotate(f"y₀ = {y0:.2f}", xy=(0, y0), xytext=(6, -2), textcoords="offset points",
                   va="top", fontsize=8, color=C_TXT2)
    ax[0].annotate(f"y∞ = {yinf:.2f}", xy=(t_fin - t0 - 120, yinf), xytext=(0, -6),
                   textcoords="offset points", ha="right", va="top", fontsize=8, color=C_TXT2)
    ax[0].set_ylabel("pO₂ [%sat]")
    ax[0].legend(frameon=False, loc="lower right")
    ax[1].step(seg["t_rel"], seg["STIR"], where="post", color=C_STIR)
    ax[1].set_ylabel("Agitación [rpm]")
    ax[1].set_xlabel("t − t₀ [s]")
    for a in ax:
        a.axvline(0, color=C_TXT2, lw=0.8, ls="--")
    fig.suptitle("Señal cruda vs. filtrada y estados estacionarios", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_ajuste(seg, t0, y0, yinf, du, sm, lsq, ruta):
    tt = seg["t_rel"].to_numpy()
    tf = np.linspace(tt.min(), tt.max(), 800)
    dy = yinf - y0
    y_sm = fopdt(tf, y0, dy / du, du, 0, sm["theta"], sm["tau"])
    y_lsq = fopdt(tf, y0, lsq["Kp"], du, 0, lsq["theta"], lsq["tau"])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(tt, seg["pO2"], "o", color=C_DATOS, ms=3.5, label="datos (cada ~5 s)")
    ax.plot(tf, y_sm, color=C_SMITH, label=f"Smith: θ = {sm['theta']:.1f} s, τ = {sm['tau']:.1f} s")
    ax.plot(tf, y_lsq, color=C_LSQ, ls="--",
            label=f"Mínimos cuadrados: θ = {lsq['theta']:.1f} s, τ = {lsq['tau']:.1f} s")
    for frac, tk in [(0.283, sm["t28"]), (0.632, sm["t63"])]:
        yk = y0 + frac * dy
        ax.plot([tk - t0] * 2, [y0 - 2, yk], color=C_TXT2, lw=0.8, ls=":")
        ax.plot([tt.min(), tk - t0], [yk] * 2, color=C_TXT2, lw=0.8, ls=":")
        ax.annotate(f"{frac * 100:.1f} %: t = {tk - t0:.1f} s", xy=(tk - t0, yk), xytext=(6, -4),
                    textcoords="offset points", va="top", fontsize=8, color=C_TXT2)
    ax.axvline(0, color=C_TXT2, lw=0.8, ls="--")
    ax.set_xlim(right=min(tt.max(), 450))
    ax.set_xlabel("t − t₀ [s]")
    ax.set_ylabel("pO₂ [%sat]")
    ax.legend(frameon=False, loc="lower right")
    fig.suptitle("Ajuste FOPDT sobre los datos experimentales", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


def fig_criterios(seg, t0, y0, yinf, tg, sk, sm, ruta, vertical=False):
    """Un panel por método: qué se lee de la curva para obtener θ y τ.

    vertical=True apila los paneles (para insertarla a ancho de página en un documento).
    """
    tt = seg["t_rel"].to_numpy()
    yy = seg["pO2"].to_numpy()
    dy = yinf - y0
    if vertical:
        fig, ax = plt.subplots(3, 1, figsize=(7.5, 8.6), sharex=True)
    else:
        fig, ax = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
    for a in ax:
        a.plot(tt, yy, "o", color=C_DATOS, ms=3)
        a.axhline(y0, color=C_TXT2, lw=0.8, ls=":")
        a.axhline(yinf, color=C_TXT2, lw=0.8, ls=":")
        a.axvline(0, color=C_TXT2, lw=0.8, ls="--")
        a.set_xlim(-40, 260)
        a.set_xlabel("t − t₀ [s]")
    for a in (ax if vertical else ax[:1]):
        a.set_ylabel("pO₂ [%sat]")
    if vertical:
        for a in ax[:-1]:
            a.set_xlabel("")

    # Ziegler-Nichols: tangente
    xa, xb = tg["ta"] - t0, tg["tb"] - t0
    ax[0].plot([xa, xb], [y0, yinf], color=C_TAN, lw=1.6)
    ax[0].plot(tg["t_pend"] - t0, tg["y_pend"], "o", color=C_TAN, ms=6)
    ax[0].annotate("", xy=(xa, y0 - 1.2), xytext=(0, y0 - 1.2), arrowprops=dict(arrowstyle="<->", color=C_TAN))
    ax[0].text(xa / 2, y0 - 2.1, f"θ = {tg['theta']:.0f} s", ha="center", va="top", fontsize=8, color=C_TXT2)
    ax[0].annotate("", xy=(xb, yinf + 0.8), xytext=(xa, yinf + 0.8), arrowprops=dict(arrowstyle="<->", color=C_TAN))
    ax[0].text((xa + xb) / 2, yinf + 1.2, f"τ = {tg['tau']:.0f} s", ha="center", fontsize=8, color=C_TXT2)
    ax[0].set_title("Equipo 1 · Ziegler-Nichols\nTangente en el punto de máxima pendiente", loc="left", fontsize=9)

    # SIMC: inicio visible + 63.2 %
    xm, x63 = sk["t_mov"] - t0, sk["t63"] - t0
    y63 = y0 + 0.632 * dy
    ax[1].plot([xm], [y0 + 0.5], "o", color=C_PO2, ms=6)
    ax[1].plot([x63], [y63], "o", color=C_PO2, ms=6)
    ax[1].plot([x63, x63], [y0 - 2, y63], color=C_PO2, lw=0.8, ls=":")
    ax[1].annotate("", xy=(xm, y0 - 1.2), xytext=(0, y0 - 1.2), arrowprops=dict(arrowstyle="<->", color=C_PO2))
    ax[1].text(xm / 2 + 2, y0 - 2.1, f"θ = {sk['theta']:.0f} s", ha="center", va="top", fontsize=8, color=C_TXT2)
    ax[1].annotate("", xy=(x63, y63 + 1.5), xytext=(xm, y63 + 1.5), arrowprops=dict(arrowstyle="<->", color=C_PO2))
    ax[1].text((xm + x63) / 2, y63 + 1.9, f"τ = {sk['tau']:.0f} s", ha="center", fontsize=8, color=C_TXT2)
    ax[1].text(x63 + 6, y63 - 0.5, "63.2 %", va="top", fontsize=8, color=C_TXT2)
    ax[1].set_title("Equipo 2 · SIMC\nInicio de la respuesta y 63.2 % del cambio", loc="left", fontsize=9)

    # ITAE: Smith dos puntos
    for frac, tk in [(0.283, sm["t28"]), (0.632, sm["t63"])]:
        yk = y0 + frac * dy
        ax[2].plot([tk - t0], [yk], "o", color=C_SMITH, ms=6)
        ax[2].plot([tk - t0] * 2, [y0 - 2, yk], color=C_SMITH, lw=0.8, ls=":")
        ax[2].text(tk - t0 + 6, yk - 0.5, f"{frac * 100:.1f} %: {tk - t0:.0f} s", va="top", fontsize=8, color=C_TXT2)
    ax[2].text(120, y0 + 3, f"τ = 1.5·(t₆₃ − t₂₈) = {sm['tau']:.0f} s\nθ = t₆₃ − τ = {sm['theta']:.0f} s",
               fontsize=8, color=C_TXT2)
    ax[2].set_title("Equipo 3 · ITAE\nDos puntos (Smith): 28.3 % y 63.2 %", loc="left", fontsize=9)

    fig.suptitle("Cómo lee la curva de reacción cada método", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(ruta)
    plt.close(fig)


# ---------------------------------------------------------------- flujo principal

def analizar(archivo, hoja, k, span=SPAN, ventana_y0=60, ventana_yinf=120):
    df = cargar(archivo, hoja)
    t0s = detectar_escalones(df)
    if not t0s:
        raise SystemExit("No se encontró un escalón 200→500 rpm")
    t0 = t0s[k - 1]
    t_fin = fin_escalon(df, t0)

    seg = df[(df["t"] >= t0 - ventana_y0) & (df["t"] < t_fin)].copy()
    seg["t_rel"] = seg["t"] - t0
    seg["pO2_filtrada"] = filtrar(seg["pO2"].to_numpy())

    y0 = seg.loc[seg["t_rel"] < 0, "pO2"].mean()
    yinf = seg.loc[seg["t"] >= t_fin - ventana_yinf, "pO2"].mean()
    dy, du = yinf - y0, U1 - U0
    du_pct = du / span * 100

    t = seg["t"].to_numpy()
    yf = seg["pO2_filtrada"].to_numpy()
    sm = smith(t, yf, t0, y0, yinf)
    tg = tangente(t, yf, t0, y0, yinf)
    sk = skogestad(t, yf, t0, y0, yinf)
    lsq = ajuste_lsq(t, seg["pO2"].to_numpy(), t0, y0, du, p0=[dy / du, sm["theta"], sm["tau"]])

    modelos = {
        "Smith": {"Kp": dy / du, "Kp_norm": dy / du_pct, "tau": sm["tau"], "theta": sm["theta"]},
        "Minimos cuadrados": {"Kp": lsq["Kp"], "Kp_norm": lsq["Kp"] * du / du_pct,
                              "tau": lsq["tau"], "theta": lsq["theta"]},
    }
    for m in modelos.values():
        m["sintonia"] = sintonia(m["Kp_norm"], m["tau"], m["theta"])

    # Cada equipo lee la curva con el criterio de su método
    kp_norm = dy / du_pct
    criterios = {"Ziegler-Nichols": ("tangente", tg), "SIMC": ("inicio + 63.2 %", sk),
                 "ITAE carga": ("dos puntos (Smith)", sm)}
    por_metodo = {m: {"criterio": c, "theta": p["theta"], "tau": p["tau"], "Kp_norm": kp_norm,
                      **regla(m, kp_norm, p["tau"], p["theta"])}
                  for m, (c, p) in criterios.items()}

    nombre = f"{hoja}_escalon{k}"
    for d in ["datos_limpios", "resultados", "figuras"]:
        (BASE / d).mkdir(exist_ok=True)
    seg[["t", "t_rel", "pO2", "pO2_filtrada", "STIR", "TEMP", "pH"]].round(3).to_csv(
        BASE / "datos_limpios" / f"{nombre}.csv", index=False)
    fig_filtro(seg, t0, y0, yinf, t_fin, BASE / "figuras" / f"10_{nombre}_filtro.png")
    fig_ajuste(seg, t0, y0, yinf, du, sm, lsq, BASE / "figuras" / f"11_{nombre}_ajuste.png")
    fig_criterios(seg, t0, y0, yinf, tg, sk, sm, BASE / "figuras" / f"12_{nombre}_criterios.png")
    fig_criterios(seg, t0, y0, yinf, tg, sk, sm, BASE / "figuras" / f"12_{nombre}_criterios_vertical.png",
                  vertical=True)

    resumen = {
        "archivo": str(archivo), "hoja": hoja, "escalon": k,
        "t0_s": t0, "t_fin_s": t_fin, "u0_rpm": U0, "u1_rpm": U1, "du_rpm": du,
        "span_rpm": span, "du_pct": du_pct,
        "y0": y0, "yinf": yinf, "dy": dy,
        "t28_rel_s": sm["t28"] - t0, "t63_rel_s": sm["t63"] - t0,
        "lsq_sd": lsq["sd"],
        "por_metodo": por_metodo,
        "modelos": modelos,
        "fijos_DCU": {"TD_s": 0, "Deadband_%": 1.5},
    }
    with open(BASE / "resultados" / f"{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False, default=float)
    return resumen


def imprimir(r):
    print(f"\n== {r['hoja']} · escalón {r['escalon']} (t0 = {r['t0_s']:.0f} s, Span = {r['span_rpm']:.0f} rpm)")
    print(f"y0 = {r['y0']:.2f} %  y∞ = {r['yinf']:.2f} %  Δy = {r['dy']:.2f} %  "
          f"t28 = {r['t28_rel_s']:.1f} s  t63 = {r['t63_rel_s']:.1f} s (desde t0)")
    for nm, m in r["modelos"].items():
        print(f"  {nm:18s} Kp = {m['Kp']:.4f} %/rpm  Kp,norm = {m['Kp_norm']:.3f}  "
              f"τ = {m['tau']:.1f} s  θ = {m['theta']:.1f} s  θ/τ = {m['theta'] / m['tau']:.3f}")
        for met, s in m["sintonia"].items():
            print(f"      {met:22s} Kc,norm = {s['Kc_norm']:6.2f}  Xp = {s['Xp_%']:6.2f} %  TI = {s['TI_s']:6.1f} s")
    print("  Cada método con su propio criterio de lectura:")
    for met, m in r["por_metodo"].items():
        print(f"      {met:16s} [{m['criterio']:18s}] θ = {m['theta']:5.1f} s  τ = {m['tau']:5.1f} s  "
              f"Xp = {m['Xp_%']:6.2f} %  TI = {m['TI_s']:6.1f} s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo")
    ap.add_argument("--hoja", default=0)
    ap.add_argument("--escalon", type=int, default=1, help="número de escalón 200→500 en la hoja")
    ap.add_argument("--span", type=float, default=SPAN, help="N_max − N_min de la cascada [rpm]")
    a = ap.parse_args()
    imprimir(analizar(a.archivo, a.hoja, a.escalon, a.span))
