"""Figuras reproducibles sobre invariancia y evolución de distribuciones."""

import csv
import hashlib
from pathlib import Path
import shutil
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tesis_generacion.estadistica.invariancia import (
    cdf_beta_medio,
    cdf_uniforme_01,
    fingerprint_ensemble,
    metricas_discrepancia_cdf,
)
from tesis_generacion.experimentos.invariancia import (
    ITERACIONES_INVARIANCIA,
    NUM_PARTICULAS_INVARIANCIA,
    SEED_INVARIANCIA,
    construir_experimentos_invariancia,
)
from tesis_generacion.visualizacion.estilo import (
    PERFIL_ANCHO,
    estilizar_eje,
    guardar_figura,
    leyenda_externa,
)


ARCHIVOS_TESIS_INVARIANCIA = (
    "LogConv_Iteraciones.png",
    "TentConv_Iteraciones.png",
)

ARCHIVOS_REFERENCIA_INVARIANCIA = (
    "logistico_evolucion_cdf.png",
    "tienda_ideal_evolucion_cdf.png",
    "discrepancia_cdf_iteraciones.png",
    "tienda_1999_vs_2_cdf.png",
    "resumen_invariancia.csv",
)


def _guardar_figura(figura: plt.Figure, ruta: Path) -> None:
    guardar_figura(figura, ruta, software="regenerar_invariancia.py")
    plt.close(figura)


def _sha256_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _graficar_cdf_empirica(eje, valores: np.ndarray, etiqueta: str) -> None:
    ordenados = np.sort(np.asarray(valores, dtype=float))
    x = np.concatenate(([0.0], ordenados, [1.0]))
    y = np.concatenate(([0.0], np.arange(1, len(ordenados) + 1) / len(ordenados), [1.0]))
    eje.step(x, y, where="post", linewidth=1.25, label=etiqueta)


def guardar_evolucion_cdf(
    ruta: Path,
    evolucion: List[np.ndarray],
    cdf_objetivo,
    titulo: str,
    etiqueta_objetivo: str,
) -> None:
    """Grafica las CDF empíricas de un único ensemble iterado."""

    figura, eje = plt.subplots(figsize=(7.6, 4.6), constrained_layout=True)
    for iteracion, valores in enumerate(evolucion):
        _graficar_cdf_empirica(eje, valores, f"n={iteracion}")
    malla = np.linspace(0.0, 1.0, 1001)
    eje.plot(
        malla,
        cdf_objetivo(malla),
        color="black",
        linestyle="--",
        linewidth=2.0,
        label=etiqueta_objetivo,
    )
    eje.set(
        title=titulo,
        xlabel="Valor",
        ylabel="Función de distribución acumulada",
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
    )
    eje.grid(alpha=0.25)
    estilizar_eje(eje, PERFIL_ANCHO)
    leyenda_externa(eje, PERFIL_ANCHO, ncol=3)
    _guardar_figura(figura, ruta)


def _metricas_evolucion(
    evolucion: List[np.ndarray], cdf_objetivo
) -> List[Dict[str, float]]:
    return [metricas_discrepancia_cdf(x, cdf_objetivo) for x in evolucion]


def guardar_discrepancias(
    ruta: Path,
    logistica: List[np.ndarray],
    tienda: List[np.ndarray],
) -> None:
    """Grafica las dos métricas CDF por iteración."""

    metricas_log = _metricas_evolucion(logistica, cdf_beta_medio)
    metricas_tent = _metricas_evolucion(tienda, cdf_uniforme_01)
    figura, ejes = plt.subplots(1, 2, figsize=(8.4, 3.6), constrained_layout=True)
    for eje, clave, titulo in (
        (ejes[0], "maxima_discrepancia_cdf", "Máxima discrepancia CDF"),
        (ejes[1], "mae_cdf", "MAE CDF"),
    ):
        eje.plot(
            ITERACIONES_INVARIANCIA,
            [fila[clave] for fila in metricas_log],
            marker="o",
            label="Logístico r=4",
        )
        eje.plot(
            ITERACIONES_INVARIANCIA,
            [fila[clave] for fila in metricas_tent],
            marker="s",
            label="Tienda ideal μ=2",
        )
        eje.set(title=titulo, xlabel="Iteración n", xticks=ITERACIONES_INVARIANCIA)
        eje.grid(alpha=0.25)
    ejes[0].set_ylabel("Discrepancia")
    for eje in ejes:
        estilizar_eje(eje, PERFIL_ANCHO)
    leyenda_externa(ejes[1], PERFIL_ANCHO, ncol=1)
    _guardar_figura(figura, ruta)


