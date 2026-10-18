# Reproducción y mantenimiento del proyecto

| Simposio | Curso avanzado |
|:---:|:---:|
| [![XI Simposio Latinoamericano de Tecnología de Cultivos Celulares](imagenes/Simposio_portada.png)](https://www.slatcc.com/) | [![Curso Avanzado de Tecnologías de Cultivo Celular 2026](imagenes/Curso_portada.png)](https://www.slatcc.com/) |

Material educativo para el **SLATCC**: [www.slatcc.com](https://www.slatcc.com/). Esta guía describe cómo reproducir el análisis y mantener los materiales del taller **“Afinación del control de oxígeno disuelto en un biorreactor”**.

## Estructura

| Ruta | Función |
|---|---|
| `explorar_datos.py` | Lee el Excel y genera las figuras generales y del piloto |
| `fopdt_sartorius.py` | Detecta los escalones, estima modelos del proceso y calcula ajustes PI |
| `practica/Practica_control_pO2.md` | Fuente del texto y de las ecuaciones del taller |
| `practica/generar_word.py` | Convierte el Markdown con Pandoc y aplica formato con python-docx |
| `plantilla_documento.docx` | Tamaño de página, márgenes, encabezados, pie y elementos del formato del evento |
| `fermentador B1 levadura.xlsx` | Datos originales; conservar como entrada del análisis |
| `datos_limpios/` | Datos de cada escalón exportados por el análisis |
| `resultados/` | Resúmenes numéricos por escalón |
| `figuras/` | Imágenes que se consultan y se insertan en los documentos |
| `requirements.txt` | Dependencias de Python |

## Entorno

Se necesita Python 3 y las bibliotecas de `requirements.txt`: NumPy, pandas, SciPy, Matplotlib, openpyxl y python-docx. Para generar Word también se requiere el ejecutable `pandoc`; para exportar PDF desde la terminal, LibreOffice.

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Las dependencias no están fijadas a versiones específicas. El entorno permite reproducir el procedimiento, pero no garantiza archivos binarios idénticos entre versiones de bibliotecas, fuentes tipográficas o conversores.

## Datos y condiciones experimentales

El análisis principal utiliza la hoja **`B1.20261014.2`** del Excel del **14 de octubre de 2026**. Contiene dos escalones de 200 a 500 rpm en un mismo lote. La función `cargar` lee el encabezado, omite las dos filas siguientes de etiquetas/unidades y estandariza las columnas:

| Señal | Columna de entrada | Uso |
|---|---|---|
| Oxígeno disuelto | `pO2_1` → `pO2` | % de saturación |
| Agitación | `STIRR_1` → `STIR` | rpm |
| Temperatura | `TEMP_1` → `TEMP` | Contexto del proceso |
| pH | `pH_1` → `pH` | Contexto del proceso |
| Marca temporal | `PDatTime` | Tiempo real transcurrido en segundos, columna `t` |

El análisis usa las marcas de tiempo reales, ya que asumir intervalos exactamente iguales a 5 s introduce deriva. Las notas del piloto indican **5 g/L de azúcar**, mientras que la preparación propuesta para el taller usa **10 g/L**. Esa diferencia debe conservarse al interpretar los resultados.

El Excel no incluye campos de modo MAN/AUTO, setpoint ni valores de Xp/TI. Las observaciones sobre ajustes ensayados provienen de las notas de operación recogidas en el anexo; no deben inferirse únicamente de las gráficas.

## Ejecutar el análisis

```bash
python explorar_datos.py
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 1 --span 1000
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 2 --span 1000
```

`--escalon` selecciona el primer o segundo cambio detectado. `--span` es la diferencia entre el máximo y el mínimo de agitación configurados en la cascada: 1200 − 200 = 1000 rpm en el recálculo documentado. Cambiarlo no modifica los límites del reactor: solo modifica el cálculo.

El detector busca transiciones de **200 a 500 rpm**. Para otros escalones hay que adaptar el código y revisar también los textos, figuras y constantes asociadas. `explorar_datos.py` usa un nombre de archivo y una hoja principal definidos en el script.

El análisis recorta una ventana alrededor de cada escalón, estima los valores inicial y final y aplica un filtro Savitzky–Golay para ayudar a leer la dinámica. Usa una aproximación de primer orden con tiempo muerto (FOPDT), con ganancia del proceso, constante de tiempo y tiempo muerto. Las curvas deben representar una respuesta ascendente, suficientemente completa y con parámetros positivos; revisar visualmente esos supuestos antes de interpretar los resultados.

## Interpretar los resultados

### Salidas

Cada ejecución de `fopdt_sartorius.py` escribe archivos con la hoja y el número de escalón en el nombre; repetirla sobrescribe sus salidas.

- **CSV:** `t`, `t_rel`, `pO2`, `pO2_filtrada`, `STIR`, `TEMP` y `pH`. `t_rel` coloca el escalón en cero.
- **JSON:** valores inicial y final, cambio de salida, Span, tiempos característicos y ajustes PI.
- **PNG:** señal cruda y filtrada, comparación de modelos y lectura de la curva para los métodos.

En el JSON, **`por_metodo`** contiene los ajustes usados como referencia para los equipos: Ziegler–Nichols con tangente, SIMC con inicio visible y 63.2 %, e ITAE con dos puntos de Smith. **`modelos`** calcula las reglas sobre modelos de Smith y mínimos cuadrados para comparación adicional. No intercambiar ambos bloques al actualizar la tabla del instructor.

Las reglas producen `Kc_norm`; la pantalla del reactor recibe **Xp = 100 / Kc_norm**, TI en segundos y TD = 0. Esta conversión supone las escalas y la cascada descritas en la guía. Los valores recalculados no equivalen a una validación experimental de los tres métodos.

### Figuras disponibles

| Prefijo | Contenido |
|---|---|
| `00`–`03` | Resumen de hojas, registro principal, escalones alineados y temperatura/pH |
| `04` | Dibujo del escalón ordenado de 200 a 500 rpm; es ilustrativo |
| `05` | Mediciones de oxígeno y agitación durante el registro del piloto |
| `06` | Ambos escalones del piloto alineados, con oxígeno y RPM |
| `10` | Señal cruda y filtrada, con agitación |
| `11` | Ajuste FOPDT por Smith y mínimos cuadrados |
| `12` | Lectura para cada método; la versión vertical incluye el panel de RPM |

## Actualizar la guía, Word y PDF

1. Modificar `practica/Practica_control_pO2.md`. Si hay cambios hechos directamente en Word, compararlos e incorporarlos al Markdown antes de regenerar.
2. Si cambiaron datos o figuras, ejecutar primero los scripts de análisis. Revisar que las tablas y ejemplos sigan coincidiendo con los JSON.
3. Generar Word:

   ```bash
   python practica/generar_word.py
   ```

4. Exportar a PDF con LibreOffice, o desde la aplicación de escritorio:

   ```bash
   libreoffice --headless --convert-to pdf --outdir practica practica/Practica_control_pO2.docx
   ```

5. Revisar visualmente el PDF: título, ecuaciones, tablas, saltos de página, leyendas y legibilidad de las gráficas. Confirmar que el aire siga fijo a 0.5 vvm y que las instrucciones usen «setpoint».

La alineación y el tamaño de imágenes pertenecen al generador de Word: el Markdown conserva el contenido, pero no representa toda la presentación. La plantilla aporta los elementos gráficos del evento. El nombre del autor está definido también en `generar_word.py`; si cambia, actualizar ambas fuentes.

## Criterios para mantener el material

Conservar separados los datos originales, los resultados calculados y las observaciones de operación. Registrar cualquier cambio de cultivo, azúcar, escala de oxígeno o límites de agitación. Mantener explícita la diferencia entre los ajustes preliminares ensayados el 14 de octubre y los valores recalculados posteriormente.

El entorno virtual, las configuraciones locales, los respaldos locales y los archivos temporales de edición se excluyen mediante `.gitignore`. Para cambios solo de documentación basta revisar enlaces, comandos y coherencia con el código; no es necesario regenerar los datos ni sobrescribir los documentos editados.

## Identidad visual y materiales relacionados

Los archivos `docs/imagenes/Simposio_portada.png` y `docs/imagenes/Curso_portada.png` son copias de las portadas proporcionadas para el simposio y el curso. Se conservan con sus nombres y sin modificaciones. Son recursos de documentación, separados de las figuras generadas por el análisis. El README y esta guía usan rutas relativas para que los logos se vean tanto en GitHub como en una copia local.

La presentación de Word y PDF se obtiene de `plantilla_documento.docx`. Para cambios solo de documentación no es necesario regenerar datos ni sobrescribir documentos editados. Si se actualizan los logos de la serie, sustituir las copias en ambos repositorios para mantener la misma identidad visual.

Taller complementario: [Respuesta de sensores en bioprocesos](https://github.com/ebalderasr/respuesta-sensores-bioprocesos). Ambos repositorios usan la misma estructura de README y guía de reproducción, con instrucciones específicas para sus datos.
