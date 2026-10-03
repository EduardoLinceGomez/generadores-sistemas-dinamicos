"""Figuras reproducibles de FGM y función característica."""

import csv
import hashlib
from pathlib import Path
import shutil
from typing import Dict, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tesis_generacion.estadistica.transformadas import (
    fgm_empirica,
    fgm_uniforme,
    funcion_caracteristica_empirica,
    funcion_caracteristica_uniforme,
    metricas_error_transformada,
)
from tesis_generacion.experimentos import NUM_ITERACIONES, construir_muestras
from tesis_generacion.generadores import orbita_logistica
from tesis_generacion.visualizacion.estilo import (
    PERFIL_RESULTADOS,
    estilizar_eje,
    guardar_figura,
    leyenda_externa,
)


T_FGM = np.linspace(0.0, 15.0, 40)
T_FC = np.linspace(0.0, 20.0, 60)

ARCHIVOS_REFERENCIA_TRANSFORMADAS = (
    "logistico_crudo_vs_uniformizado_fgm.png",
    "logistico_crudo_vs_uniformizado_fc.png",
    "resumen_transformadas.csv",
)

ARCHIVOS_TESIS_TRANSFORMADAS = (
    "logistico_fgm.png",
    "logistico_error_fgm.png",
    "logistico_fc.png",
    "logistico_error_fc.png",
    "tienda_fgm.png",
    "tienda_error_fgm.png",
    "tienda_fc.png",
    "tienda_error_fc.png",
    "r30_fgm.png",
    "r30_error_fgm.png",
    "r30_fc.png",
    "r30_error_fc.png",
)

# Las dos gráficas de función característica que se muestran en pareja en la
# tesis comparten lienzo nominal. La trayectoria conserva ``aspect="equal"``;
# sólo se armoniza el espacio disponible para título, ejes y leyenda.
FIGSIZE_FC_PAREADA = (8.2, 7.0)

TITULOS_FC = {
    "logistico": (
        "Función característica:\nmapeo logístico uniformizado",
        "Error de la función característica:\nmapeo logístico uniformizado",
    ),
    "tienda": (
        "Función característica: mapeo tienda",
        "Error de la función característica: mapeo tienda",
    ),
    "r30": (
        "Función característica: regla 30",
        "Error de la función característica: regla 30",
    ),
}


def _guardar_figura(figura: plt.Figure, ruta: Path) -> None:
    guardar_figura(figura, ruta, software="regenerar_transformadas.py")
    plt.close(figura)


def _fingerprint(valores: np.ndarray) -> Dict[str, object]:
    muestra = np.ascontiguousarray(valores, dtype=np.dtype("<f8"))
    return {
        "n_elementos": int(muestra.size),
        "n_bytes": int(muestra.nbytes),
        "dtype": muestra.dtype.str,
        "endianness": "little",
        "sha256": hashlib.sha256(muestra.tobytes(order="C")).hexdigest(),
    }


def _sha256_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _resumen_transformadas(valores: np.ndarray) -> Dict[str, object]:
    fgm_observada = np.asarray(fgm_empirica(valores, T_FGM), dtype=float)
    fgm_teorica = np.asarray(fgm_uniforme(T_FGM), dtype=float)
    fc_observada = np.asarray(
        funcion_caracteristica_empirica(valores, T_FC), dtype=complex
    )
    fc_teorica = np.asarray(
        funcion_caracteristica_uniforme(T_FC), dtype=complex
    )
    return {
        "n": int(len(valores)),
        "fingerprint": _fingerprint(valores),
        "fgm": metricas_error_transformada(fgm_observada, fgm_teorica),
        "funcion_caracteristica": metricas_error_transformada(
            fc_observada, fc_teorica
        ),
    }


