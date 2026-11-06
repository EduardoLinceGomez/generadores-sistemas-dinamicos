#!/usr/bin/env python3
"""Regenera los 14 paneles de las siete parejas corregidas de la tesis."""
import argparse
from pathlib import Path

from tesis_generacion.experimentos import construir_muestras
from tesis_generacion.visualizacion import momentos as m, transformadas as t


def regenerar(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    muestras = construir_muestras()
    configuraciones = (
        ("logistico", "mapeo logístico", {"Logístico uniformizado": muestras["logistico"]}, m.ORDEN_MAXIMO_LOGISTICO),
        ("tienda", "mapeo tienda", {"Mapeo tienda": muestras["tienda"]}, m.ORDEN_MAXIMO_OTROS),
        ("r30", "regla 30", {"R30 columnas": muestras["r30_columnas"], "R30 filas": muestras["r30_filas"]}, m.ORDEN_MAXIMO_OTROS),
    )
    for nombre, titulo, series, orden in configuraciones:
        m.guardar_momentos_pareados(output_dir, nombre, series, orden, titulo)
        titulo_fgm = "mapeo logístico uniformizado" if nombre == "logistico" else titulo
        t.guardar_fgm_pareadas(output_dir, nombre, series, titulo_fgm)
        if nombre == "r30":
            t.guardar_fc_pareadas(output_dir, nombre, series, *t.TITULOS_FC[nombre])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/paneles_alineados"))
    regenerar(parser.parse_args().output_dir)
