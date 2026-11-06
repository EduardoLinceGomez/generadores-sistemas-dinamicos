"""Regresión geométrica y científica de las siete parejas editoriales."""
import json
import tempfile
import unittest
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from tesis_generacion.experimentos import construir_muestras
from tesis_generacion.visualizacion import momentos as m, transformadas as t
from tesis_generacion.visualizacion.estilo import guardar_paneles_alineados


def contenido(eje):
    """Datos y semántica independientes del tamaño final de cada panel."""
    return {
        "lineas": [(line.get_xdata().tolist(), line.get_ydata().tolist(),
                    line.get_color(), line.get_marker(), line.get_linestyle()) for line in eje.lines],
        "colecciones": [(obj.get_offsets().tolist(), obj.get_sizes().tolist()) for obj in eje.collections],
        "limites": (eje.get_xlim(), eje.get_ylim()),
        "escalas": (eje.get_xscale(), eje.get_yscale(), eje.get_aspect()),
        "textos": [(txt.get_text(), txt.get_fontsize()) for txt in
                   [eje.title, eje.xaxis.label, eje.yaxis.label, *eje.get_legend().get_texts()]],
    }


class PanelesAlineadosTest(unittest.TestCase):
    def test_siete_parejas_alinean_datos_sin_cambiar_contenido_ni_recortar(self):
        muestras = construir_muestras()
        for nombre, series, orden in [
            ("logistico", {"Logístico uniformizado": muestras["logistico"]}, 40),
            ("tienda", {"Mapeo tienda": muestras["tienda"]}, 20),
            ("r30", {"R30 columnas": muestras["r30_columnas"], "R30 filas": muestras["r30_filas"]}, 20),
        ]:
            parejas = [
                (m.guardar_comparacion_momentos(None, series, orden, "Momentos ordinarios: " + nombre),
                 m.guardar_error_momentos(None, series, orden, "Error de momentos: " + nombre)),
                (t.guardar_fgm(None, series, "FGM empírica: " + nombre),
                 t.guardar_error_fgm(None, series, "Error de la FGM: " + nombre)),
            ]
            if nombre == "r30":
                parejas.append((t.guardar_funcion_caracteristica(None, series, t.TITULOS_FC[nombre][0]),
                                t.guardar_error_funcion_caracteristica(None, series, t.TITULOS_FC[nombre][1])))
            for indice, figuras in enumerate(parejas):
                with self.subTest(muestra=nombre, pareja=indice), tempfile.TemporaryDirectory() as directorio:
                    for fig in figuras:
                        fig.canvas.draw()
                    antes = [contenido(fig.axes[0]) for fig in figuras]
                    rutas = tuple(Path(directorio) / f'{i}.png' for i in range(2))
                    guardar_paneles_alineados(figuras, rutas, software="test")
                    self.assertEqual(antes, [contenido(fig.axes[0]) for fig in figuras])
                    with Image.open(rutas[0]) as a, Image.open(rutas[1]) as b:
                        self.assertEqual(a.size, b.size)
                        cajas = [json.loads(im.info['AxesBounds']) for im in [a,b]]
                        np.testing.assert_allclose(np.array(cajas[0])[[1,3]], np.array(cajas[1])[[1,3]], atol=1e-6)
                        # Comprobar todos los textos visibles, no sólo los bordes del eje.
                        for fig, caja in zip(figuras,cajas):
                            fig.canvas.draw()
                            eje=fig.axes[0];renderer=fig.canvas.get_renderer()
                            xt=[txt for value,txt in zip(eje.get_xticks(),eje.get_xticklabels()) if eje.get_xlim()[0]<=value<=eje.get_xlim()[1]]
                            yt=[txt for value,txt in zip(eje.get_yticks(),eje.get_yticklabels()) if eje.get_ylim()[0]<=value<=eje.get_ylim()[1]]
                            dx=caja[0]-eje.bbox.x0;dy=caja[3]+eje.bbox.y0
                            textos=[eje.title,eje.xaxis.label,eje.yaxis.label,
                                    eje.xaxis.get_offset_text(),eje.yaxis.get_offset_text(),
                                    *xt,*yt,*eje.get_legend().get_texts()]
                            for texto in textos:
                                if texto.get_visible() and texto.get_text():
                                    rect=texto.get_window_extent(renderer)
                                    self.assertGreaterEqual(rect.x0+dx,0)
                                    self.assertLessEqual(rect.x1+dx,a.width+1)
                                    self.assertGreaterEqual(dy-rect.y1,0)
                                    self.assertLessEqual(dy-rect.y0,a.height+1)
                    for fig in figuras:
                        plt.close(fig)


if __name__ == '__main__':
    unittest.main()
