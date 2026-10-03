# Segunda ronda editorial de figuras

## Estado y alcance

- Fecha: 2026-10-03.
- Rama: `codex/segunda-ronda-figuras`; base `283a7680761cacecfe075429f552d39bd88b138d`.
- Estado: implementado; 31 paneles de 18 figuras regenerados e incorporados a las copias canónicas y al manuscrito.
- Cambios exclusivos de presentación: tipografía, matemáticas en etiquetas, títulos, márgenes y leyendas.
- Datos, semillas, orden máximo de momentos, mallas, límites, escalas y trazas numéricas conservados. No hay cambios en estadística, generadores ni experimentos.
- Referencias visuales: Figuras 3.2 y 3.17, preservadas.

## Generación selectiva

Desde la raíz del repositorio:

```bash
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-segunda-ronda PYTHONDONTWRITEBYTECODE=1 \
  python3 scripts/regenerar_segunda_ronda.py --output-dir outputs/segunda_ronda
```

El selector llama a las funciones existentes con sus muestras, mallas y parámetros canónicos. Produce únicamente los 31 PNG solicitados. No promueve imágenes automáticamente: después de la revisión, se copiaron a las rutas `archivo_canonico` del manifiesto y a las rutas `archivo_tesis`. Se actualizaron exclusivamente los 31 SHA y comandos correspondientes del manifiesto. Los scripts generales anteriores siguen disponibles.

Las fuentes de la tabla están bajo `src/tesis_generacion/visualizacion/`. El punto de entrada selectivo es `scripts/regenerar_segunda_ronda.py`.

## Decisiones editoriales

- `PERFIL_RESULTADOS`: título 24, ejes 23, ticks 19, leyendas 18 pt; adaptación a figuras reducidas a media página.
- `PERFIL_BRECHAS`: título y ejes 27, ticks 22, leyendas 20 y títulos de panel 22 pt. El título general usa el mismo tamaño que los ejes.
- La referencia visual prevalece sobre la igualdad de tamaños nominales: Figuras 3.2 y 3.17 tienen lienzos e inclusiones diferentes.
- `estilo.guardar_figura`: resolver el layout, incluir explícitamente etiquetas, títulos y leyendas en `bbox_extra_artists`, exportar con `bbox_inches="tight"` y `pad_inches=0.08`, y congelar el layout antes de guardar.
- Leyendas externas de ejes: medir xlabel/ticks y situar el borde superior de la leyenda 10 pt por debajo. Excluir la leyenda del cálculo inicial evita reducir innecesariamente el área útil.
- Brechas: título general en dos líneas, leyenda de dos columnas, márgenes izquierdo/inferior 0.19/0.13, límite superior 0.73 y separación de paneles 0.52.
- Todas las etiquetas verticales permanecen en una línea. Se compararon versiones en una y dos líneas con el recorte resuelto y se conservó la primera por su margen izquierdo más compacto. El problema estaba en los PNG, no en una opción de recorte de LaTeX.
- Momentos: `Momento ordinario $m_k$` y `Orden $k$` con MathText.
- Títulos de evolución: «Evolución de distribuciones: mapeo tienda» y «Evolución de distribuciones: mapeo logístico»; los parámetros siguen en los captions.

## Correspondencia y revisión final