def guardar_diagnostico_tienda(
    ruta: Path,
    tienda_ideal: List[np.ndarray],
    tienda_1999: List[np.ndarray],
) -> None:
    """Compara el último pushforward para factores 2 y 1.999."""

    figura, eje = plt.subplots(figsize=(7.2, 4.3), constrained_layout=True)
    _graficar_cdf_empirica(eje, tienda_ideal[-1], "μ=2, n=4")
    _graficar_cdf_empirica(eje, tienda_1999[-1], "factor=1.999, n=4")
    malla = np.linspace(0.0, 1.0, 1001)
    eje.plot(
        malla,
        malla,
        color="black",
        linestyle="--",
        linewidth=2.0,
        label="Uniforme(0,1) teórica",
    )
    eje.set(
        title="Diagnóstico: tienda ideal frente a implementación histórica",
        xlabel="Valor",
        ylabel="Función de distribución acumulada",
        xlim=(0.0, 1.0),
        ylim=(0.0, 1.0),
    )
    eje.grid(alpha=0.25)
    estilizar_eje(eje, PERFIL_ANCHO)
    leyenda_externa(eje, PERFIL_ANCHO, ncol=3)
    _guardar_figura(figura, ruta)


def _escribir_csv(
    ruta: Path,
    experimentos: Dict[str, List[np.ndarray]],
) -> None:
    objetivos = {
        "logistico_r4": cdf_beta_medio,
        "tienda_ideal_2": cdf_uniforme_01,
        "tienda_diagnostico_1_999": cdf_uniforme_01,
    }
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            lineterminator="\n",
            fieldnames=(
                "experimento",
                "iteracion",
                "n",
                "maxima_discrepancia_cdf",
                "mae_cdf",
                "fingerprint_sha256",
            ),
        )
        escritor.writeheader()
        for nombre, evolucion in experimentos.items():
            for iteracion, valores in enumerate(evolucion):
                metricas = metricas_discrepancia_cdf(valores, objetivos[nombre])
                escritor.writerow(
                    {
                        "experimento": nombre,
                        "iteracion": iteracion,
                        "n": len(valores),
                        **metricas,
                        "fingerprint_sha256": fingerprint_ensemble(valores)["sha256"],
                    }
                )


def regenerar_invariancia(directorio: Path) -> Dict[str, object]:
    """Regenera figuras, CSV y resumen numérico del bloque 11."""

    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    experimentos = construir_experimentos_invariancia()
    logistica = experimentos["logistico_r4"]
    tienda = experimentos["tienda_ideal_2"]
    tienda_1999 = experimentos["tienda_diagnostico_1_999"]

    guardar_evolucion_cdf(
        directorio / "LogConv_Iteraciones.png",
        logistica,
        cdf_beta_medio,
        "Evolución de distribuciones: mapeo logístico",
        "Beta(1/2,1/2) teórica",
    )
    guardar_evolucion_cdf(
        directorio / "TentConv_Iteraciones.png",
        tienda,
        cdf_uniforme_01,
        "Evolución de distribuciones: mapeo tienda",
        "Uniforme(0,1) teórica",
    )
    shutil.copyfile(
        directorio / "LogConv_Iteraciones.png",
        directorio / "logistico_evolucion_cdf.png",
    )
    shutil.copyfile(
        directorio / "TentConv_Iteraciones.png",
        directorio / "tienda_ideal_evolucion_cdf.png",
    )
    guardar_discrepancias(
        directorio / "discrepancia_cdf_iteraciones.png", logistica, tienda
    )
    guardar_diagnostico_tienda(
        directorio / "tienda_1999_vs_2_cdf.png", tienda, tienda_1999
    )
    _escribir_csv(directorio / "resumen_invariancia.csv", experimentos)

    objetivos = {
        "logistico_r4": cdf_beta_medio,
        "tienda_ideal_2": cdf_uniforme_01,
        "tienda_diagnostico_1_999": cdf_uniforme_01,
    }
    resumen_experimentos = {}
    for nombre, evolucion in experimentos.items():
        resumen_experimentos[nombre] = {
            "n": len(evolucion[0]),
            "fingerprint_inicial": fingerprint_ensemble(evolucion[0]),
            "fingerprint_final": fingerprint_ensemble(evolucion[-1]),
            "metricas_por_iteracion": [
                metricas_discrepancia_cdf(x, objetivos[nombre])
                for x in evolucion
            ],
        }

    archivos = ARCHIVOS_TESIS_INVARIANCIA + ARCHIVOS_REFERENCIA_INVARIANCIA
    return {
        "parametros": {
            "seed": SEED_INVARIANCIA,
            "n": NUM_PARTICULAS_INVARIANCIA,
            "iteraciones": list(ITERACIONES_INVARIANCIA),
            "logistico": {
                "mapa": "f(x)=4x(1-x)",
                "inicial": "Triangular(0,0.5,1)",
                "objetivo": "Beta(1/2,1/2)",
            },
            "tienda_ideal": {
                "mapa": "T(x)=2x si x<=1/2; 2(1-x) si x>1/2",
                "inicial": "Beta(2,2)",
                "objetivo": "Uniforme(0,1)",
            },
            "tienda_diagnostico": {"factor": 1.999},
            "mae_cdf": "promedio en linspace(0,1,1001)",
        },
        "experimentos": resumen_experimentos,
        "figuras": {
            nombre: _sha256_archivo(directorio / nombre)
            for nombre in archivos
            if nombre.endswith(".png")
        },
        "archivos": list(archivos),
    }


def copiar_referencias_invariancia(origen: Path, destino: Path) -> None:
    """Copia solo referencias auxiliares cuando se solicita expresamente."""

    origen = Path(origen)
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS_REFERENCIA_INVARIANCIA:
        shutil.copyfile(origen / nombre, destino / nombre)
