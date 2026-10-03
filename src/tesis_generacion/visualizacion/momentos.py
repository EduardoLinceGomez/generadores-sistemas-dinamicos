"""Figuras reproducibles para histogramas y momentos ordinarios."""

import csv
import hashlib
from pathlib import Path
import shutil
from typing import Dict, Mapping, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import cauchy, norm

from tesis_generacion.estadistica.momentos import (
    momentos_ordinarios,
    momentos_teoricos_uniforme,
    resumen_momentos,
    resumen_uniforme_teorica,
)
from tesis_generacion.experimentos import (
    NUM_ITERACIONES,
    construir_muestras,
)
from tesis_generacion.generadores import orbita_logistica
from tesis_generacion.visualizacion.estilo import (
    PERFIL_RESULTADOS,
    PERFIL_HISTOGRAMA_DOBLE,
    estilizar_eje,
    guardar_figura,
    leyenda_externa,
)


SEED_HISTOGRAMAS = 2024
N_HISTOGRAMAS = 10_000
VENTANA_HISTOGRAMAS = (-20.0, 20.0)
NUM_BINS_HISTOGRAMAS = 80
ORDEN_MAXIMO_LOGISTICO = 40
ORDEN_MAXIMO_OTROS = 20

ARCHIVOS_REFERENCIA = (
    "hist_normal_escala_comun.png",
    "hist_cauchy_escala_comun.png",
    "logistico_crudo_vs_uniformizado_hist.png",
    "logistico_crudo_vs_uniformizado_momentos.png",
    "resumen_momentos.csv",
)

ARCHIVOS_TESIS = (
    "logistico_momentos.png",
    "logistico_error_momentos.png",
    "tienda_momentos.png",
    "tienda_error_momentos.png",
    "r30_momentos.png",
    "r30_error_momentos.png",
)


def bordes_histogramas() -> np.ndarray:
    """Devuelve los 81 bordes comunes de -20 a 20."""

    return np.linspace(
        VENTANA_HISTOGRAMAS[0],
        VENTANA_HISTOGRAMAS[1],
        NUM_BINS_HISTOGRAMAS + 1,
    )


def generar_muestras_histogramas() -> Dict[str, np.ndarray]:
    """Genera Normal y luego Cauchy con un único RNG local."""

    rng = np.random.RandomState(SEED_HISTOGRAMAS)
    normal_estandar = rng.normal(0.0, 1.0, N_HISTOGRAMAS)
    cauchy_estandar = rng.standard_cauchy(N_HISTOGRAMAS)
    return {
        "normal": normal_estandar,
        "cauchy": cauchy_estandar,
    }


