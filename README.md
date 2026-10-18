# Control de oxígeno en biorreactores

| Simposio | Curso avanzado |
|:---:|:---:|
| [![XI Simposio Latinoamericano de Tecnología de Cultivos Celulares](docs/imagenes/Simposio_portada.png)](https://www.slatcc.com/) | [![Curso Avanzado de Tecnologías de Cultivo Celular 2026](docs/imagenes/Curso_portada.png)](https://www.slatcc.com/) |

Material educativo en español preparado para el **Simposio Latinoamericano de Tecnología de Cultivos Celulares (SLATCC)** y su actividad de formación en bioprocesos. Sitio del evento: **[www.slatcc.com](https://www.slatcc.com/)**.

El proyecto reúne una guía de taller, datos experimentales del **14 de octubre de 2026** y herramientas de análisis para comprender la dinámica del oxígeno disuelto y afinar un controlador PI en un Sartorius Biostat B. Está dirigido a personas de cultivo celular con distintos perfiles —biología, bioingeniería, genética y personal técnico—, sin requerir una formación matemática avanzada.

## La actividad

**Taller:** “Afinación del control de oxígeno disuelto en un biorreactor”. **Organización:** 3 equipos de 6 personas, de forma sucesiva, con **45 minutos como máximo por equipo**.

| Aspecto | Descripción |
|---|---|
| Trabajo del equipo | Aplicar un escalón de agitación de **200 a 500 rpm**, leer la curva y calcular un ajuste mediante Ziegler–Nichols, SIMC o ITAE. |
| Condiciones principales | Aire fijo a **0.5 vvm (2.5 L/min para 5 L de líquido)**; agitación como variable manipulada. |
| Resultado | Ajustes **Xp y TI**, con TD = 0, y observación de la respuesta a cambios de **setpoint**. |

La guía contiene fundamentos accesibles, roles, procedimiento, hoja de datos y un anexo del instructor que distingue lo observado en el piloto de lo calculado después.

## Materiales y documentación

| Recurso | Contenido |
|---|---|
| [Guía Markdown](practica/Practica_control_pO2.md) | Fuente editable de la práctica, fichas y notas del instructor |
| [Word](practica/Practica_control_pO2.docx) y [PDF](practica/Practica_control_pO2.pdf) | Versiones para edición, consulta e impresión |
| [Guía de reproducción y mantenimiento](docs/REPRODUCIBILIDAD.md) | Instalación, scripts, datos, interpretación y actualización de documentos |
| [Datos originales](fermentador%20B1%20levadura.xlsx) | Exportación del Biostat con los escalones del piloto |
| [Datos procesados](datos_limpios/) | Registros y ventanas de análisis en CSV |
| [Resultados](resultados/) | Parámetros y métricas calculados, con su contexto |
| [Figuras](figuras/) | Registro experimental, escalón de RPM y lectura de las curvas |

## Inicio rápido

Desde la raíz del repositorio, con Python 3 instalado:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python explorar_datos.py
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 1 --span 1000
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 2 --span 1000
```

Los scripts generan o actualizan archivos en `datos_limpios/`, `resultados/` y `figuras/`. La [guía de reproducción](docs/REPRODUCIBILIDAD.md) explica las entradas, decisiones del análisis y comprobaciones correspondientes a este taller.

## Actualizar Word y PDF

Se requieren **Pandoc** para generar Word y **LibreOffice** para exportar PDF desde la terminal:

```bash
python practica/generar_word.py
libreoffice --headless --convert-to pdf --outdir practica practica/Practica_control_pO2.docx
```

El generador sobrescribe el Word a partir del Markdown. Si se editó el Word directamente, incorporar primero esos cambios a la fuente. Revisar visualmente el PDF después de generarlo. Los logos de esta página se conservan en `docs/imagenes/`; el formato de los documentos de la práctica procede de `plantilla_documento.docx`.

## Alcance de los resultados

Los ajustes dependen del cultivo, la escala de oxígeno y los límites reales de la cascada. La comparación incluye tanto la lectura de la curva como la regla de ajuste; los cambios de setpoint no verifican por sí solos el rechazo de perturbaciones.

El anexo distingue los ajustes preliminares ensayados el 14 de octubre de 2026 de los valores recalculados posteriormente. El piloto usó 5 g/L de azúcar, mientras que la preparación propuesta para el taller usa 10 g/L.

Los scripts están preparados para el formato de exportación y los datos incluidos en este repositorio. Revisar las condiciones y adaptar el análisis antes de usar nuevos registros.

## Taller complementario

[Respuesta de sensores en bioprocesos](https://github.com/ebalderasr/respuesta-sensores-bioprocesos): Identificación de sondas de pH y O₂ y medición de su tiempo de respuesta. Ambos repositorios comparten organización y presentación para facilitar su uso conjunto.

## Autor

**Emiliano Balderas · Instituto de Biotecnología, UNAM**.
