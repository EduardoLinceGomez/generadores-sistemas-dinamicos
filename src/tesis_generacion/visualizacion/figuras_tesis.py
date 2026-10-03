"""Figuras canónicas y esquemas reproducibles usados por la tesis."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Iterable, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np

from tesis_generacion.experimentos.muestras import (
    muestra_logistica,
    muestra_tienda,
    muestras_regla_30,
)
from tesis_generacion.experimentos.parametros import (
    NUM_CELDAS,
    NUM_ITERACIONES,
    SEED,
)
from tesis_generacion.generadores.regla30 import (
    evolucion_regla30,
    paso_regla30,
)
from tesis_generacion.visualizacion.estilo import (
    guardar_figura,
    estilizar_eje,
    leyenda_externa,
)


DPI = 220
COLOR_OSCURO = "#1f2933"
COLOR_MEDIO = "#52616b"
COLOR_CLARO = "#d9e2ec"
COLOR_ACENTO = "#9b4d00"
COLOR_SECUNDARIO = "#1f5a94"

CELDAS_R30_PEDAGOGICO = 101
INSTANTES_R30_PEDAGOGICO = 50
CELDAS_R184 = 101
INSTANTES_R184 = 55
DENSIDADES_R184 = (0.25, 0.50, 0.70)

ARCHIVOS_GENERADOS = (
    "conceptuales/sistema_dinamico.pdf",
    "conceptuales/punto_fijo_repulsor.pdf",
    "conceptuales/punto_fijo_atractor.pdf",
    "conceptuales/orbita_periodo_cuatro.pdf",
    "conceptuales/malla_automata.pdf",
    "conceptuales/regla184_trafico.pdf",
    "conceptuales/regla184_local.png",
    "conceptuales/regla184_densidad_25.png",
    "conceptuales/regla184_densidad_50.png",
    "conceptuales/regla184_densidad_70.png",
    "conceptuales/regla30_local.pdf",
    "conceptuales/regla30_espaciotemporal.png",
    "conceptuales/coleccionista_bloques.png",
    "conceptuales/prueba_brechas.png",
    "conceptuales/logistico_preimagenes.pdf",
    "conceptuales/tienda_mapeo.pdf",
    "conceptuales/tienda_preimagenes.pdf",
    "cientificas/logistico_bifurcacion.png",
    "cientificas/tienda_bifurcacion.png",
    "cientificas/logistico_histograma.png",
    "cientificas/tienda_histograma.png",
    "cientificas/r30_matriz_1000.png",
    "cientificas/r30_hist_columnas.png",
    "cientificas/r30_hist_filas.png",
    "decorativas/capitulo_introduccion.png",
    "decorativas/capitulo_marco_teorico.png",
    "decorativas/capitulo_resultados.png",
    "decorativas/capitulo_conclusiones.png",
)

# Estas salidas continúan disponibles como alternativas reproducibles, pero no
# deben sobrescribir las versiones históricas propias elegidas para la tesis.
# PCC y PG se regeneran por separado desde sus fuentes TikZ versionadas.
ARCHIVOS_CANONICOS_ACTIVOS = tuple(
    nombre
    for nombre in ARCHIVOS_GENERADOS
    if nombre
    not in {
        "conceptuales/sistema_dinamico.pdf",
        "conceptuales/punto_fijo_repulsor.pdf",
        "conceptuales/punto_fijo_atractor.pdf",
        "conceptuales/orbita_periodo_cuatro.pdf",
        "conceptuales/regla184_trafico.pdf",
        "conceptuales/coleccionista_bloques.png",
        "conceptuales/prueba_brechas.png",
        "conceptuales/tienda_mapeo.pdf",
        "conceptuales/tienda_preimagenes.pdf",
        "cientificas/logistico_bifurcacion.png",
        "cientificas/tienda_bifurcacion.png",
        "decorativas/capitulo_introduccion.png",
        "decorativas/capitulo_marco_teorico.png",
        "decorativas/capitulo_resultados.png",
        "decorativas/capitulo_conclusiones.png",
    }
)


def _guardar(figura: plt.Figure, ruta: Path, *, transparente: bool = False) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"Creator": "tesis-generacion"}
    if ruta.suffix.lower() == ".pdf":
        metadata.update({"CreationDate": None, "ModDate": None})
    figura.savefig(
        ruta,
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0.05,
        metadata=metadata,
        transparent=transparente,
    )
    plt.close(figura)


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def tabla_regla30() -> Tuple[Tuple[Tuple[int, int, int], int], ...]:
    """Devuelve la tabla local usando la implementación validada de Rule 30."""

    filas = []
    for codigo in range(7, -1, -1):
        vecindad = tuple((codigo >> desplazamiento) & 1 for desplazamiento in (2, 1, 0))
        salida = int(paso_regla30(np.asarray(vecindad, dtype=np.uint8))[1])
        filas.append((vecindad, salida))
    return tuple(filas)


def salida_regla_elemental(numero: int, vecindad: Sequence[int]) -> int:
    """Evalúa una regla elemental numerada con el convenio de Wolfram."""

    if not 0 <= numero <= 255:
        raise ValueError("numero debe pertenecer a [0,255]")
    if len(vecindad) != 3 or any(bit not in (0, 1) for bit in vecindad):
        raise ValueError("vecindad debe contener exactamente tres bits")
    indice = 4 * int(vecindad[0]) + 2 * int(vecindad[1]) + int(vecindad[2])
    return (numero >> indice) & 1


def tabla_regla_elemental(numero: int) -> Tuple[Tuple[Tuple[int, int, int], int], ...]:
    return tuple(
        (
            tuple((codigo >> desplazamiento) & 1 for desplazamiento in (2, 1, 0)),
            salida_regla_elemental(
                numero,
                tuple((codigo >> desplazamiento) & 1 for desplazamiento in (2, 1, 0)),
            ),
        )
        for codigo in range(7, -1, -1)
    )


def evolucion_regla_elemental(
    numero: int, condicion_inicial: np.ndarray, numero_instantes: int
) -> np.ndarray:
    """Evoluciona una regla elemental con frontera espacial periódica."""

    inicial = np.asarray(condicion_inicial, dtype=np.uint8)
    if inicial.ndim != 1 or inicial.size == 0:
        raise ValueError("condicion_inicial debe ser un vector no vacío")
    if not np.all((inicial == 0) | (inicial == 1)):
        raise ValueError("condicion_inicial debe contener únicamente bits")
    if numero_instantes < 1:
        raise ValueError("numero_instantes debe ser positivo")
    matriz = np.empty((numero_instantes, inicial.size), dtype=np.uint8)
    matriz[0] = inicial
    for instante in range(1, numero_instantes):
        anterior = matriz[instante - 1]
        izquierda = np.roll(anterior, 1)
        derecha = np.roll(anterior, -1)
        codigos = 4 * izquierda + 2 * anterior + derecha
        matriz[instante] = (numero >> codigos) & 1
    return matriz


def condicion_inicial_densidad(
    numero_celdas: int, densidad: float, semilla: int
) -> np.ndarray:
    """Construye una fila con un número controlado de celdas activas."""

    if numero_celdas < 1 or not 0.0 <= densidad <= 1.0:
        raise ValueError("parámetros de densidad inválidos")
    activos = int(round(numero_celdas * densidad))
    fila = np.zeros(numero_celdas, dtype=np.uint8)
    rng = np.random.RandomState(semilla)
    fila[rng.permutation(numero_celdas)[:activos]] = 1
    return fila


def matriz_regla30_pedagogica() -> np.ndarray:
    inicial = np.zeros(CELDAS_R30_PEDAGOGICO, dtype=np.uint8)
    inicial[CELDAS_R30_PEDAGOGICO // 2] = 1
    return evolucion_regla30(inicial, INSTANTES_R30_PEDAGOGICO)


def _figura_sistema_dinamico(ruta: Path) -> None:
    figura, eje = plt.subplots(figsize=(10.0, 2.2))
    eje.set_axis_off()
    posiciones = (0.7, 2.6, 4.5, 6.3, 8.5)
    etiquetas = (
        r"$x_0$",
        r"$x_1=f(x_0)$",
        r"$x_2=f(x_1)$",
        r"$\cdots$",
        r"$x_n=f^n(x_0)$",
    )
    for posicion, etiqueta in zip(posiciones, etiquetas):
        if etiqueta == r"$\cdots$":
            eje.text(posicion, 0.5, etiqueta, ha="center", va="center", fontsize=18)
            continue
        caja = patches.FancyBboxPatch(
            (posicion - 0.62, 0.31),
            1.24,
            0.38,
            boxstyle="round,pad=0.04",
            facecolor="white",
            edgecolor=COLOR_OSCURO,
            linewidth=1.4,
        )
        eje.add_patch(caja)
        eje.text(posicion, 0.5, etiqueta, ha="center", va="center", fontsize=13)
    for izquierda, derecha in zip(posiciones[:-1], posiciones[1:]):
        eje.annotate(
            "",
            xy=(derecha - 0.72, 0.5),
            xytext=(izquierda + 0.72, 0.5),
            arrowprops={"arrowstyle": "->", "color": COLOR_OSCURO, "lw": 1.5},
        )
    eje.text(4.5, 0.08, r"iteraciones sucesivas de $f$", ha="center", fontsize=11)
    eje.set_xlim(0, 9.2)
    eje.set_ylim(0, 1)
    _guardar(figura, ruta)


def _figura_punto_fijo(ruta: Path, *, atractor: bool) -> None:
    figura, eje = plt.subplots(figsize=(4.6, 4.3))
    eje.set_aspect("equal")
    eje.set_xlim(-1.25, 1.25)
    eje.set_ylim(-1.25, 1.25)
    eje.axis("off")
    eje.add_patch(
        patches.Circle((0, 0), 0.83, fill=False, ls="--", lw=1.1, ec=COLOR_MEDIO)
    )
    eje.scatter([0], [0], s=45, color=COLOR_OSCURO, zorder=4)
    eje.text(0.07, -0.05, r"$x^*$", fontsize=13)
    eje.text(0.48, 0.70, r"$B_\delta(x^*)$", fontsize=11)
    angulos = (0.25, 2.1, 4.2)
    for indice, inicio in enumerate(angulos):
        parametro = np.linspace(0.0, 1.0, 140)
        if atractor:
            radio = 0.76 * (1.0 - 0.83 * parametro)
            theta = inicio + 2.1 * parametro
        else:
            radio = 0.12 + 0.92 * parametro
            theta = inicio + 1.7 * parametro
        x = radio * np.cos(theta)
        y = radio * np.sin(theta)
        eje.plot(x, y, color=(COLOR_SECUNDARIO if indice % 2 else COLOR_ACENTO), lw=1.6)
        paso = 84
        eje.annotate(
            "",
            xy=(x[paso + 4], y[paso + 4]),
            xytext=(x[paso], y[paso]),
            arrowprops={"arrowstyle": "->", "lw": 1.3, "color": COLOR_OSCURO},
        )
    _guardar(figura, ruta)


def _figura_periodo_cuatro(ruta: Path) -> None:
    figura, eje = plt.subplots(figsize=(4.8, 4.4))
    eje.set_aspect("equal")
    eje.axis("off")
    angulos = np.asarray([0.25, 1.95, 3.35, 5.0])
    puntos = np.column_stack((np.cos(angulos), np.sin(angulos)))
    etiquetas = (r"$x$", r"$f(x)$", r"$f^2(x)$", r"$f^3(x)$")
    for indice, (punto, etiqueta) in enumerate(zip(puntos, etiquetas)):
        eje.scatter(*punto, s=46, color=COLOR_OSCURO, zorder=4)
        eje.text(
            punto[0] + (0.08 if punto[0] >= 0 else -0.35),
            punto[1] + (0.08 if punto[1] >= 0 else -0.18),
            etiqueta,
            fontsize=12,
        )
        siguiente = puntos[(indice + 1) % 4]
        eje.annotate(
            "",
            xy=siguiente,
            xytext=punto,
            arrowprops={
                "arrowstyle": "->",
                "connectionstyle": "arc3,rad=0.16",
                "lw": 1.5,
                "color": COLOR_SECUNDARIO,
            },
        )
    eje.text(0.12, 1.17, r"$f^4(x)=x$", fontsize=13)
    eje.set_xlim(-1.35, 1.35)
    eje.set_ylim(-1.3, 1.35)
    _guardar(figura, ruta)


def _figura_malla(ruta: Path) -> None:
    matriz = evolucion_regla30(
        np.asarray([0, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8), 7
    )
    figura, eje = plt.subplots(figsize=(7.3, 4.3))
    eje.imshow(matriz, cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
    filas, columnas = matriz.shape
    for x in np.arange(0.5, columnas - 0.5, 1):
        eje.vlines(x, ymin=-0.5, ymax=filas - 0.5, color="#7b8794", linewidth=0.55)
    for y in np.arange(0.5, filas - 0.5, 1):
        eje.hlines(y, xmin=-0.5, xmax=columnas - 0.5, color="#7b8794", linewidth=0.55)
    for borde in eje.spines.values():
        borde.set_visible(False)
    eje.tick_params(which="both", left=False, bottom=False, labelleft=False, labelbottom=False)
    eje.add_patch(
        patches.Rectangle(
            (-0.5, 3.5), matriz.shape[1], 1, fill=False, lw=2.2, ec=COLOR_ACENTO
        )
    )
    eje.add_patch(
        patches.Rectangle(
            (5.5, -0.5), 1, matriz.shape[0], fill=False, lw=2.2, ec=COLOR_SECUNDARIO
        )
    )
    eje.annotate(
        "fila: configuración espacial en un instante",
        xy=(8.6, 4.0),
        xytext=(10.1, 5.4),
        arrowprops={"arrowstyle": "->", "color": COLOR_ACENTO},
        color=COLOR_ACENTO,
        fontsize=10,
        va="center",
    )
    eje.annotate(
        "columna: historia temporal de una celda",
        xy=(6.0, 0.0),
        xytext=(10.1, 1.0),
        arrowprops={"arrowstyle": "->", "color": COLOR_SECUNDARIO},
        color=COLOR_SECUNDARIO,
        fontsize=10,
        va="center",
    )
    eje.text(-1.35, 3.0, "tiempo", rotation=90, va="center", fontsize=10)
    eje.annotate("", xy=(-0.9, 6.4), xytext=(-0.9, -0.3), arrowprops={"arrowstyle": "->"})
    eje.text(4.0, -1.1, "posición espacial", ha="center", fontsize=10)
    eje.set_xlim(-1.6, 14.5)
    eje.set_ylim(6.8, -1.5)
    _guardar(figura, ruta)


def _figura_trafico(ruta: Path) -> None:
    bits = (1, 1, 1, 1, 0, 1, 0, 1, 0, 1)
    figura, eje = plt.subplots(figsize=(9.5, 2.4))
    eje.set_aspect("equal")
    eje.axis("off")
    for indice, bit in enumerate(bits):
        eje.add_patch(
            patches.Rectangle((indice, 0), 1, 0.72, fill=False, lw=1.0, ec=COLOR_OSCURO)
        )
        eje.text(indice + 0.5, 0.35, str(bit), ha="center", va="center", fontsize=12)
        if bit:
            eje.add_patch(
                patches.FancyBboxPatch(
                    (indice + 0.18, 0.93),
                    0.64,
                    0.28,
                    boxstyle="round,pad=0.02",
                    facecolor=COLOR_CLARO,
                    edgecolor=COLOR_OSCURO,
                )
            )
            eje.add_patch(patches.Circle((indice + 0.33, 0.91), 0.07, color=COLOR_OSCURO))
            eje.add_patch(patches.Circle((indice + 0.68, 0.91), 0.07, color=COLOR_OSCURO))
    eje.annotate(
        "sentido de avance",
        xy=(9.9, 1.55),
        xytext=(6.9, 1.55),
        arrowprops={"arrowstyle": "->", "lw": 1.4},
        va="center",
    )
    eje.set_xlim(-0.1, 10.2)
    eje.set_ylim(-0.1, 1.9)
    _guardar(figura, ruta)


def _figura_regla_local(
    ruta: Path, tabla: Iterable[Tuple[Tuple[int, int, int], int]], titulo: str
) -> None:
    figura, ejes = plt.subplots(2, 4, figsize=(10.2, 4.1))
    for eje, (vecindad, salida) in zip(ejes.flat, tabla):
        eje.set_aspect("equal")
        eje.axis("off")
        for indice, bit in enumerate(vecindad):
            eje.add_patch(
                patches.Rectangle(
                    (indice, 1.1),
                    0.9,
                    0.9,
                    facecolor=(COLOR_OSCURO if bit else "white"),
                    edgecolor=COLOR_OSCURO,
                    lw=1.1,
                )
            )
        eje.annotate("", xy=(1.35, 0.85), xytext=(1.35, 1.08), arrowprops={"arrowstyle": "->"})
        eje.add_patch(
            patches.Rectangle(
                (0.9, -0.08),
                0.9,
                0.9,
                facecolor=(COLOR_OSCURO if salida else "white"),
                edgecolor=COLOR_OSCURO,
                lw=1.1,
            )
        )
        eje.text(1.35, -0.35, f"{''.join(map(str, vecindad))} → {salida}", ha="center", fontsize=10)
        eje.set_xlim(-0.15, 2.95)
        eje.set_ylim(-0.5, 2.1)
    figura.suptitle(titulo, fontsize=13)
    figura.subplots_adjust(wspace=0.25, hspace=0.32, top=0.88)
    _guardar(figura, ruta)


def _figura_espaciotemporal(ruta: Path, matriz: np.ndarray, *, ejes: bool) -> None:
    figura, eje = plt.subplots(figsize=(7.0, 5.0 if ejes else 7.0))
    eje.imshow(matriz, cmap="binary", interpolation="nearest", aspect="auto", vmin=0, vmax=1)
    if ejes:
        eje.set_xlabel("Posición espacial")
        eje.set_ylabel("Tiempo")
    else:
        eje.axis("off")
    _guardar(figura, ruta)


def _figura_regla184_densidad(ruta: Path, densidad: float) -> None:
    inicial = condicion_inicial_densidad(
        CELDAS_R184, densidad, SEED + int(round(100 * densidad))
    )
    matriz = evolucion_regla_elemental(184, inicial, INSTANTES_R184)
    figura, eje = plt.subplots(figsize=(8.1, 3.4))
    eje.imshow(matriz, cmap="binary", interpolation="nearest", aspect="auto", vmin=0, vmax=1)
    eje.set_xlabel("Posición espacial")
    eje.set_ylabel("Tiempo")
    eje.set_title(f"Densidad inicial: {densidad:.0%}")
    _guardar(figura, ruta)


def _bifurcacion_logistica(ruta: Path) -> None:
    parametros = np.linspace(2.8, 4.0, 2400)
    valores = np.full(parametros.shape, 0.02024, dtype=float)
    for _ in range(900):
        valores = parametros * valores * (1.0 - valores)
    xs, ys = [], []
    for _ in range(100):
        valores = parametros * valores * (1.0 - valores)
        xs.append(parametros.copy())
        ys.append(valores.copy())
    figura, eje = plt.subplots(figsize=(8.5, 5.0))
    eje.plot(np.concatenate(xs), np.concatenate(ys), ",", color=COLOR_OSCURO, alpha=0.45)
    eje.set(xlim=(2.8, 4.0), ylim=(0.0, 1.0), xlabel=r"Parámetro $r$", ylabel=r"Estado asintótico $x$")
    eje.grid(alpha=0.18)
    _guardar(figura, ruta)


def _bifurcacion_tienda(ruta: Path) -> None:
    parametros = np.linspace(1.0, 2.0, 2400)
    valores = np.full(parametros.shape, 0.02024, dtype=float)
    for _ in range(900):
        valores = np.where(valores <= 0.5, parametros * valores, parametros * (1.0 - valores))
    xs, ys = [], []
    for _ in range(100):
        valores = np.where(valores <= 0.5, parametros * valores, parametros * (1.0 - valores))
        xs.append(parametros.copy())
        ys.append(valores.copy())
    figura, eje = plt.subplots(figsize=(8.5, 5.0))
    eje.plot(np.concatenate(xs), np.concatenate(ys), ",", color=COLOR_OSCURO, alpha=0.45)
    eje.set(xlim=(1.0, 2.0), ylim=(0.0, 1.0), xlabel=r"Parámetro $\mu$", ylabel=r"Estado asintótico $x$")
    eje.grid(alpha=0.18)
    _guardar(figura, ruta)


def _figura_histograma(ruta: Path, valores: np.ndarray, titulo: str, *, perfil=None) -> None:
    bordes = np.linspace(0.0, 1.0, 11)
    conteos, _ = np.histogram(valores, bins=bordes)
    anchos = np.diff(bordes)
    alturas = conteos / (valores.size * anchos)
    figura, eje = plt.subplots(figsize=(6.1, 4.3))
    eje.bar(
        bordes[:-1],
        alturas,
        width=anchos,
        align="edge",
        color=COLOR_CLARO,
        edgecolor=COLOR_OSCURO,
        linewidth=0.8,
        label="Densidad empírica",
    )
    eje.axhline(1.0, color=COLOR_ACENTO, ls="--", lw=1.4, label="Uniforme(0,1)")
    eje.set(xlim=(0.0, 1.0), xlabel="Valor", ylabel="Densidad empírica", title=titulo)
    if perfil is None:
        estilizar_eje(eje)
        leyenda_externa(eje, ncol=2)
    else:
        estilizar_eje(eje, perfil)
        leyenda_externa(eje, perfil, ncol=1)
    if perfil is None:
        _guardar(figura, ruta)
    else:
        guardar_figura(figura, ruta, software="regenerar_segunda_ronda.py")
        plt.close(figura)


def _figura_coleccionista(ruta: Path) -> None:
    bloques = (
        (0, 2, 0, 5, 1, 3, 4, 2, 6, 7, 8, 1, 9),
        (4, 4, 2, 0, 7, 3, 8, 5, 5, 1, 6, 2, 0, 9),
    )
    figura, eje = plt.subplots(figsize=(11.2, 3.2))
    eje.axis("off")
    for fila, bloque in enumerate(bloques):
        y = 1.6 - fila * 1.15
        for indice, digito in enumerate(bloque):
            color = COLOR_CLARO if indice < len(bloque) - 1 else "#f4d6b8"
            eje.add_patch(
                patches.Rectangle((indice, y), 0.78, 0.68, facecolor=color, edgecolor=COLOR_OSCURO, lw=0.8)
            )
            eje.text(indice + 0.39, y + 0.34, str(digito), ha="center", va="center", fontsize=11)
        eje.annotate(
            "último tipo faltante",
            xy=(len(bloque) - 0.61, y + 0.34),
            xytext=(len(bloque) + 0.15, y + 0.34),
            arrowprops={"arrowstyle": "->", "color": COLOR_ACENTO},
            color=COLOR_ACENTO,
            fontsize=9,
            va="center",
        )
        eje.text(-0.25, y + 0.34, rf"$n_{fila + 1}={len(bloque)}$", ha="right", va="center", fontsize=11)
    eje.set_xlim(-1.6, 16.2)
    eje.set_ylim(0.15, 2.65)
    _guardar(figura, ruta)


def _figura_brechas(ruta: Path) -> None:
    valores = np.asarray([0.12, 0.84, 0.41, 0.62, 0.55, 0.91, 0.33, 0.68])
    figura, (eje_valores, eje_tiempo) = plt.subplots(2, 1, figsize=(10.3, 4.4), gridspec_kw={"height_ratios": (1.4, 1.0)})
    eje_valores.axvspan(0.5, 0.7, color=COLOR_CLARO, label=r"intervalo $(0.5,0.7)$")
    exitos = (valores > 0.5) & (valores < 0.7)
    eje_valores.scatter(valores[~exitos], np.zeros((~exitos).sum()), marker="x", s=52, color=COLOR_MEDIO, label="fracaso")
    eje_valores.scatter(valores[exitos], np.zeros(exitos.sum()), marker="o", s=58, color=COLOR_ACENTO, label="éxito")
    for indice, valor in enumerate(valores, start=1):
        eje_valores.text(valor, 0.08 + 0.05 * (indice % 2), rf"$U_{indice}$", ha="center", fontsize=9)
    eje_valores.set(xlim=(0, 1), ylim=(-0.12, 0.32), yticks=[], xlabel="Valor observado")
    eje_valores.legend(ncol=3, loc="upper center", fontsize=9)
    estados = np.where(exitos, 1, 0)
    eje_tiempo.step(np.arange(1, 9), estados, where="mid", color=COLOR_OSCURO, lw=1.3)
    eje_tiempo.scatter(np.flatnonzero(exitos) + 1, np.ones(exitos.sum()), color=COLOR_ACENTO, zorder=3)
    eje_tiempo.set(xlim=(0.5, 8.5), ylim=(-0.15, 1.25), yticks=(0, 1), yticklabels=("fracaso", "éxito"), xlabel="Orden temporal")
    eje_tiempo.text(2.0, 0.48, r"$G_1=3$", ha="center")
    eje_tiempo.text(4.5, 0.48, r"$G_2=0$", ha="center")
    eje_tiempo.text(6.5, 0.48, r"$G_3=2$", ha="center")
    figura.tight_layout()
    _guardar(figura, ruta)


def _figura_mapeo_y_preimagenes(ruta: Path, *, tipo: str) -> None:
    x = np.linspace(0.0, 1.0, 800)
    if tipo == "logistico":
        y_curva = 4.0 * x * (1.0 - x)
        nivel = 0.56
        preimagenes = ((1.0 - np.sqrt(1.0 - nivel)) / 2.0, (1.0 + np.sqrt(1.0 - nivel)) / 2.0)
        etiqueta = r"$f(x)=4x(1-x)$"
    elif tipo == "tienda":
        y_curva = np.where(x <= 0.5, 2.0 * x, 2.0 * (1.0 - x))
        nivel = 0.56
        preimagenes = (nivel / 2.0, 1.0 - nivel / 2.0)
        etiqueta = r"$T_2(x)$"
    else:
        raise ValueError("tipo desconocido")
    figura, eje = plt.subplots(figsize=(5.1, 4.6))
    eje.plot(x, y_curva, color=COLOR_OSCURO, lw=1.8, label=etiqueta)
    eje.axhline(nivel, color=COLOR_MEDIO, ls="--", lw=1.0)
    for indice, preimagen in enumerate(preimagenes):
        eje.vlines(preimagen, 0.0, nivel, color=COLOR_ACENTO, ls=":" if indice else "--", lw=1.2)
        eje.scatter([preimagen], [nivel], color=COLOR_ACENTO, s=28, zorder=3)
        eje.text(preimagen, -0.08, rf"$x_{{{'-' if indice == 0 else '+'}}}(y)$", ha="center", fontsize=10)
    eje.text(0.02, nivel + 0.035, r"$y$", fontsize=10)
    eje.set(xlim=(0, 1), ylim=(-0.13, 1.04), xlabel=r"$x$", ylabel=r"$\phi(x)$")
    eje.legend(loc="upper left", fontsize=9)
    _guardar(figura, ruta)


def _figura_tienda(ruta: Path) -> None:
    x = np.linspace(0.0, 1.0, 600)
    y = np.where(x <= 0.5, 2.0 * x, 2.0 * (1.0 - x))
    figura, eje = plt.subplots(figsize=(4.8, 4.2))
    eje.plot(x, y, color=COLOR_OSCURO, lw=1.9)
    eje.axvline(0.5, color=COLOR_MEDIO, ls="--", lw=0.9)
    eje.set(xlim=(0, 1), ylim=(0, 1.04), xlabel=r"$x$", ylabel=r"$T_2(x)$")
    eje.grid(alpha=0.18)
    _guardar(figura, ruta)


def _figura_capitulo(ruta: Path, tipo: str) -> None:
    figura, eje = plt.subplots(figsize=(4.2, 4.2))
    eje.axis("off")
    if tipo == "introduccion":
        x = np.linspace(0, 1, 300)
        eje.plot(x, 4 * x * (1 - x), color=COLOR_SECUNDARIO, lw=4)
        eje.scatter([0.18, 0.59, 0.97], [0.59, 0.97, 0.12], color=COLOR_ACENTO, s=40)
    elif tipo == "marco":
        eje.plot([0, 0.5, 1], [0, 1, 0], color=COLOR_SECUNDARIO, lw=4)
        eje.plot([0, 1], [0, 1], color=COLOR_MEDIO, ls="--", lw=1.5)
    elif tipo == "resultados":
        barras = np.asarray([0.72, 0.93, 0.86, 1.04, 0.96, 0.81, 1.03, 0.91])
        eje.bar(np.arange(barras.size), barras, color=COLOR_CLARO, edgecolor=COLOR_OSCURO)
        eje.axhline(1.0, color=COLOR_ACENTO, ls="--", lw=2)
    elif tipo == "conclusiones":
        matriz = matriz_regla30_pedagogica()[:35]
        eje.imshow(matriz, cmap="binary", interpolation="nearest", aspect="auto")
    else:
        raise ValueError("tipo de capítulo desconocido")
    eje.set_xlim(0, 1 if tipo in ("introduccion", "marco") else eje.get_xlim()[1])
    _guardar(figura, ruta, transparente=True)


def regenerar_figuras_tesis(output_dir: Path) -> Dict[str, object]:
    """Regenera las 28 figuras nuevas o históricas integradas en el bloque 14."""

    output_dir = Path(output_dir)
    _figura_sistema_dinamico(output_dir / "conceptuales/sistema_dinamico.pdf")
    _figura_punto_fijo(output_dir / "conceptuales/punto_fijo_repulsor.pdf", atractor=False)
    _figura_punto_fijo(output_dir / "conceptuales/punto_fijo_atractor.pdf", atractor=True)
    _figura_periodo_cuatro(output_dir / "conceptuales/orbita_periodo_cuatro.pdf")
    _figura_malla(output_dir / "conceptuales/malla_automata.pdf")
    _figura_trafico(output_dir / "conceptuales/regla184_trafico.pdf")
    _figura_regla_local(
        output_dir / "conceptuales/regla184_local.png",
        tabla_regla_elemental(184),
        "Regla 184",
    )
    for densidad, sufijo in zip(DENSIDADES_R184, ("25", "50", "70")):
        _figura_regla184_densidad(
            output_dir / f"conceptuales/regla184_densidad_{sufijo}.png", densidad
        )
    _figura_regla_local(
        output_dir / "conceptuales/regla30_local.pdf", tabla_regla30(), "Regla 30"
    )
    _figura_espaciotemporal(
        output_dir / "conceptuales/regla30_espaciotemporal.png",
        matriz_regla30_pedagogica(),
        ejes=True,
    )
    _figura_coleccionista(output_dir / "conceptuales/coleccionista_bloques.png")
    _figura_brechas(output_dir / "conceptuales/prueba_brechas.png")
    _figura_mapeo_y_preimagenes(
        output_dir / "conceptuales/logistico_preimagenes.pdf", tipo="logistico"
    )
    _figura_tienda(output_dir / "conceptuales/tienda_mapeo.pdf")
    _figura_mapeo_y_preimagenes(
        output_dir / "conceptuales/tienda_preimagenes.pdf", tipo="tienda"
    )
    _bifurcacion_logistica(output_dir / "cientificas/logistico_bifurcacion.png")
    _bifurcacion_tienda(output_dir / "cientificas/tienda_bifurcacion.png")

    logistica = muestra_logistica()
    tienda = muestra_tienda()
    columnas, filas = muestras_regla_30()
    _figura_histograma(
        output_dir / "cientificas/logistico_histograma.png",
        logistica,
        "Mapeo logístico uniformizado",
    )
    _figura_histograma(
        output_dir / "cientificas/tienda_histograma.png",
        tienda,
        "Mapeo tienda, factor 1.999",
    )
    _figura_histograma(
        output_dir / "cientificas/r30_hist_columnas.png",
        columnas,
        "Regla 30 por columnas",
    )
    _figura_histograma(
        output_dir / "cientificas/r30_hist_filas.png",
        filas,
        "Regla 30 por filas",
    )
    rng = np.random.RandomState(SEED)
    matriz_canonica = evolucion_regla30(
        rng.binomial(size=NUM_CELDAS, n=1, p=0.5), NUM_ITERACIONES
    )
    _figura_espaciotemporal(
        output_dir / "cientificas/r30_matriz_1000.png",
        matriz_canonica,
        ejes=False,
    )
    for nombre, tipo in (
        ("capitulo_introduccion.png", "introduccion"),
        ("capitulo_marco_teorico.png", "marco"),
        ("capitulo_resultados.png", "resultados"),
        ("capitulo_conclusiones.png", "conclusiones"),
    ):
        _figura_capitulo(output_dir / "decorativas" / nombre, tipo)

    faltantes = [nombre for nombre in ARCHIVOS_GENERADOS if not (output_dir / nombre).is_file()]
    if faltantes:
        raise RuntimeError(f"faltan figuras generadas: {faltantes}")
    hashes = {
        nombre: _sha256(output_dir / nombre) for nombre in ARCHIVOS_GENERADOS
    }
    return {
        "archivos": list(ARCHIVOS_GENERADOS),
        "archivos_canonicos_activos": list(ARCHIVOS_CANONICOS_ACTIVOS),
        "sha256": hashes,
        "parametros": {
            "r30_pedagogico": {
                "celdas": CELDAS_R30_PEDAGOGICO,
                "instantes": INSTANTES_R30_PEDAGOGICO,
                "condicion_inicial": "una celda central activa",
            },
            "r30_canonico": {
                "celdas": NUM_CELDAS,
                "instantes": NUM_ITERACIONES,
                "semilla": SEED,
            },
            "r184": {
                "celdas": CELDAS_R184,
                "instantes": INSTANTES_R184,
                "densidades": list(DENSIDADES_R184),
                "semillas": [SEED + int(round(100 * d)) for d in DENSIDADES_R184],
            },
            "bifurcaciones": {
                "parametros": 2400,
                "transitorio": 900,
                "iteraciones_representadas": 100,
            },
            "histogramas": {"intervalos": 10, "n": 1000},
        },
    }


def copiar_archivos_generados(
    origen: Path, destino: Path, mapeo: Mapping[str, str]
) -> None:
    """Copia salidas aprobadas a rutas canónicas explícitas."""

    origen = Path(origen)
    destino = Path(destino)
    for nombre_origen, nombre_destino in mapeo.items():
        fuente = origen / nombre_origen
        objetivo = destino / nombre_destino
        if not fuente.is_file():
            raise FileNotFoundError(fuente)
        objetivo.parent.mkdir(parents=True, exist_ok=True)
        objetivo.write_bytes(fuente.read_bytes())
