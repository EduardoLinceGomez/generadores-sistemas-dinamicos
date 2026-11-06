# Alineación editorial de paneles de la tesis

Fecha: 2026-11-06. Base: `73f09efe4cf101d8557bc6cbeb13e94f978305af`
(`origin/main`, después de sincronizar referencias). Rama:
`codex/alinear-paneles-tesis`. No se modifica el modelo ni se fusiona la rama.

## Causa y solución

Las figuras 3.3, 3.4, 3.5, 3.11, 3.12, 3.18 y 3.19 combinan paneles que se
exportaban independientemente mediante `constrained_layout` y un recorte
`tight`. Diferencias de etiquetas, proporción de los ejes y número de filas en
las leyendas daban bordes de trazado distintos, aunque los lienzos nominales
pudieran tener el mismo tamaño. En LaTeX, además, las Figuras 3.5 y 3.11 usaban
anchos distintos dentro de la pareja.

`guardar_paneles_alineados` mide los ejes efectivos después del primer dibujo,
les asigna una altura común y sitúa las leyendas debajo de la decoración del eje
horizontal en una misma línea. Calcula la unión de los límites de los artistas
para exportar ambos paneles con un recorte idéntico y margen de seguridad. Así
se alinean las áreas de datos, no sólo los PNG.

Los límites de los ejes, escalas lineales/logarítmicas/symlog, datos, colores,
marcadores, títulos, etiquetas y tamaños de fuente se conservan. En el plano
complejo se mantiene `aspect='equal'`; su anchura puede diferir de la del panel
de error para conservar esa proporción y la altura común. La exportación incluye
metadatos PNG `AxesBounds` para comprobar después la alineación en el PDF.

## Fuentes

- `src/tesis_generacion/visualizacion/estilo.py`: exportador común de parejas.
- `src/tesis_generacion/visualizacion/momentos.py`: construcción de figuras sin
  exportar mediante `ruta=None` y composición pareada de comparación/error.
- `src/tesis_generacion/visualizacion/transformadas.py`: composición pareada de
  las tres FGM y de la función característica de regla 30.
- `scripts/regenerar_paneles_alineados.py`: genera exactamente los 14 paneles
  solicitados. Las funciones características de tienda y logístico quedan fuera.
- `figuras_tesis/cientificas/momentos/` y `transformadas/`: 14 PNG regenerados.
- `figuras_tesis/manifest_figuras.csv`: únicamente las 14 entradas afectadas,
  con hashes, comando y procedencia actualizados.
- `tests/test_paneles_alineados.py`: verifica las siete parejas, la invariancia
  de sus datos y escalas, y que títulos, etiquetas, ticks visibles y leyendas
  queden dentro del PNG.

Los comandos generales `regenerar_momentos.py` y `regenerar_transformadas.py`
utilizan también la nueva composición. El script de la segunda ronda anterior
se conserva como procedimiento histórico de esa revisión.

## Reproducción

```sh
cd '/Users/lince/.codex/worktrees/generadores-paneles'
PYTHONPATH=src python3 scripts/regenerar_paneles_alineados.py \
  --output-dir outputs/paneles_alineados
PYTHONPATH=src python3 scripts/verificar_figuras_tesis.py
PYTHONPATH=src python3 -m pytest -q \
  tests/test_paneles_alineados.py \
  tests/test_estadistica_momentos.py tests/test_estadistica_transformadas.py \
  tests/test_visualizacion_momentos.py tests/test_visualizacion_transformadas.py \
  tests/test_cli_momentos.py tests/test_cli_transformadas.py
```

## Evidencia científica e integración

Se ejecutaron ambos generadores generales antes y después del cambio en el mismo
entorno. Los resúmenes JSON (excluyendo rutas y hashes de imágenes) y los CSV
numéricos son idénticos. Los fingerprints de las muestras, parámetros, mallas,
métricas y estadísticas no cambian. Los datos y estilos de líneas/colecciones,
límites, escalas, aspecto, textos y tamaños de fuente permanecen iguales tras
aplicar el exportador pareado.

Las copias de los 14 PNG en la rama editorial de la tesis son idénticas byte a
byte a las canónicas. El manifiesto canónico de 65 entradas pasa sin errores.
La auditoría completa de integración con la tesis tiene diez discrepancias
previas en recursos ajenos a este cambio, reproducidas contra el manifiesto y
el manuscrito base; no se introduce ninguna nueva. No se sincronizaron esos
recursos fuera de alcance. Las verificaciones detalladas y las capturas están
en la rama `codex/alinear-figuras-agrupar-tablas` del repositorio de la tesis.

Resultado de las siete suites seleccionadas: **31 pruebas y 53 subpruebas
aprobadas**; dos pruebas de comparación estricta de PNG históricos permanecen
omitidas por su configuración explícita (`VERIFICAR_PNG_EXACTO`). La validación
actual de geometría, contenido y visibilidad de las siete parejas sí se ejecutó.