def guardar_fgm(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    titulo: str,
    *, perfil=PERFIL_RESULTADOS,
) -> None:
    """Compara la FGM empírica con la FGM de Uniforme(0,1)."""

    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    eje.plot(
        T_FGM,
        fgm_uniforme(T_FGM),
        color="black",
        linewidth=2.0,
        label="Uniforme(0,1) teórica",
    )
    for etiqueta, valores in series.items():
        eje.plot(
            T_FGM,
            fgm_empirica(valores, T_FGM),
            marker="o",
            markevery=4,
            markersize=3.5,
            linewidth=1.3,
            label=etiqueta,
        )
    eje.set(
        title=titulo.replace(": ", ":\n"),
        xlabel="t",
        ylabel="Función generadora de momentos $M(t)$",
        yscale="log",
    )
    eje.grid(alpha=0.25, which="both")
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def guardar_error_fgm(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    titulo: str,
    *, perfil=PERFIL_RESULTADOS,
) -> None:
    """Grafica |M_n(t)-M_U(t)| en la malla común."""

    teorica = np.asarray(fgm_uniforme(T_FGM), dtype=float)
    figura, eje = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    for etiqueta, valores in series.items():
        observada = np.asarray(fgm_empirica(valores, T_FGM), dtype=float)
        eje.plot(
            T_FGM,
            np.abs(observada - teorica),
            marker="o",
            markevery=4,
            markersize=3.5,
            linewidth=1.3,
            label=etiqueta,
        )
    eje.set(
        title=titulo.replace(": ", ":\n"),
        xlabel="t",
        ylabel=r"Error absoluto $|M_n(t)-M_U(t)|$",
        yscale="symlog",
    )
    eje.grid(alpha=0.25, which="both")
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def guardar_funcion_caracteristica(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    titulo: str,
    *,
    perfil=PERFIL_RESULTADOS,
    figsize: tuple[float, float] = (6.4, 5.2),
) -> None:
    """Grafica la trayectoria compleja de phi(t), 0 <= t <= 20."""

    teorica = np.asarray(funcion_caracteristica_uniforme(T_FC), dtype=complex)
    figura, eje = plt.subplots(figsize=figsize, constrained_layout=True)
    eje.plot(
        teorica.real,
        teorica.imag,
        color="black",
        linewidth=2.0,
        label="Uniforme(0,1) teórica",
    )
    for etiqueta, valores in series.items():
        observada = np.asarray(
            funcion_caracteristica_empirica(valores, T_FC), dtype=complex
        )
        eje.plot(
            observada.real,
            observada.imag,
            marker="o",
            markevery=6,
            markersize=3.5,
            linewidth=1.3,
            label=etiqueta,
        )
    eje.scatter([1.0], [0.0], color="tab:red", s=28, zorder=5, label=r"$t=0$")
    eje.set(
        title=titulo.replace(": ", ":\n"),
        xlabel=r"Parte real de $\varphi(t)$",
        ylabel=r"Parte imaginaria de $\varphi(t)$",
        aspect="equal",
    )
    eje.grid(alpha=0.25)
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def guardar_error_funcion_caracteristica(
    ruta: Path,
    series: Mapping[str, np.ndarray],
    titulo: str,
    *,
    perfil=PERFIL_RESULTADOS,
    figsize: tuple[float, float] = (7.2, 4.5),
) -> None:
    """Grafica |phi_n(t)-phi_U(t)| en la malla común."""

    teorica = np.asarray(funcion_caracteristica_uniforme(T_FC), dtype=complex)
    figura, eje = plt.subplots(figsize=figsize, constrained_layout=True)
    for etiqueta, valores in series.items():
        observada = np.asarray(
            funcion_caracteristica_empirica(valores, T_FC), dtype=complex
        )
        eje.plot(
            T_FC,
            np.abs(observada - teorica),
            marker="o",
            markevery=6,
            markersize=3.5,
            linewidth=1.3,
            label=etiqueta,
        )
    eje.set(
        title=titulo.replace(": ", ":\n"),
        xlabel="t",
        ylabel=r"Error absoluto $|\varphi_n(t)-\varphi_U(t)|$",
    )
    eje.set_ylim(bottom=0.0)
    eje.grid(alpha=0.25)
    estilizar_eje(eje, perfil)
    leyenda_externa(eje, perfil, ncol=1 if len(series) == 1 else 2)
    _guardar_figura(figura, ruta)


def guardar_resumen_csv(
    ruta: Path, resumenes: Mapping[str, Mapping[str, object]]
) -> None:
    """Guarda métricas sin redondear para ambas transformadas."""

    campos = (
        "muestra",
        "n",
        "fgm_t_min",
        "fgm_t_max",
        "fgm_num_puntos",
        "fgm_maxima_diferencia_absoluta",
        "fgm_mae",
        "fc_t_min",
        "fc_t_max",
        "fc_num_puntos",
        "fc_maxima_diferencia_absoluta",
        "fc_mae",
        "fingerprint_sha256",
    )
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos, lineterminator="\n")
        escritor.writeheader()
        for nombre, resumen in resumenes.items():
            escritor.writerow(
                {
                    "muestra": nombre,
                    "n": resumen["n"],
                    "fgm_t_min": T_FGM[0],
                    "fgm_t_max": T_FGM[-1],
                    "fgm_num_puntos": len(T_FGM),
                    "fgm_maxima_diferencia_absoluta": resumen["fgm"][
                        "maxima_diferencia_absoluta"
                    ],
                    "fgm_mae": resumen["fgm"]["mae"],
                    "fc_t_min": T_FC[0],
                    "fc_t_max": T_FC[-1],
                    "fc_num_puntos": len(T_FC),
                    "fc_maxima_diferencia_absoluta": resumen[
                        "funcion_caracteristica"
                    ]["maxima_diferencia_absoluta"],
                    "fc_mae": resumen["funcion_caracteristica"]["mae"],
                    "fingerprint_sha256": resumen["fingerprint"]["sha256"],
                }
            )