def calcular_histograma(
    valores: Sequence[float], bordes: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    """Normaliza conteos por n total y ancho, sin redistribuir la cola."""

    muestra = np.asarray(valores, dtype=float)
    bordes = np.asarray(bordes, dtype=float)
    if muestra.ndim != 1 or muestra.size == 0:
        raise ValueError("valores debe ser un arreglo unidimensional no vacío")
    if not np.all(np.isfinite(muestra)):
        raise ValueError("valores contiene NaN o infinito")
    if bordes.ndim != 1 or bordes.size < 2:
        raise ValueError("bordes debe contener al menos dos valores")
    if not np.all(np.isfinite(bordes)) or not np.all(np.diff(bordes) > 0):
        raise ValueError("bordes debe ser finito y estrictamente creciente")

    conteos, bordes_observados = np.histogram(muestra, bins=bordes)
    anchos = np.diff(bordes_observados)
    alturas = conteos / (muestra.size * anchos)
    fuera = int(np.count_nonzero((muestra < bordes[0]) | (muestra > bordes[-1])))
    resumen = {
        "n": int(muestra.size),
        "en_ventana": int(conteos.sum()),
        "fuera_ventana": fuera,
        "fraccion_fuera_ventana": fuera / muestra.size,
        "masa_visible": float(np.sum(alturas * anchos)),
    }
    return conteos, alturas, resumen


def _guardar_figura(figura: plt.Figure, ruta: Path) -> None:
    guardar_figura(figura, ruta, software="regenerar_momentos.py")
    plt.close(figura)


def guardar_histograma_distribucion(
    ruta: Path,
    valores: np.ndarray,
    bordes: np.ndarray,
    nombre: str,
) -> Dict[str, float]:
    """Guarda un histograma con la PDF teórica en la escala común."""

    _, alturas, resumen = calcular_histograma(valores, bordes)
    anchos = np.diff(bordes)
    x_pdf = np.linspace(*VENTANA_HISTOGRAMAS, 2001)
    if nombre == "normal":
        titulo = "Normal estándar"
        etiqueta_muestra = "Muestra Normal(0,1)"
        etiqueta_pdf = "Densidad Normal(0,1)"
        color = "skyblue"
        pdf = norm.pdf(x_pdf, loc=0.0, scale=1.0)
    elif nombre == "cauchy":
        titulo = "Cauchy estándar"
        etiqueta_muestra = "Muestra Cauchy(0,1)"
        etiqueta_pdf = "Densidad Cauchy(0,1)"
        color = "lightgreen"
        pdf = cauchy.pdf(x_pdf, loc=0.0, scale=1.0)
    else:
        raise ValueError(f"distribución desconocida: {nombre}")

    figura, eje = plt.subplots(figsize=(7.2, 5.6), layout="constrained")
    eje.bar(
        bordes[:-1],
        alturas,
        width=anchos,
        align="edge",
        alpha=0.65,
        color=color,
        edgecolor="black",
        linewidth=0.5,
        label=etiqueta_muestra,
    )
    eje.plot(x_pdf, pdf, color="tab:red", linewidth=2, label=etiqueta_pdf)
    eje.set(
        xlim=VENTANA_HISTOGRAMAS,
        ylim=(0.0, 0.42),
    )
    eje.set_title(titulo)
    eje.set_xlabel("Valor")
    eje.set_ylabel("Densidad empírica")
    eje.grid(alpha=0.25)
    estilizar_eje(eje, PERFIL_HISTOGRAMA_DOBLE)
    leyenda_externa(eje, PERFIL_HISTOGRAMA_DOBLE, ncol=1)
    _guardar_figura(figura, ruta)
    return resumen


def _alturas_en_intervalo_unidad(
    valores: np.ndarray, bordes: np.ndarray
) -> np.ndarray:
    _, alturas, resumen = calcular_histograma(valores, bordes)
    if resumen["fuera_ventana"] != 0:
        raise ValueError("la muestra logística contiene valores fuera de [0,1]")
    return alturas


def guardar_diagnostico_histograma_logistico(
    ruta: Path, cruda: np.ndarray, uniformizada: np.ndarray
) -> None:
    """Compara la órbita cruda y la muestra uniformizada en [0,1]."""

    bordes = np.linspace(0.0, 1.0, 41)
    alturas_cruda = _alturas_en_intervalo_unidad(cruda, bordes)
    alturas_uniformes = _alturas_en_intervalo_unidad(uniformizada, bordes)

    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    eje.stairs(
        alturas_cruda,
        bordes,
        linewidth=2,
        label=f"Órbita cruda (n = {len(cruda)})",
    )
    eje.stairs(
        alturas_uniformes,
        bordes,
        linewidth=2,
        label=f"Muestra uniformizada (n = {len(uniformizada)})",
    )
    eje.axhline(1.0, color="black", linestyle="--", label="Uniforme(0,1)")
    eje.set(
        title="Diagnóstico de la muestra logística",
        xlabel="Valor",
        ylabel="Densidad empírica",
        xlim=(0.0, 1.0),
    )
    eje.set_ylim(bottom=0.0)
    eje.grid(alpha=0.25)
    estilizar_eje(eje)
    leyenda_externa(eje, ncol=2)
    _guardar_figura(figura, ruta)


def guardar_comparacion_momentos(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    orden_maximo: int,
    titulo: str,
    *, perfil=PERFIL_RESULTADOS,
) -> None:
    """Guarda momentos ordinarios empíricos y teóricos en un mismo eje."""

    ordenes = np.arange(1, orden_maximo + 1)
    teoricos = momentos_teoricos_uniforme(orden_maximo)
    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    eje.scatter(
        ordenes,
        teoricos,
        s=52,
        facecolors="none",
        edgecolors="black",
        label="Uniforme(0,1) teórica",
    )
    for etiqueta, valores in series.items():
        eje.plot(
            ordenes,
            momentos_ordinarios(valores, orden_maximo),
            marker="x",
            linewidth=1.2,
            markersize=5,
            label=etiqueta,
        )
    eje.set(title=titulo.replace(": ", ":\n"), xlabel=r"Orden $k$", ylabel=r"Momento ordinario $m_k$")
    eje.grid(alpha=0.25)
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def guardar_error_momentos(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    orden_maximo: int,
    titulo: str,
    *, perfil=PERFIL_RESULTADOS,
) -> None:
    """Guarda errores absolutos respecto de Uniforme(0,1)."""

    ordenes = np.arange(1, orden_maximo + 1)
    teoricos = np.asarray(momentos_teoricos_uniforme(orden_maximo))
    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    for etiqueta, valores in series.items():
        observados = np.asarray(momentos_ordinarios(valores, orden_maximo))
        eje.plot(
            ordenes,
            np.abs(observados - teoricos),
            marker="x",
            linewidth=1.2,
            markersize=5,
            label=etiqueta,
        )
    eje.set(
        title=titulo.replace(": ", ":\n"),
        xlabel=r"Orden $k$",
        ylabel="Error absoluto del momento",
    )
    eje.set_ylim(bottom=0.0)
    eje.grid(alpha=0.25)
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def _fingerprint(valores: np.ndarray) -> Dict[str, object]:
    muestra = np.ascontiguousarray(valores, dtype=np.dtype("<f8"))
    return {
        "n_elementos": int(muestra.size),
        "n_bytes": int(muestra.nbytes),
        "dtype": muestra.dtype.str,
        "endianness": "little",
        "sha256": hashlib.sha256(muestra.tobytes(order="C")).hexdigest(),
    }


def _resumen_con_fingerprint(valores: np.ndarray) -> Dict[str, object]:
    resumen = resumen_momentos(valores, 4)
    resumen["fingerprint"] = _fingerprint(valores)
    return resumen


def guardar_resumen_csv(
    ruta: Path, resumenes: Mapping[str, Mapping[str, object]]
) -> None:
    """Guarda las estadísticas principales sin redondear."""

    campos = (
        "muestra",
        "n",
        "media",
        "varianza",
        "asimetria_fisher_pearson",
        "curtosis_pearson",
        "exceso_curtosis",
        "m1",
        "m2",
        "m3",
        "m4",
    )
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos,
            lineterminator="\n",
        )
        escritor.writeheader()
        for nombre, resumen in resumenes.items():
            momentos = resumen["momentos_ordinarios"]
            escritor.writerow(
                {
                    "muestra": nombre,
                    "n": "" if resumen["n"] is None else resumen["n"],
                    "media": resumen["media"],
                    "varianza": resumen["varianza"],
                    "asimetria_fisher_pearson": resumen[
                        "asimetria_fisher_pearson"
                    ],
                    "curtosis_pearson": resumen["curtosis_pearson"],
                    "exceso_curtosis": resumen["exceso_curtosis"],
                    "m1": momentos[0],
                    "m2": momentos[1],
                    "m3": momentos[2],
                    "m4": momentos[3],
                }
            )


