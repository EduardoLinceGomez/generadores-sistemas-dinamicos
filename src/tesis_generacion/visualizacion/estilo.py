"""Criterios visuales compartidos para las gráficas usadas en la tesis."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from matplotlib.axes import Axes
from matplotlib.figure import Figure


@dataclass(frozen=True)
class PerfilTipografico:
    """Tamaños adaptados al ancho final de una figura en el PDF."""

    titulo: float
    ejes: float
    ticks: float
    leyenda: float
    anotacion: float
    separacion_leyenda: float


# Figuras que terminan a aproximadamente media página.
PERFIL_MEDIO = PerfilTipografico(22, 19, 16, 14, 14, -0.24)
# Perfiles de la segunda ronda: compensan la reducción a media página.
PERFIL_RESULTADOS = PerfilTipografico(24, 23, 19, 18, 18, -0.27)
PERFIL_BRECHAS = PerfilTipografico(27, 27, 22, 20, 22, -0.24)
# Figuras que se insertan al 80 % del ancho del texto.
PERFIL_ANCHO = PerfilTipografico(18, 16, 13, 12, 12, -0.20)
# Los dos histogramas de la Figura 2.13 se muestran lado a lado y requieren
# tipografía ligeramente mayor por la reducción final.
PERFIL_HISTOGRAMA_DOBLE = PerfilTipografico(26, 23, 19, 17, 16, -0.25)


def estilizar_eje(eje: Axes, perfil: PerfilTipografico = PERFIL_MEDIO) -> None:
    """Normaliza título, etiquetas y ticks sin alterar datos ni escalas."""

    eje.title.set_fontsize(perfil.titulo)
    eje.xaxis.label.set_fontsize(perfil.ejes)
    eje.yaxis.label.set_fontsize(perfil.ejes)
    eje.tick_params(axis="both", which="both", labelsize=perfil.ticks)
    eje.xaxis.get_offset_text().set_fontsize(perfil.ticks)
    eje.yaxis.get_offset_text().set_fontsize(perfil.ticks)


def leyenda_externa(
    eje: Axes,
    perfil: PerfilTipografico = PERFIL_MEDIO,
    *,
    ncol: int = 2,
) -> Optional[object]:
    """Sitúa una leyenda existente debajo del eje, cerca del xlabel."""

    manejadores, etiquetas = eje.get_legend_handles_labels()
    if not manejadores:
        return None
    leyenda = eje.legend(
        manejadores,
        etiquetas,
        loc="upper center",
        bbox_to_anchor=(0.5, perfil.separacion_leyenda),
        borderaxespad=0.0,
        fontsize=perfil.leyenda,
        ncol=ncol,
        columnspacing=1.1,
        handletextpad=0.55,
        labelspacing=0.45,
    )
    return leyenda


def guardar_figura(
    figura: Figure,
    ruta: Path,
    *,
    software: str,
    dpi: int = 200,
) -> None:
    """Guarda sin recortes y con un padding compacto y reproducible."""

    # Resolver el layout antes de medir; las leyendas externas no reducen
    # el área de datos. Su borde superior queda debajo del xlabel y los ticks.
    for eje in figura.axes:
        if eje.get_legend() is not None:
            eje.get_legend().set_in_layout(False)
    figura.canvas.draw()
    renderer = figura.canvas.get_renderer()
    extras = list(figura.texts) + list(figura.legends)
    for eje in figura.axes:
        extras.extend([eje.xaxis.label, eje.yaxis.label, eje.title])
        leyenda = eje.get_legend()
        if leyenda is not None:
            cajas = [texto.get_window_extent(renderer) for texto in
                     [eje.xaxis.label, *eje.get_xticklabels()]
                     if texto.get_visible() and texto.get_text()]
            inferior = min(caja.y0 for caja in cajas)
            centro = (eje.bbox.x0 + eje.bbox.x1) / 2
            punto = figura.transFigure.inverted().transform(
                (centro, inferior - 10 * figura.dpi / 72)
            )
            leyenda.set_bbox_to_anchor(punto, transform=figura.transFigure)
            extras.append(leyenda)
    # Evitar que savefig vuelva a redistribuir ejes tras medir los artistas.
    figura.set_layout_engine(None)
    figura.savefig(
        ruta,
        dpi=dpi,
        bbox_inches="tight",
        bbox_extra_artists=extras,
        pad_inches=0.08,
        metadata={"Software": software},
    )