def regenerar_transformadas(output_dir: Path) -> Dict[str, object]:
    """Regenera figuras, métricas y diagnóstico del cálculo histórico."""

    output_dir.mkdir(parents=True, exist_ok=True)
    muestras = construir_muestras()
    cruda = np.asarray(
        orbita_logistica(4.0, 0.02024, NUM_ITERACIONES), dtype=float
    )

    configuraciones = (
        (
            "logistico",
            "mapeo logístico uniformizado",
            {"Logístico uniformizado": muestras["logistico"]},
        ),
        (
            "tienda",
            "mapeo tienda",
            {"Mapeo tienda": muestras["tienda"]},
        ),
        (
            "r30",
            "regla 30",
            {
                "R30 columnas": muestras["r30_columnas"],
                "R30 filas": muestras["r30_filas"],
            },
        ),
    )
    for nombre, titulo, series in configuraciones:
        titulo_fc, titulo_error_fc = TITULOS_FC[nombre]
        figsize_fc = (
            FIGSIZE_FC_PAREADA
            if nombre in {"logistico", "tienda"}
            else (6.4, 5.2)
        )
        figsize_error_fc = (
            FIGSIZE_FC_PAREADA
            if nombre in {"logistico", "tienda"}
            else (7.2, 4.5)
        )
        guardar_fgm(
            output_dir / f"{nombre}_fgm.png",
            series,
            f"FGM empírica: {titulo}",
        )
        guardar_error_fgm(
            output_dir / f"{nombre}_error_fgm.png",
            series,
            f"Error de la FGM: {titulo}",
        )
        guardar_funcion_caracteristica(
            output_dir / f"{nombre}_fc.png",
            series,
            titulo_fc,
            figsize=figsize_fc,
        )
        guardar_error_funcion_caracteristica(
            output_dir / f"{nombre}_error_fc.png",
            series,
            titulo_error_fc,
            figsize=figsize_error_fc,
        )

    diagnostico = {
        "Órbita cruda histórica": cruda,
        "Muestra uniformizada correcta": muestras["logistico"],
    }
    guardar_fgm(
        output_dir / "logistico_crudo_vs_uniformizado_fgm.png",
        diagnostico,
        "FGM logística: cálculo histórico y corrección",
    )
    guardar_funcion_caracteristica(
        output_dir / "logistico_crudo_vs_uniformizado_fc.png",
        diagnostico,
        "Función característica logística: cálculo histórico y corrección",
    )

    resumenes = {
        nombre: _resumen_transformadas(valores)
        for nombre, valores in muestras.items()
    }
    resumen_crudo = _resumen_transformadas(cruda)
    resumen_csv = dict(resumenes)
    resumen_csv["logistico_crudo_historico"] = resumen_crudo
    guardar_resumen_csv(output_dir / "resumen_transformadas.csv", resumen_csv)

    figuras = {
        ruta.name: {
            "ruta": str(ruta.resolve()),
            "sha256": _sha256_archivo(ruta),
        }
        for ruta in sorted(output_dir.glob("*.png"))
    }
    return {
        "convenciones": {
            "fgm_empirica": "(1/n) sum_j exp(t x_j)",
            "funcion_caracteristica_empirica": "(1/n) sum_j exp(i t x_j)",
            "error": "modulo de la diferencia compleja",
            "malla_fgm": "comun para todas las muestras",
            "malla_funcion_caracteristica": "comun para todas las muestras",
        },
        "mallas": {
            "fgm": T_FGM.tolist(),
            "funcion_caracteristica": T_FC.tolist(),
        },
        "muestras": resumenes,
        "logistico_historico_crudo": resumen_crudo,
        "figuras": figuras,
        "csv": str((output_dir / "resumen_transformadas.csv").resolve()),
    }


def copiar_referencias_transformadas(
    output_dir: Path, reference_dir: Path
) -> None:
    """Copia referencias diagnósticas solo mediante opción explícita."""

    if output_dir.resolve() == reference_dir.resolve():
        raise ValueError("output_dir y reference_dir deben ser distintos")
    reference_dir.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS_REFERENCIA_TRANSFORMADAS:
        origen = output_dir / nombre
        if not origen.is_file():
            raise FileNotFoundError(f"no se generó la referencia: {origen}")
        shutil.copyfile(origen, reference_dir / nombre)