| Figura | Fuente y función | Archivo producido → archivo de la tesis | Página final | Revisión visual |
|---|---|---|---|---|
| 3.3 | `momentos.py`: guardar_comparacion_momentos / guardar_error_momentos | `r30_momentos.png` → `recursos/graficas/R30/Uniformidad/momentos_r30.png`<br>`r30_error_momentos.png` → `recursos/graficas/R30/Uniformidad/ErrorMomentos_r30.png` | 78 (PDF 88) | Ejes y leyendas legibles; notación matemática correcta. |
| 3.4 | `transformadas.py`: guardar_fgm / guardar_error_fgm | `r30_fgm.png` → `recursos/graficas/R30/Uniformidad/FGM_r30.png`<br>`r30_error_fgm.png` → `recursos/graficas/R30/Uniformidad/ErrorFGM_r30.png` | 79 (PDF 89) | Etiquetas completas; ejes y leyendas legibles. |
| 3.5 | `transformadas.py`: guardar_funcion_caracteristica / guardar_error_funcion_caracteristica | `r30_fc.png` → `recursos/graficas/R30/Uniformidad/R30_FC.png`<br>`r30_error_fc.png` → `recursos/graficas/R30/Uniformidad/R30_FCError.png` | 80 (PDF 90) | Ejes y leyendas legibles; sin colisiones. |
| 3.6 | `coleccionista.py`: guardar_cdf / guardar_pmf (regenerar_muestra) | `R30_col_distCCT.png` → `recursos/graficas/R30/Independencia/R30_col_distCCT.png`<br>`R30_col_densCCT.png` → `recursos/graficas/R30/Independencia/R30_col_densCCT.png` | 81 (PDF 91) | Ambas etiquetas verticales completas en una línea. |
| 3.7 | `coleccionista.py`: guardar_cdf / guardar_pmf (regenerar_muestra) | `R30_fila_distCCT.png` → `recursos/graficas/R30/Independencia/R30_fila_distCCT.png`<br>`R30_fila_densCCT.png` → `recursos/graficas/R30/Independencia/R30_fila_densCCT.png` | 82 (PDF 92) | Ambas etiquetas verticales completas en una línea. |
| 3.8 | `reordenamiento.py`: guardar_brechas_antes_despues | `R30_col_PG.png` → `recursos/graficas/R30/Independencia/R30_col_PG.png`<br>`R30_fila_PG.png` → `recursos/graficas/R30/Independencia/R30_fila_PG.png` | 83 (PDF 93) | Título y ejes de igual tamaño; tres paneles y leyenda sin colisiones. |
| 3.9 | `invariancia.py`: guardar_evolucion_cdf | `TentConv_Iteraciones.png` → `recursos/graficas/Tent/Convergencia/TentConv_Iteraciones.png` | 85 (PDF 95) | Título breve sin parámetros; etiqueta completa. |
| 3.10 | `figuras_tesis.py`: _figura_histograma | `tienda_histograma.png` → `recursos/graficas/Tent/Uniformidad/Tent_histograma.png` | 86 (PDF 96) | Ejes y leyenda legibles. |
| 3.11 | `momentos.py`: guardar_comparacion_momentos / guardar_error_momentos | `tienda_momentos.png` → `recursos/graficas/Tent/Uniformidad/Tent_Momentos.png`<br>`tienda_error_momentos.png` → `recursos/graficas/Tent/Uniformidad/Tent_MomentosError.png` | 86 (PDF 96) | m_k y k matemáticos; ejes y leyendas legibles. |
| 3.12 | `transformadas.py`: guardar_fgm / guardar_error_fgm | `tienda_fgm.png` → `recursos/graficas/Tent/Uniformidad/Tent_FGM.png`<br>`tienda_error_fgm.png` → `recursos/graficas/Tent/Uniformidad/Tent_ErrorFGM.png` | 87 (PDF 97) | Etiquetas verticales completas en una línea. |
| 3.13 | `transformadas.py`: guardar_funcion_caracteristica / guardar_error_funcion_caracteristica | `tienda_fc.png` → `recursos/graficas/Tent/Uniformidad/Tent_FC.png`<br>`tienda_error_fc.png` → `recursos/graficas/Tent/Uniformidad/Tent_FCError.png` | 88 (PDF 98) | Ejes y leyendas legibles; aspecto de la trayectoria conservado. |
| 3.14 | `coleccionista.py`: guardar_cdf / guardar_pmf (regenerar_muestra) | `Tent_dsit_CCT.png` → `recursos/graficas/Tent/Independencia/Tent_dsit_CCT.png`<br>`Tent_dens_CCT.png` → `recursos/graficas/Tent/Independencia/Tent_dens_CCT.png` | 89 (PDF 99) | Ambas etiquetas verticales completas en una línea. |
| 3.15 | `reordenamiento.py`: guardar_brechas_antes_despues | `Tent_PG.png` → `recursos/graficas/Tent/Independencia/Tent_PG.png` | 89 (PDF 99) | Título y ejes de igual tamaño; paneles y leyenda sin colisiones. |
| 3.16 | `invariancia.py`: guardar_evolucion_cdf | `LogConv_Iteraciones.png` → `recursos/graficas/Logist/Convergencia/LogConv_Iteraciones.png` | 91 (PDF 101) | Título breve sin parámetros; etiqueta completa. |
| 3.18 | `momentos.py`: guardar_comparacion_momentos / guardar_error_momentos | `logistico_momentos.png` → `recursos/graficas/Logist/Uniformidad/Log_Momentos.png`<br>`logistico_error_momentos.png` → `recursos/graficas/Logist/Uniformidad/Log_MomentosError.png` | 92 (PDF 102) | m_k y k matemáticos; ejes y leyendas legibles. |
| 3.19 | `transformadas.py`: guardar_fgm / guardar_error_fgm | `logistico_fgm.png` → `recursos/graficas/Logist/Uniformidad/Log_FGM.png`<br>`logistico_error_fgm.png` → `recursos/graficas/Logist/Uniformidad/Log_ErrorFGM.png` | 93 (PDF 103) | Etiquetas verticales completas en una línea. |
| 3.21 | `coleccionista.py`: guardar_cdf / guardar_pmf (regenerar_muestra) | `log_dist_CCT.png` → `recursos/graficas/Logist/Independencia/log_dist_CCT.png`<br>`Log_dens_CCT.png` → `recursos/graficas/Logist/Independencia/Log_dens_CCT.png` | 95 (PDF 105) | Ambas etiquetas verticales completas en una línea. |
| 3.22 | `reordenamiento.py`: guardar_brechas_antes_despues | `Log_PG.png` → `recursos/graficas/Logist/Independencia/Log_PG.png` | 95 (PDF 105) | Título y ejes de igual tamaño; paneles y leyenda sin colisiones. |