def _sha256_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def regenerar_momentos(output_dir: Path) -> Dict[str, object]:
    """Regenera figuras y estadísticas del bloque 09."""

    output_dir.mkdir(parents=True, exist_ok=True)
    muestras = construir_muestras()
    cruda = np.asarray(
        orbita_logistica(4.0, 0.02024, NUM_ITERACIONES), dtype=float
    )

    histogramas = generar_muestras_histogramas()
    bordes = bordes_histogramas()
    resumen_histogramas = {}
    for nombre, archivo in (
        ("normal", "hist_normal_escala_comun.png"),
        ("cauchy", "hist_cauchy_escala_comun.png"),
    ):
        resumen_histogramas[nombre] = guardar_histograma_distribucion(
            output_dir / archivo,
            histogramas[nombre],
            bordes,
            nombre,
        )
        resumen_histogramas[nombre]["fingerprint"] = _fingerprint(
            histogramas[nombre]
        )

    guardar_diagnostico_histograma_logistico(
        output_dir / "logistico_crudo_vs_uniformizado_hist.png",
        cruda,
        muestras["logistico"],
    )
    guardar_comparacion_momentos(
        output_dir / "logistico_crudo_vs_uniformizado_momentos.png",
        {
            "Órbita cruda histórica": cruda,
            "Muestra uniformizada correcta": muestras["logistico"],
        },
        ORDEN_MAXIMO_LOGISTICO,
        "Momentos logísticos: cálculo histórico y corrección",
    )

    configuraciones = (
        (
            "logistico",
            "mapeo logístico",
            {"Logístico uniformizado": muestras["logistico"]},
            ORDEN_MAXIMO_LOGISTICO,
        ),
        (
            "tienda",
            "mapeo tienda",
            {"Mapeo tienda": muestras["tienda"]},
            ORDEN_MAXIMO_OTROS,
        ),
        (
            "r30",
            "regla 30",
            {
                "R30 columnas": muestras["r30_columnas"],
                "R30 filas": muestras["r30_filas"],
            },
            ORDEN_MAXIMO_OTROS,
        ),
    )
    for nombre, titulo, series, orden_maximo in configuraciones:
        guardar_comparacion_momentos(
            output_dir / f"{nombre}_momentos.png",
            series,
            orden_maximo,
            f"Momentos ordinarios: {titulo}",
        )
        guardar_error_momentos(
            output_dir / f"{nombre}_error_momentos.png",
            series,
            orden_maximo,
            f"Error de momentos: {titulo}",
        )

    resumenes = {"uniforme_teorica": resumen_uniforme_teorica(4)}
    for nombre, valores in muestras.items():
        resumenes[nombre] = _resumen_con_fingerprint(valores)
    guardar_resumen_csv(output_dir / "resumen_momentos.csv", resumenes)

    figuras = {}
    for ruta in sorted(output_dir.glob("*.png")):
        figuras[ruta.name] = {
            "ruta": str(ruta.resolve()),
            "sha256": _sha256_archivo(ruta),
        }

    return {
        "parametros": {
            "seed_histogramas": SEED_HISTOGRAMAS,
            "orden_rng": ["normal", "cauchy"],
            "n_normal": N_HISTOGRAMAS,
            "n_cauchy": N_HISTOGRAMAS,
            "ventana": list(VENTANA_HISTOGRAMAS),
            "numero_bins": NUM_BINS_HISTOGRAMAS,
            "numero_bordes": int(bordes.size),
            "ancho_bin": float(bordes[1] - bordes[0]),
            "orden_maximo_logistico": ORDEN_MAXIMO_LOGISTICO,
            "orden_maximo_tienda_r30": ORDEN_MAXIMO_OTROS,
        },
        "histogramas": resumen_histogramas,
        "uniforme_teorica": resumenes["uniforme_teorica"],
        "muestras": {
            nombre: resumenes[nombre]
            for nombre in ("logistico", "tienda", "r30_columnas", "r30_filas")
        },
        "logistico_historico_crudo": _resumen_con_fingerprint(cruda),
        "figuras": figuras,
        "csv": str((output_dir / "resumen_momentos.csv").resolve()),
    }


def copiar_referencias(output_dir: Path, reference_dir: Path) -> None:
    """Copia solo referencias aprobables mediante una opción explícita."""

    if output_dir.resolve() == reference_dir.resolve():
        raise ValueError("output_dir y reference_dir deben ser distintos")
    reference_dir.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS_REFERENCIA:
        origen = output_dir / nombre
        if not origen.is_file():
            raise FileNotFoundError(f"no se generó la referencia: {origen}")
        shutil.copyfile(origen, reference_dir / nombre)
