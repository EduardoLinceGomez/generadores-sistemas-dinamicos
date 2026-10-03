"""Construcción reproducible de las figuras del coleccionista."""

from collections import Counter
from pathlib import Path
from typing import Dict, Optional, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tesis_generacion.estadistica.coleccionista import (
    cdf_coleccionista,
    metricas_coleccionista,
    pmf_coleccionista,
)
from tesis_generacion.experimentos import (
    NUM_VALORES,
    calcular_maximo_soporte_coleccionista_comun,
    construir_muestras,
)
from tesis_generacion.visualizacion.estilo import (
    PERFIL_RESULTADOS,
    estilizar_eje,
    guardar_figura,
    leyenda_externa,
)


NOMBRES_FIGURAS = {
    "logistico": ("log_dist_CCT.png", "Log_dens_CCT.png"),
    "tienda": ("Tent_dsit_CCT.png", "Tent_dens_CCT.png"),
    "r30_columnas": ("R30_col_distCCT.png", "R30_col_densCCT.png"),
    "r30_filas": ("R30_fila_distCCT.png", "R30_fila_densCCT.png"),
}

ETIQUETAS = {
    "logistico": "Mapeo logístico transformado",
    "tienda": "Mapeo tienda",
    "r30_columnas": "Regla 30 por columnas",
    "r30_filas": "Regla 30 por filas",
}


def validar_muestra(nombre: str, valores: np.ndarray) -> None:
    if len(valores) != NUM_VALORES:
        raise ValueError(f"{nombre}: se esperaban {NUM_VALORES} valores")
    if not np.all(np.isfinite(valores)):
        raise ValueError(f"{nombre}: contiene NaN o infinito")
    if not np.all((0.0 <= valores) & (valores < 1.0)):
        raise ValueError(f"{nombre}: contiene valores fuera de [0,1)")


def rango_grafica(longitudes: Sequence[int]) -> np.ndarray:
    limite = max(longitudes)
    while cdf_coleccionista(limite) < 0.9999:
        limite += 1
    return np.arange(10, limite + 1, dtype=int)


def guardar_cdf(
    ruta: Path, etiqueta: str, longitudes: Sequence[int], valores_m: np.ndarray
) -> None:
    ordenadas = np.sort(np.asarray(longitudes, dtype=int))
    cdf_empirica = np.searchsorted(
        ordenadas, valores_m, side="right"
    ) / len(ordenadas)
    cdf_teorica = np.asarray(
        [cdf_coleccionista(int(m)) for m in valores_m]
    )

    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    eje.step(
        valores_m,
        cdf_empirica,
        where="post",
        linewidth=2,
        label="CDF empírica",
    )
    eje.step(
        valores_m,
        cdf_teorica,
        where="post",
        linewidth=2,
        label="CDF teórica",
    )
    eje.set(
        title=etiqueta,
        xlabel="Longitud del bloque",
        ylabel="Función de distribución acumulada",
        ylim=(-0.02, 1.02),
    )
    eje.grid(alpha=0.25)
    estilizar_eje(eje, PERFIL_RESULTADOS)
    leyenda_externa(eje, PERFIL_RESULTADOS, ncol=2)
    guardar_figura(figura, ruta, software="regenerar_coleccionista.py")
    plt.close(figura)


def guardar_pmf(
    ruta: Path, etiqueta: str, longitudes: Sequence[int], valores_m: np.ndarray
) -> None:
    frecuencias = Counter(longitudes)
    pmf_empirica = np.asarray(
        [frecuencias.get(int(m), 0) / len(longitudes) for m in valores_m]
    )
    pmf_teorica = np.asarray(
        [pmf_coleccionista(int(m)) for m in valores_m]
    )

    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    eje.bar(
        valores_m,
        pmf_empirica,
        width=0.8,
        alpha=0.65,
        label="PMF empírica",
    )
    eje.plot(
        valores_m,
        pmf_teorica,
        color="tab:red",
        marker=".",
        markersize=3,
        linewidth=1.5,
        label="PMF teórica",
    )
    eje.set(
        title=etiqueta,
        xlabel="Longitud del bloque",
        ylabel="Función de masa de probabilidad",
    )
    eje.set_ylim(bottom=0)
    eje.grid(axis="y", alpha=0.25)
    estilizar_eje(eje, PERFIL_RESULTADOS)
    leyenda_externa(eje, PERFIL_RESULTADOS, ncol=2)
    guardar_figura(figura, ruta, software="regenerar_coleccionista.py")
    plt.close(figura)


def regenerar_muestra(
    nombre: str,
    valores: np.ndarray,
    output_dir: Path,
    maximo_soporte: Optional[int] = None,
) -> Dict[str, float]:
    """Valida una muestra y regenera su par de figuras CDF/PMF."""

    if nombre not in NOMBRES_FIGURAS:
        raise ValueError(f"muestra desconocida: {nombre}")
    output_dir.mkdir(parents=True, exist_ok=True)
    valores = np.asarray(valores, dtype=float)
    validar_muestra(nombre, valores)
    longitudes, metricas = metricas_coleccionista(
        valores, maximo_soporte=maximo_soporte
    )
    valores_m = rango_grafica(longitudes)
    archivo_cdf, archivo_pmf = NOMBRES_FIGURAS[nombre]
    guardar_cdf(
        output_dir / archivo_cdf, ETIQUETAS[nombre], longitudes, valores_m
    )
    guardar_pmf(
        output_dir / archivo_pmf, ETIQUETAS[nombre], longitudes, valores_m
    )
    return metricas


def regenerar(output_dir: Path) -> Dict[str, Dict[str, float]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    muestras = construir_muestras()
    maximo_soporte = calcular_maximo_soporte_coleccionista_comun(muestras)
    resumen = {}

    for nombre, valores in muestras.items():
        resumen[nombre] = regenerar_muestra(
            nombre,
            valores,
            output_dir,
            maximo_soporte=maximo_soporte,
        )

    return resumen