## Validación

```bash
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-segunda-ronda PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-segunda-ronda \
  python3 scripts/verificar_figuras_tesis.py --tesis-root '../Tesis UNAM'
git diff --check
```

- 165 pruebas: 159 aprobadas y 6 omisiones previstas de comprobaciones gráficas estrictas históricas.
- Comparación antes/después de los 31 paneles: arrays de líneas, colecciones y barras, límites y escalas idénticos. Las semillas y los módulos científicos no se modificaron.
- Márgenes positivos de contenido en los 31 PNG; ninguna etiqueta toca el borde de exportación.
- Regeneración final: 31/31 PNG idénticos byte a byte a las copias canónicas y a las incorporadas a la tesis.
- Manifiesto canónico: 65 entradas válidas, sin errores.
- Integración global con la tesis: 10 discrepancias fuera de esta ronda, idénticas al contrastar ambos repositorios en sus bases originales. Tres PDF históricos difieren de la copia canónica (`log_proof.pdf`, `tent.pdf`, `tent_proof.pdf`); cinco PDF incorporados al manuscrito no aparecen en el manifiesto (tres diagramas de invariancia y las dos bifurcaciones PDF); las dos bifurcaciones PNG declaradas ya no son usadas por LaTeX. No hay discrepancias en los 31 archivos de esta ronda.
- Tesis: compilación completa sin errores ni referencias indefinidas; revisión de las 18 figuras en el PDF, con captions y numeración intactos.
- No se modifica ningún baseline científico ni se reescriben imágenes manualmente.
