# Control de oxígeno en biorreactores

Material educativo en español preparado para el **Simposio Latinoamericano de Tecnología de Cultivos Celulares (SLATCC)** y su actividad de formación en control de biorreactores. Sitio del evento: **[www.slatcc.com](https://www.slatcc.com/)**.

El proyecto reúne una guía de taller, datos experimentales de un Sartorius Biostat B y scripts para analizar la respuesta del oxígeno disuelto y calcular ajustes de un controlador PI. Está dirigido a personas de cultivo celular con distintos perfiles: biología, bioingeniería, genética y personal técnico, sin requerir una formación matemática avanzada.

## La actividad

El taller **“Afinación del control de oxígeno disuelto en un biorreactor”** está organizado para **3 equipos de 6 personas**, con **45 minutos como máximo por equipo**. Cada equipo mide la respuesta del oxígeno a un cambio de agitación de **200 a 500 rpm**, calcula un ajuste mediante Ziegler–Nichols, SIMC o ITAE y observa su respuesta a cambios de **setpoint**.

El aire permanece fijo a **0.5 vvm (2.5 L/min para 5 L de líquido)**. La guía explica los fundamentos del PID, la lectura de las curvas y la conversión de ganancia a los campos **Xp, TI y TD** de Biostat. El anexo del instructor distingue los resultados calculados de los ajustes realmente ensayados el 14 de octubre de 2026.

## Materiales y documentación

| Recurso | Contenido |
|---|---|
| [Guía Markdown](practica/Practica_control_pO2.md) | Fuente editable de la práctica y notas del instructor |
| [Word](practica/Practica_control_pO2.docx) y [PDF](practica/Practica_control_pO2.pdf) | Versiones para edición, consulta e impresión |
| [Guía de reproducción y mantenimiento](docs/REPRODUCIBILIDAD.md) | Instalación, scripts, datos, interpretación y actualización de documentos |
| [Datos originales](fermentador%20B1%20levadura.xlsx) | Exportación del piloto del 14 de octubre de 2026 |
| [Datos procesados](datos_limpios/) | Ventanas de los escalones en CSV |
| [Resultados](resultados/) | Parámetros del proceso y ajustes PI en JSON |
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

Para regenerar Word se necesita además **Pandoc** instalado en el sistema:

```bash
python practica/generar_word.py
```

Este comando sobrescribe el Word a partir del Markdown. Si se editó el Word directamente, primero incorporar esos cambios a la fuente. La exportación del PDF es un paso separado, descrito en la [guía de mantenimiento](docs/REPRODUCIBILIDAD.md#actualizar-la-guía-word-y-pdf).

## Alcance de los resultados

Los scripts están preparados para el formato de exportación y los escalones incluidos en este repositorio. Los ajustes dependen del cultivo, la escala de oxígeno y los límites reales de la cascada. La comparación del taller incluye tanto la lectura de la curva como la regla de ajuste; los cambios de setpoint no verifican por sí solos el rechazo de perturbaciones.

Autor: **Emiliano Balderas · Instituto de Biotecnología, UNAM**.
