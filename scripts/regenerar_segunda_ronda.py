#!/usr/bin/env python3
"""Regenera exclusivamente los 31 paneles de la segunda revisión editorial.

Reutiliza muestras, mallas y funciones de trazado del pipeline canónico.
"""
import argparse
from pathlib import Path

from tesis_generacion.visualizacion.estilo import PERFIL_BRECHAS, PERFIL_RESULTADOS
from tesis_generacion.experimentos import construir_muestras
from tesis_generacion.experimentos.reordenamiento import construir_experimentos_reordenamiento
from tesis_generacion.experimentos.parametros import INTERVALOS_BRECHAS_COMUNES
from tesis_generacion.experimentos.invariancia import construir_experimentos_invariancia
from tesis_generacion.estadistica.invariancia import cdf_beta_medio, cdf_uniforme_01
from tesis_generacion.visualizacion import momentos as m, transformadas as t
from tesis_generacion.visualizacion import coleccionista as c, reordenamiento as r
from tesis_generacion.visualizacion import invariancia as i, figuras_tesis as f


def regenerar(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    muestras = construir_muestras()
    configuraciones = (
        ("logistico", "mapeo logístico", {"Logístico uniformizado": muestras["logistico"]}, m.ORDEN_MAXIMO_LOGISTICO),
        ("tienda", "mapeo tienda", {"Mapeo tienda": muestras["tienda"]}, m.ORDEN_MAXIMO_OTROS),
        ("r30", "regla 30", {"R30 columnas": muestras["r30_columnas"], "R30 filas": muestras["r30_filas"]}, m.ORDEN_MAXIMO_OTROS),
    )
    for nombre, titulo, series, orden in configuraciones:
        m.guardar_comparacion_momentos(output_dir / f"{nombre}_momentos.png", series, orden, f"Momentos ordinarios: {titulo}")
        m.guardar_error_momentos(output_dir / f"{nombre}_error_momentos.png", series, orden, f"Error de momentos: {titulo}")
        titulo_fgm = "mapeo logístico uniformizado" if nombre == "logistico" else titulo
        t.guardar_fgm(output_dir / f"{nombre}_fgm.png", series, f"FGM empírica: {titulo_fgm}")
        t.guardar_error_fgm(output_dir / f"{nombre}_error_fgm.png", series, f"Error de la FGM: {titulo_fgm}")
        if nombre != "logistico":  # La Figura 3.20 no pertenece a esta ronda.
            titulo_fc, titulo_error = t.TITULOS_FC[nombre]
            t.guardar_funcion_caracteristica(output_dir / f"{nombre}_fc.png", series, titulo_fc, figsize=t.FIGSIZE_FC_PAREADA if nombre == "tienda" else (6.4, 5.2))
            t.guardar_error_funcion_caracteristica(output_dir / f"{nombre}_error_fc.png", series, titulo_error, figsize=t.FIGSIZE_FC_PAREADA if nombre == "tienda" else (7.2, 4.5))
    c.regenerar(output_dir)
    experimentos = construir_experimentos_reordenamiento()
    for nombre, datos in experimentos["muestras"].items():
        r.guardar_brechas_antes_despues(output_dir / r.ARCHIVOS_TESIS_REORDENAMIENTO[nombre], datos["original"], datos["reordenada"], INTERVALOS_BRECHAS_COMUNES, r.ETIQUETAS_MUESTRAS[nombre], perfil=PERFIL_BRECHAS)
    evolucion = construir_experimentos_invariancia()
    i.guardar_evolucion_cdf(output_dir / "LogConv_Iteraciones.png", evolucion["logistico_r4"], cdf_beta_medio, "Evolución de distribuciones: mapeo logístico", "Beta(1/2,1/2) teórica")
    i.guardar_evolucion_cdf(output_dir / "TentConv_Iteraciones.png", evolucion["tienda_ideal_2"], cdf_uniforme_01, "Evolución de distribuciones: mapeo tienda", "Uniforme(0,1) teórica")
    f._figura_histograma(output_dir / "tienda_histograma.png", muestras["tienda"], "Mapeo tienda, factor 1.999", perfil=PERFIL_RESULTADOS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/segunda_ronda"))
    regenerar(parser.parse_args().output_dir)
