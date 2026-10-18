# Control de oxígeno en biorreactores

Material en español para comprender y ajustar el control de oxígeno disuelto en un biorreactor Sartorius Biostat B. Incluye una guía accesible para personas de cultivo celular con distintos perfiles, datos experimentales y herramientas de análisis.

La actividad está organizada para **3 equipos de 6 personas**, con **45 minutos como máximo por equipo**. Compara ajustes PI mediante Ziegler–Nichols, SIMC e ITAE. El aire permanece fijo a **0.5 vvm**; se modifica la agitación y se comprueba la respuesta a cambios de consigna.

- [Guía de la práctica](practica/Practica_control_pO2.md)
- [Documento Word](practica/Practica_control_pO2.docx) y [PDF](practica/Practica_control_pO2.pdf)
- [Datos originales](fermentador%20B1%20levadura.xlsx), [datos procesados](datos_limpios/) y [resultados](resultados/)
- [Figuras](figuras/)

## Reproducir el análisis

Se requiere Python 3 y, para generar Word, Pandoc instalado en el sistema.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python explorar_datos.py
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 1
python fopdt_sartorius.py "fermentador B1 levadura.xlsx" --hoja B1.20261014.2 --escalon 2
python practica/generar_word.py
```

La guía Markdown es la fuente del documento Word; `plantilla_documento.docx` aporta el formato del congreso. Los ajustes numéricos dependen de las condiciones del cultivo, de la escala de oxígeno y de los límites de la cascada del equipo. La nota final de la guía explica la conversión de ganancia a banda proporcional Xp.

Autor: Emiliano Balderas · Instituto de Biotecnología, UNAM.
